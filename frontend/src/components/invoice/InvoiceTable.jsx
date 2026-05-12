import { useNavigate } from 'react-router-dom';
import { StatusBadge } from '../common';
import { EmptyState } from '../common';
import { formatCurrency, formatDate, truncate } from '../../utils';

/**
 * Invoice table with clickable rows for navigation to details.
 */
export default function InvoiceTable({ invoices: rawInvoices = [], loading = false }) {
  const navigate = useNavigate();
  const invoices = Array.isArray(rawInvoices) ? rawInvoices : [];

  if (!loading && invoices.length === 0) {
    return (
      <EmptyState
        icon={
          <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
          </svg>
        }
        title="No invoices found"
        description="Upload your first invoice to get started."
      />
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-left text-sm" id="invoice-table">
        <thead>
          <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
            <th className="px-4 py-3 font-medium">Invoice</th>
            <th className="px-4 py-3 font-medium">Vendor</th>
            <th className="px-4 py-3 font-medium">Date</th>
            <th className="px-4 py-3 font-medium text-right">Amount</th>
            <th className="px-4 py-3 font-medium text-center">Status</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-800/60">
          {loading
            ? Array.from({ length: 5 }).map((_, i) => (
                <tr key={i} className="animate-pulse">
                  <td className="px-4 py-4"><div className="h-4 w-24 rounded bg-gray-800" /></td>
                  <td className="px-4 py-4"><div className="h-4 w-32 rounded bg-gray-800" /></td>
                  <td className="px-4 py-4"><div className="h-4 w-20 rounded bg-gray-800" /></td>
                  <td className="px-4 py-4 text-right"><div className="ml-auto h-4 w-20 rounded bg-gray-800" /></td>
                  <td className="px-4 py-4 text-center"><div className="mx-auto h-5 w-20 rounded-full bg-gray-800" /></td>
                </tr>
              ))
            : invoices.map((invoice) => (
                <tr
                  key={invoice.invoice_id}
                  onClick={() => navigate(`/invoice/${invoice.invoice_id}`)}
                  className="group cursor-pointer transition-colors hover:bg-gray-800/40"
                  id={`invoice-row-${invoice.invoice_id}`}
                >
                  <td className="px-4 py-4">
                    <span className="font-medium text-gray-200 group-hover:text-brand-400 transition-colors">
                      {invoice.invoice_number || invoice.invoice_id?.slice(0, 8)}
                    </span>
                  </td>
                  <td className="px-4 py-4 text-gray-400">
                    {truncate(invoice.vendor_name, 28) || '—'}
                  </td>
                  <td className="px-4 py-4 text-gray-500">
                    {formatDate(invoice.invoice_date)}
                  </td>
                  <td className="px-4 py-4 text-right font-medium tabular-nums text-gray-200">
                    {formatCurrency(invoice.total_amount)}
                  </td>
                  <td className="px-4 py-4 text-center">
                    <StatusBadge status={invoice.status} />
                  </td>
                </tr>
              ))}
        </tbody>
      </table>
    </div>
  );
}
