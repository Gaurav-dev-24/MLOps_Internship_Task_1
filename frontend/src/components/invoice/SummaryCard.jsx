import { formatCurrency, formatDate } from '../../utils';
import { StatusBadge } from '../common';

/**
 * Invoice summary card displaying key invoice metadata.
 */
export default function SummaryCard({ invoice }) {
  if (!invoice) return null;

  const fields = [
    { label: 'Vendor Name', value: invoice.vendor_name || '—' },
    { label: 'Invoice Number', value: invoice.invoice_number || '—' },
    { label: 'Invoice Date', value: formatDate(invoice.invoice_date) },
    { label: 'Total Amount', value: formatCurrency(invoice.total_amount), highlight: true },
    { label: 'Tax Amount', value: formatCurrency(invoice.tax_amount) },
    { label: 'Due Date', value: formatDate(invoice.due_date) },
  ];

  return (
    <div className="card overflow-hidden animate-slide-up">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-gray-800 px-6 py-4">
        <h3 className="text-base font-semibold text-gray-100">Invoice Summary</h3>
        <StatusBadge status={invoice.status} />
      </div>

      {/* Fields grid */}
      <div className="grid grid-cols-1 gap-px bg-gray-800/40 sm:grid-cols-2 lg:grid-cols-3">
        {fields.map((field) => (
          <div key={field.label} className="bg-gray-900/70 px-6 py-4">
            <p className="text-xs font-medium uppercase tracking-wider text-gray-500">{field.label}</p>
            <p
              className={`mt-1.5 text-sm font-medium ${
                field.highlight ? 'text-brand-400' : 'text-gray-200'
              }`}
            >
              {field.value}
            </p>
          </div>
        ))}
      </div>

      {/* Summary text */}
      {invoice.summary && (
        <div className="border-t border-gray-800 px-6 py-4">
          <p className="text-xs font-medium uppercase tracking-wider text-gray-500 mb-2">AI Summary</p>
          <p className="text-sm leading-relaxed text-gray-300">{invoice.summary}</p>
        </div>
      )}
    </div>
  );
}
