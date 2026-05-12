import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { invoiceService } from '../../services';
import { SummaryCard, LineItemsTable, JsonViewer } from '../../components/invoice';
import { LoadingSpinner, ErrorState } from '../../components/common';

/**
 * Invoice details page showing summary, line items, and extracted JSON.
 */
export default function InvoiceDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchInvoice() {
      try {
        setLoading(true);
        const result = await invoiceService.getById(id);
        setInvoice(result.data || result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchInvoice();
  }, [id]);

  if (loading) {
    return (
      <div className="flex h-96 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  }

  if (!invoice) {
    return <ErrorState message="Invoice not found." />;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate(-1)}
            className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-800 hover:text-gray-200"
            id="back-btn"
            aria-label="Go back"
          >
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5 3 12m0 0 7.5-7.5M3 12h18" />
            </svg>
          </button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-white" id="invoice-detail-title">
              Invoice Details
            </h1>
            <p className="mt-0.5 text-sm text-gray-500">
              {invoice.invoice_number || id}
            </p>
          </div>
        </div>
      </div>

      {/* Summary */}
      <SummaryCard invoice={invoice} />

      {/* Line items */}
      <LineItemsTable items={invoice.line_items || invoice.items || []} />

      {/* JSON viewer */}
      <JsonViewer data={invoice.extracted_json || invoice} />
    </div>
  );
}
