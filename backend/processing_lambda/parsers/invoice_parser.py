"""
parsers/invoice_parser.py (processing_lambda)

Textract JSON → structured Invoice domain model.

This is the most complex module in the pipeline. It parses the raw
flat list of Textract Block objects into meaningful invoice fields
using the following strategies:

1. KEY_VALUE_SET blocks  →  key/value pairs (vendor, date, total, etc.)
2. TABLE / CELL blocks   →  line items (description, qty, price, amount)
3. LINE blocks           →  fallback text extraction for unmatched fields

Textract block reference:
  https://docs.aws.amazon.com/textract/latest/dg/API_Block.html
"""

from __future__ import annotations

import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from processing_lambda.exceptions.custom_exceptions import InvoiceParsingException
from processing_lambda.models.invoice import Invoice, LineItem
from processing_lambda.utils.logger import get_logger

logger: logging.Logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Field keyword maps — maps Textract extracted keys to our field names.
# Keys are lowercase for case-insensitive matching.
# ---------------------------------------------------------------------------

_VENDOR_KEYS: frozenset[str] = frozenset(
    {"vendor", "vendor name", "seller", "company", "billed by", "from", "bill from"}
)
_INVOICE_NUMBER_KEYS: frozenset[str] = frozenset(
    {"invoice #", "invoice no", "invoice number", "inv #", "inv no", "number"}
)
_INVOICE_DATE_KEYS: frozenset[str] = frozenset(
    {"invoice date", "date", "date of issue", "issue date", "billing date"}
)
_DUE_DATE_KEYS: frozenset[str] = frozenset(
    {"due date", "payment due", "pay by", "due by"}
)
_TOTAL_KEYS: frozenset[str] = frozenset(
    {"total", "total amount", "amount due", "balance due", "grand total", "total due"}
)
_TAX_KEYS: frozenset[str] = frozenset(
    {"tax", "tax amount", "vat", "gst", "hst", "sales tax", "tax total"}
)
_CURRENCY_KEYS: frozenset[str] = frozenset({"currency", "currency code"})

# Currency symbol → ISO code mapping
_CURRENCY_SYMBOLS: dict[str, str] = {
    "$": "USD",
    "€": "EUR",
    "£": "GBP",
    "₹": "INR",
    "¥": "JPY",
    "₩": "KRW",
    "₪": "ILS",
    "₦": "NGN",
    "₫": "VND",
}

# Line-item column header keywords (lowercase)
_LINE_ITEM_DESC_HEADERS: frozenset[str] = frozenset(
    {"description", "item", "service", "product", "details", "particulars"}
)
_LINE_ITEM_QTY_HEADERS: frozenset[str] = frozenset(
    {"qty", "quantity", "units", "pcs", "nos"}
)
_LINE_ITEM_PRICE_HEADERS: frozenset[str] = frozenset(
    {"unit price", "rate", "price", "unit cost", "cost"}
)
_LINE_ITEM_AMOUNT_HEADERS: frozenset[str] = frozenset(
    {"amount", "total", "line total", "subtotal", "ext", "extended"}
)


