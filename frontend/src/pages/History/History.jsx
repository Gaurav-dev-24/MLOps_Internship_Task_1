import { useState } from 'react';
import { InvoiceTable } from '../../components/invoice';
import { useInvoices } from '../../hooks';
import { INVOICE_STATUS, cn } from '../../utils';
import ErrorState from "../../components/common/ErrorState";

const statusOptions = [
  { value: '', label: 'All Statuses' },
  { value: INVOICE_STATUS.COMPLETED, label: 'Completed' },
  { value: INVOICE_STATUS.PROCESSING, label: 'Processing' },
  { value: INVOICE_STATUS.FAILED, label: 'Failed' },
];

/**
 * History page with searchable, filterable, paginated invoice table.
 */
export default function History() {
  const { invoices, loading, error, pagination, params, updateParams, goToPage, refetch } =
    useInvoices();

  const [searchInput, setSearchInput] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    updateParams({ search: searchInput });
  };

  const handleStatusChange = (status) => {
    updateParams({ status });
  };

  const handleDateChange = (key, value) => {
    updateParams({ [key]: value });
  };

  if (error && !loading) {
    return <ErrorState message={error} onRetry={refetch} />;
  }

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white" id="history-title">Invoice History</h1>
        <p className="mt-1 text-sm text-gray-500">Browse and search your processed invoices.</p>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1">
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-gray-500">
              Search
            </label>
            <div className="relative">
              <svg
                className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                strokeWidth={1.5}
              >
                <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
              </svg>
              <input
                type="text"
                placeholder="Search by vendor, invoice number…"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="w-full rounded-lg bg-gray-900 py-2.5 pl-10 pr-4 text-sm text-gray-200 ring-1 ring-gray-800 placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-brand-500/40"
                id="search-input"
              />
            </div>
          </form>

          {/* Status filter */}
          <div className="w-full sm:w-48">
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-gray-500">
              Status
            </label>
            <select
              value={params.status}
              onChange={(e) => handleStatusChange(e.target.value)}
              className="w-full rounded-lg bg-gray-900 px-3 py-2.5 text-sm text-gray-200 ring-1 ring-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-500/40 appearance-none"
              id="status-filter"
            >
              {statusOptions.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </div>

          {/* Start date */}
          <div className="w-full sm:w-44">
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-gray-500">
              From
            </label>
            <input
              type="date"
              value={params.startDate}
              onChange={(e) => handleDateChange('startDate', e.target.value)}
              className="w-full rounded-lg bg-gray-900 px-3 py-2.5 text-sm text-gray-200 ring-1 ring-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-500/40"
              id="date-from"
            />
          </div>

          {/* End date */}
          <div className="w-full sm:w-44">
            <label className="mb-1.5 block text-xs font-medium uppercase tracking-wider text-gray-500">
              To
            </label>
            <input
              type="date"
              value={params.endDate}
              onChange={(e) => handleDateChange('endDate', e.target.value)}
              className="w-full rounded-lg bg-gray-900 px-3 py-2.5 text-sm text-gray-200 ring-1 ring-gray-800 focus:outline-none focus:ring-2 focus:ring-brand-500/40"
              id="date-to"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <InvoiceTable invoices={invoices} loading={loading} />
      </div>

      {/* Pagination */}
      {pagination.totalPages > 1 && (
        <div className="flex items-center justify-between" id="pagination">
          <p className="text-sm text-gray-500">
            Page <span className="font-medium text-gray-300">{pagination.page}</span> of{' '}
            <span className="font-medium text-gray-300">{pagination.totalPages}</span>
            <span className="ml-2 text-gray-600">({pagination.total} total)</span>
          </p>
          <div className="flex items-center gap-2">
            <button
              onClick={() => goToPage(pagination.page - 1)}
              disabled={pagination.page <= 1}
              className={cn(
                'rounded-lg px-3.5 py-2 text-sm font-medium transition-colors',
                pagination.page <= 1
                  ? 'cursor-not-allowed text-gray-700'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200',
              )}
              id="prev-page-btn"
            >
              ← Previous
            </button>
            <button
              onClick={() => goToPage(pagination.page + 1)}
              disabled={pagination.page >= pagination.totalPages}
              className={cn(
                'rounded-lg px-3.5 py-2 text-sm font-medium transition-colors',
                pagination.page >= pagination.totalPages
                  ? 'cursor-not-allowed text-gray-700'
                  : 'text-gray-400 hover:bg-gray-800 hover:text-gray-200',
              )}
              id="next-page-btn"
            >
              Next →
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
