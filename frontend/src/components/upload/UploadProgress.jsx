import { cn, formatFileSize } from '../../utils';

/**
 * Upload progress bar with file info, progress percentage, and states.
 */
export default function UploadProgress({ file, progress, status, error, onCancel }) {
  const isUploading = status === 'uploading';
  const isSuccess = status === 'success';
  const isError = status === 'error';

  return (
    <div className="card p-6 animate-slide-up">
      {/* File info */}
      <div className="flex items-start gap-4">
        {/* File icon */}
        <div
          className={cn(
            'flex h-12 w-12 shrink-0 items-center justify-center rounded-xl',
            isError ? 'bg-red-500/10 text-red-400' : isSuccess ? 'bg-emerald-500/10 text-emerald-400' : 'bg-brand-500/10 text-brand-400',
          )}
        >
          {isSuccess ? (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
          ) : isError ? (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          )}
        </div>

        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-medium text-gray-200">{file?.name || 'Unknown file'}</p>
          <p className="mt-0.5 text-xs text-gray-500">
            {file ? formatFileSize(file.size) : '—'}
            {isSuccess && ' • Upload complete'}
            {isError && ' • Upload failed'}
          </p>
        </div>

        {/* Cancel / Status */}
        <div className="shrink-0">
          {isUploading && (
            <span className="text-sm font-semibold tabular-nums text-brand-400">{progress}%</span>
          )}
          {(isSuccess || isError) && onCancel && (
            <button
              onClick={onCancel}
              id="upload-cancel-btn"
              className="rounded-lg p-1.5 text-gray-500 transition-colors hover:bg-gray-800 hover:text-gray-300"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      {(isUploading || isSuccess) && (
        <div className="mt-4 h-1.5 w-full overflow-hidden rounded-full bg-gray-800">
          <div
            className={cn(
              'h-full rounded-full transition-all duration-500 ease-out',
              isSuccess ? 'bg-emerald-500' : 'bg-brand-500',
            )}
            style={{ width: `${progress}%` }}
          />
        </div>
      )}

      {/* Error message */}
      {isError && error && (
        <p className="mt-3 text-sm text-red-400">{error}</p>
      )}
    </div>
  );
}
