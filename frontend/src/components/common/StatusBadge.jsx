import { cn } from '../../utils';
import { INVOICE_STATUS } from '../../utils';

const statusConfig = {
  [INVOICE_STATUS.PROCESSING]: {
    label: 'Processing',
    dot: 'bg-amber-400',
    bg: 'bg-amber-400/10',
    text: 'text-amber-400',
    ring: 'ring-amber-400/20',
  },
  [INVOICE_STATUS.COMPLETED]: {
    label: 'Completed',
    dot: 'bg-emerald-400',
    bg: 'bg-emerald-400/10',
    text: 'text-emerald-400',
    ring: 'ring-emerald-400/20',
  },
  [INVOICE_STATUS.FAILED]: {
    label: 'Failed',
    dot: 'bg-red-400',
    bg: 'bg-red-400/10',
    text: 'text-red-400',
    ring: 'ring-red-400/20',
  },
};

/**
 * Status badge component showing processing state with animated dot.
 */
export default function StatusBadge({ status, className = '' }) {
  const config = statusConfig[status] || statusConfig[INVOICE_STATUS.PROCESSING];

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium ring-1 ring-inset',
        config.bg,
        config.text,
        config.ring,
        className,
      )}
    >
      <span
        className={cn(
          'h-1.5 w-1.5 rounded-full',
          config.dot,
          status === INVOICE_STATUS.PROCESSING && 'animate-pulse',
        )}
      />
      {config.label}
    </span>
  );
}
