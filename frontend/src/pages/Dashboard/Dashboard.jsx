import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { invoiceService } from '../../services';
import { InvoiceTable } from '../../components/invoice';
import { LoadingSpinner, ErrorState } from '../../components/common';
import { formatCurrency } from '../../utils';

const statCards = [
  {
    key: 'total',
    label: 'Total Invoices',
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
      </svg>
    ),
    color: 'text-brand-400',
    bg: 'bg-brand-500/10',
  },
  {
    key: 'processed',
    label: 'Processed',
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75 11.25 15 15 9.75M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      </svg>
    ),
    color: 'text-emerald-400',
    bg: 'bg-emerald-500/10',
  },
  {
    key: 'failed',
    label: 'Failed',
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="m9.75 9.75 4.5 4.5m0-4.5-4.5 4.5M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      </svg>
    ),
    color: 'text-red-400',
    bg: 'bg-red-500/10',
  },
  {
    key: 'totalAmount',
    label: 'Total Extracted',
    icon: (
      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18.75a60.07 60.07 0 0 1 15.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 0 1 3 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 0 0-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 0 1-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 0 0 3 15h-.75M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm3 0h.008v.008H18V10.5Zm-12 0h.008v.008H6V10.5Z" />
      </svg>
    ),
    color: 'text-amber-400',
    bg: 'bg-amber-500/10',
    isCurrency: true,
  },
];

/**
 * Dashboard page with stats cards and recent invoices.
 */
export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState({ total: 0, processed: 0, failed: 0, totalAmount: 0 });
  const [recentInvoices, setRecentInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDashboard() {
      try {
        setLoading(true);
        const [statsResult, recentResult] = await Promise.allSettled([
          invoiceService.getStats(),
          invoiceService.getRecent(5),
        ]);

        if (statsResult.status === 'fulfilled') {
          setStats(statsResult.value.data || statsResult.value);
        }
        if (recentResult.status === 'fulfilled') {
          const data = recentResult.value?.data || recentResult.value || [];
          setRecentInvoices(Array.isArray(data) ? data : []);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchDashboard();
  }, []);

  if (error && !loading) {
    return <ErrorState message={error} onRetry={() => window.location.reload()} />;
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white" id="dashboard-title">Dashboard</h1>
          <p className="mt-1 text-sm text-gray-500">Overview of your invoice processing pipeline.</p>
        </div>
        <button
          onClick={() => navigate('/upload')}
          className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition-all hover:bg-brand-500 hover:shadow-brand-500/30 active:scale-[0.98]"
          id="upload-cta-btn"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Upload Invoice
        </button>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((card, index) => (
          <div
            key={card.key}
            className="card group relative overflow-hidden p-5 transition-all duration-300 hover:border-gray-700 hover:shadow-lg hover:shadow-black/20"
            style={{ animationDelay: `${index * 80}ms` }}
            id={`stat-${card.key}`}
          >
            {/* Subtle glow */}
            <div className="absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br from-brand-600/5 to-transparent opacity-0 transition-opacity group-hover:opacity-100" />

            <div className="flex items-center justify-between">
              <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${card.bg} ${card.color}`}>
                {card.icon}
              </div>
            </div>
            <div className="mt-4">
              <p className="text-2xl font-bold tabular-nums text-white">
                {loading ? (
                  <span className="inline-block h-7 w-16 animate-pulse rounded bg-gray-800" />
                ) : card.isCurrency ? (
                  formatCurrency(stats[card.key])
                ) : (
                  stats[card.key]?.toLocaleString() || '0'
                )}
              </p>
              <p className="mt-1 text-sm text-gray-500">{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Recent invoices */}
      <div className="card overflow-hidden">
        <div className="flex items-center justify-between border-b border-gray-800 px-6 py-4">
          <h2 className="text-base font-semibold text-gray-100">Recent Invoices</h2>
          <button
            onClick={() => navigate('/history')}
            className="text-sm font-medium text-brand-400 transition-colors hover:text-brand-300"
            id="view-all-btn"
          >
            View all →
          </button>
        </div>
        <InvoiceTable invoices={recentInvoices} loading={loading} />
      </div>
    </div>
  );
}
