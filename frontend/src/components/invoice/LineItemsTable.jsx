import { formatCurrency } from '../../utils';

/**
 * Line items table for invoice details page.
 */
export default function LineItemsTable({ items = [] }) {
  if (!items.length) {
    return (
      <div className="card px-6 py-10 text-center text-sm text-gray-500 animate-slide-up">
        No line items extracted.
      </div>
    );
  }

  return (
    <div className="card overflow-hidden animate-slide-up" id="line-items-table">
      <div className="border-b border-gray-800 px-6 py-4">
        <h3 className="text-base font-semibold text-gray-100">Line Items</h3>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead>
            <tr className="border-b border-gray-800 text-xs uppercase tracking-wider text-gray-500">
              <th className="px-6 py-3 font-medium">#</th>
              <th className="px-6 py-3 font-medium">Item</th>
              <th className="px-6 py-3 font-medium text-right">Qty</th>
              <th className="px-6 py-3 font-medium text-right">Unit Price</th>
              <th className="px-6 py-3 font-medium text-right">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-800/60">
            {items.map((item, index) => (
              <tr key={index} className="transition-colors hover:bg-gray-800/30">
                <td className="px-6 py-3.5 text-gray-500 tabular-nums">{index + 1}</td>
                <td className="px-6 py-3.5 font-medium text-gray-200">{item.name || item.description || '—'}</td>
                <td className="px-6 py-3.5 text-right text-gray-400 tabular-nums">{item.quantity ?? '—'}</td>
                <td className="px-6 py-3.5 text-right text-gray-400 tabular-nums">{formatCurrency(item.unit_price)}</td>
                <td className="px-6 py-3.5 text-right font-medium text-gray-200 tabular-nums">{formatCurrency(item.total)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t border-gray-700">
              <td colSpan={4} className="px-6 py-3.5 text-right text-xs uppercase tracking-wider font-medium text-gray-400">
                Total
              </td>
              <td className="px-6 py-3.5 text-right font-semibold text-brand-400 tabular-nums">
                {formatCurrency(items.reduce((sum, item) => sum + (item.total || 0), 0))}
              </td>
            </tr>
          </tfoot>
        </table>
      </div>
    </div>
  );
}