class InvoiceParser:
    """
    Parses raw Textract blocks into a structured Invoice domain model.

    Usage:
        parser = InvoiceParser()
        invoice = parser.parse(blocks, bucket_name, file_key)
    """

    def parse(
        self,
        blocks: list[dict[str, Any]],
        bucket_name: str,
        file_key: str,
    ) -> Invoice:
        """
        Convert a flat list of Textract Block objects into an Invoice.

        Processing order:
          1. Index all blocks by Id for O(1) child lookup.
          2. Extract key-value pairs from KEY_VALUE_SET blocks.
          3. Extract line items from TABLE blocks.
          4. Map extracted key-value pairs to Invoice fields.
          5. Detect currency from amount strings if not explicitly found.
          6. Return a populated Invoice instance.

        Args:
            blocks:      Raw Textract response['Blocks'] list.
            bucket_name: S3 bucket name (stored as part of s3_path).
            file_key:    S3 object key (stored as s3_path).

        Returns:
            Populated Invoice domain model.

        Raises:
            InvoiceParsingException: If blocks is empty or fatally malformed.
        """
        if not blocks:
            logger.error(
                "Textract returned empty blocks list. bucket=%s key=%s",
                bucket_name,
                file_key,
            )
            raise InvoiceParsingException(
                f"Textract returned no blocks for s3://{bucket_name}/{file_key}."
            )

        logger.info(
            "Starting invoice parse. block_count=%d bucket=%s key=%s",
            len(blocks),
            bucket_name,
            file_key,
        )

        # Step 1: Build lookup index
        block_map: dict[str, dict[str, Any]] = self._build_block_map(blocks)

        # Step 2: Extract key-value pairs
        kv_pairs: dict[str, str] = self._extract_key_value_pairs(
            blocks, block_map
        )
        logger.info("Extracted %d key-value pairs from Textract.", len(kv_pairs))

        # Step 3: Extract line items from tables
        line_items: list[LineItem] = self._extract_line_items(blocks, block_map)
        logger.info("Extracted %d line items from Textract tables.", len(line_items))

        # Step 4: Map kv_pairs to invoice fields
        invoice: Invoice = self._map_to_invoice(
            kv_pairs=kv_pairs,
            line_items=line_items,
            blocks=blocks,
            bucket_name=bucket_name,
            file_key=file_key,
        )

        logger.info(
            "Invoice parsing complete. invoice_id=%s vendor=%r total=%r",
            invoice.invoice_id,
            invoice.vendor_name,
            invoice.total_amount,
        )
        return invoice

    # ------------------------------------------------------------------
    # Private: Block indexing
    # ------------------------------------------------------------------

    @staticmethod
    def _build_block_map(
        blocks: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """Build a dict of block_id → block for O(1) child resolution."""
        return {block["Id"]: block for block in blocks if "Id" in block}

    # ------------------------------------------------------------------
    # Private: Key-Value extraction
    # ------------------------------------------------------------------

    def _extract_key_value_pairs(
        self,
        blocks: list[dict[str, Any]],
        block_map: dict[str, dict[str, Any]],
    ) -> dict[str, str]:
        """
        Extract all FORMS key-value pairs from KEY_VALUE_SET blocks.

        Textract represents a form field as two linked KEY_VALUE_SET blocks:
          KEY block  → contains child WORD blocks forming the field label
          VALUE block → contains child WORD blocks forming the field value

        Returns:
            dict mapping normalised key text → value text.
        """
        kv_pairs: dict[str, str] = {}
        key_blocks: list[dict[str, Any]] = [
            b
            for b in blocks
            if b.get("BlockType") == "KEY_VALUE_SET"
            and "KEY" in b.get("EntityTypes", [])
        ]

        for key_block in key_blocks:
            key_text: str = self._get_text_from_block(key_block, block_map).strip()
            value_text: str = ""

            # Resolve the linked VALUE block
            for rel in key_block.get("Relationships", []):
                if rel.get("Type") == "VALUE":
                    for value_id in rel.get("Ids", []):
                        value_block = block_map.get(value_id)
                        if value_block:
                            value_text += (
                                self._get_text_from_block(value_block, block_map)
                                + " "
                            )

            value_text = value_text.strip()
            if key_text:
                kv_pairs[key_text.lower()] = value_text

        return kv_pairs

    def _get_text_from_block(
        self,
        block: dict[str, Any],
        block_map: dict[str, dict[str, Any]],
    ) -> str:
        """
        Concatenate all WORD child block texts for a given block.

        Args:
            block:     The parent KEY_VALUE_SET or CELL block.
            block_map: Full block id → block lookup dict.

        Returns:
            Space-joined text of all WORD children.
        """
        words: list[str] = []
        for rel in block.get("Relationships", []):
            if rel.get("Type") == "CHILD":
                for child_id in rel.get("Ids", []):
                    child = block_map.get(child_id)
                    if child and child.get("BlockType") == "WORD":
                        words.append(child.get("Text", ""))
        return " ".join(words)

    # ------------------------------------------------------------------
    # Private: Table / Line Item extraction
    # ------------------------------------------------------------------

    def _extract_line_items(
        self,
        blocks: list[dict[str, Any]],
        block_map: dict[str, dict[str, Any]],
    ) -> list[LineItem]:
        """
        Extract line items from Textract TABLE blocks.

        Strategy:
          1. Find all TABLE blocks.
          2. Collect all ROW cells, grouping by row index.
          3. Identify header row by matching cell text against known headers.
          4. Map subsequent rows to LineItem using the header column mapping.

        Returns:
            List of LineItem dataclasses. Empty list if no tables found.
        """
        line_items: list[LineItem] = []
        table_blocks: list[dict[str, Any]] = [
            b for b in blocks if b.get("BlockType") == "TABLE"
        ]

        for table in table_blocks:
            rows: dict[int, dict[int, str]] = self._extract_table_rows(
                table, block_map
            )
            if not rows:
                continue

            sorted_row_nums: list[int] = sorted(rows.keys())
            if len(sorted_row_nums) < 2:
                # Need at least a header row + one data row
                continue

            # Attempt to detect the header row
            header_row_num: int = sorted_row_nums[0]
            header_cells: dict[int, str] = rows[header_row_num]
            col_map: dict[str, int] = self._detect_column_map(header_cells)

            if not col_map:
                # No recognisable headers — skip this table
                logger.info(
                    "Table skipped — no recognisable line-item headers found."
                )
                continue

            for row_num in sorted_row_nums[1:]:
                cells: dict[int, str] = rows[row_num]
                item: LineItem = self._cells_to_line_item(cells, col_map)
                # Skip empty / total rows
                if item.description or item.amount:
                    line_items.append(item)

        return line_items

    def _extract_table_rows(
        self,
        table_block: dict[str, Any],
        block_map: dict[str, dict[str, Any]],
    ) -> dict[int, dict[int, str]]:
        """
        Build a row_index → {col_index → cell_text} mapping for a TABLE block.

        Returns:
            Nested dict: rows[row_index][col_index] = cell text.
        """
        rows: dict[int, dict[int, str]] = {}
        for rel in table_block.get("Relationships", []):
            if rel.get("Type") == "CHILD":
                for cell_id in rel.get("Ids", []):
                    cell = block_map.get(cell_id)
                    if not cell or cell.get("BlockType") != "CELL":
                        continue
                    row_idx: int = cell.get("RowIndex", 0)
                    col_idx: int = cell.get("ColumnIndex", 0)
                    cell_text: str = self._get_text_from_block(
                        cell, block_map
                    ).strip()
                    if row_idx not in rows:
                        rows[row_idx] = {}
                    rows[row_idx][col_idx] = cell_text
        return rows

    def _detect_column_map(self, header_cells: dict[int, str]) -> dict[str, int]:
        """
        Map column index to a semantic field name using header keyword matching.

        Args:
            header_cells: dict of col_index → header text.

        Returns:
            dict mapping field names ('description', 'quantity', 'unit_price',
            'amount') to their column index. Only includes detected fields.
        """
        col_map: dict[str, int] = {}
        for col_idx, text in header_cells.items():
            lower: str = text.lower().strip()
            if lower in _LINE_ITEM_DESC_HEADERS:
                col_map["description"] = col_idx
            elif lower in _LINE_ITEM_QTY_HEADERS:
                col_map["quantity"] = col_idx
            elif lower in _LINE_ITEM_PRICE_HEADERS:
                col_map["unit_price"] = col_idx
            elif lower in _LINE_ITEM_AMOUNT_HEADERS and "amount" not in col_map:
                col_map["amount"] = col_idx
        return col_map

    @staticmethod
    def _cells_to_line_item(
        cells: dict[int, str], col_map: dict[str, int]
    ) -> LineItem:
        """Build a LineItem from a data row using the detected column map."""
        return LineItem(
            description=cells.get(col_map.get("description", -1), ""),
            quantity=cells.get(col_map.get("quantity", -1), ""),
            unit_price=cells.get(col_map.get("unit_price", -1), ""),
            amount=cells.get(col_map.get("amount", -1), ""),
        )

    # ------------------------------------------------------------------
    # Private: Field mapping
    # ------------------------------------------------------------------

    def _map_to_invoice(
        self,
        kv_pairs: dict[str, str],
        line_items: list[LineItem],
        blocks: list[dict[str, Any]],
        bucket_name: str,
        file_key: str,
    ) -> Invoice:
        """
        Map extracted key-value pairs to Invoice domain model fields.

        Uses keyword sets to match Textract keys to our field names,
        falling back to empty strings for any undetected fields.

        Returns:
            Fully populated Invoice instance.
        """
        vendor_name: str = self._find_value(kv_pairs, _VENDOR_KEYS)
        invoice_number: str = self._find_value(kv_pairs, _INVOICE_NUMBER_KEYS)
        invoice_date: str = self._find_value(kv_pairs, _INVOICE_DATE_KEYS)
        due_date: str = self._find_value(kv_pairs, _DUE_DATE_KEYS)
        total_amount: str = self._clean_amount(
            self._find_value(kv_pairs, _TOTAL_KEYS)
        )
        tax_amount: str = self._clean_amount(
            self._find_value(kv_pairs, _TAX_KEYS)
        )
        currency: str = self._find_value(kv_pairs, _CURRENCY_KEYS)

        # Auto-detect currency from total_amount string if not found explicitly
        if not currency:
            raw_total: str = self._find_value(kv_pairs, _TOTAL_KEYS)
            currency = self._detect_currency(raw_total)

        # Build full raw extracted JSON for storage (all kv pairs + line items)
        extracted_json: dict[str, Any] = {
            "kv_pairs": kv_pairs,
            "line_items": [
                {
                    "description": li.description,
                    "quantity": li.quantity,
                    "unit_price": li.unit_price,
                    "amount": li.amount,
                }
                for li in line_items
            ],
            "block_count": len(blocks),
        }

        # Generate a unique invoice_id — use invoice_number if extracted,
        # otherwise fall back to a UUID
        invoice_id: str = (
            f"INV-{invoice_number}" if invoice_number else f"INV-{uuid.uuid4()}"
        )

        return Invoice(
            invoice_id=invoice_id,
            vendor_name=vendor_name,
            invoice_number=invoice_number,
            invoice_date=invoice_date,
            due_date=due_date,
            currency=currency,
            tax_amount=tax_amount,
            total_amount=total_amount,
            line_items=line_items,
            extracted_json=extracted_json,
            s3_path=f"s3://{bucket_name}/{file_key}",
            created_at=datetime.now(tz=timezone.utc).isoformat(),
        )

    @staticmethod
    def _find_value(
        kv_pairs: dict[str, str], keyword_set: frozenset[str]
    ) -> str:
        """
        Search kv_pairs for a key that matches any keyword in keyword_set.

        Performs case-insensitive substring matching to handle slight
        OCR variations (e.g. "VENDOR NAME:" still matches "vendor name").

        Returns:
            The matched value string, or "" if no match found.
        """
        for key, value in kv_pairs.items():
            key_clean: str = key.strip().rstrip(":").strip().lower()
            if key_clean in keyword_set:
                return value
        # Fallback: substring match
        for key, value in kv_pairs.items():
            key_clean = key.strip().rstrip(":").strip().lower()
            for keyword in keyword_set:
                if keyword in key_clean or key_clean in keyword:
                    return value
        return ""

    @staticmethod
    def _clean_amount(raw: str) -> str:
        """
        Strip currency symbols, commas, and whitespace from an amount string.

        Examples:
            "$1,234.56"  → "1234.56"
            "₹ 12,999"  → "12999"
            "1,234.56"   → "1234.56"
        """
        if not raw:
            return ""
        # Remove everything except digits, decimal point, and minus sign
        cleaned: str = re.sub(r"[^\d.\-]", "", raw)
        return cleaned if cleaned else raw

    @staticmethod
    def _detect_currency(raw: str) -> str:
        """
        Detect currency from a raw amount string by checking for symbol prefixes.

        Args:
            raw: Raw amount string, e.g. "$1,234.56" or "₹12,999".

        Returns:
            ISO currency code string (e.g. "USD"), or "" if undetected.
        """
        if not raw:
            return ""
        for symbol, code in _CURRENCY_SYMBOLS.items():
            if symbol in raw:
                return code
        return ""
