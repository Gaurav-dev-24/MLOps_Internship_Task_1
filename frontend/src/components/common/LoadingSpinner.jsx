import { cn } from '../../utils';

/**
 * Reusable loading spinner with configurable size.
 */
export default function LoadingSpinner({ size = 'md', className = '' }) {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-[3px]',
    lg: 'h-12 w-12 border-4',
    xl: 'h-16 w-16 border-4',
  };

  return (
    <div className={cn('flex items-center justify-center', className)}>
      <div
        className={cn(
          'animate-spin rounded-full border-brand-500/30 border-t-brand-500',
          sizes[size],
        )}
        role="status"
        aria-label="Loading"
      />
    </div>
  );
}
