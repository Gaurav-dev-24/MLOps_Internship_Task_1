import { useNavigate } from 'react-router-dom';
import { UploadCard } from '../../components/upload';
import { UploadProgress } from '../../components/upload';
import { useUpload } from '../../hooks';

/**
 * Upload page with drag-and-drop zone and progress tracking.
 */
export default function Upload() {
  const navigate = useNavigate();
  const { file, progress, status, error, selectFile, upload, reset } = useUpload();

  const handleFileSelect = (selectedFile) => {
    selectFile(selectedFile);
  };

  const isIdle = status === 'idle';
  const hasFile = !!file;

  return (
    <div className="mx-auto max-w-2xl space-y-8 animate-fade-in">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white" id="upload-title">Upload Invoice</h1>
        <p className="mt-1 text-sm text-gray-500">
          Upload an invoice document to extract structured data using AI.
        </p>
      </div>

      {/* Upload zone */}
      {(isIdle || status === 'validating') && !hasFile && (
        <UploadCard onFileSelect={handleFileSelect} />
      )}

      {/* File selected — show preview + upload button */}
      {hasFile && isIdle && (
        <div className="space-y-4 animate-slide-up">
          <UploadProgress file={file} progress={0} status="idle" onCancel={reset} />
          <div className="flex items-center justify-end gap-3">
            <button
              onClick={reset}
              className="rounded-xl px-5 py-2.5 text-sm font-medium text-gray-400 transition-colors hover:bg-gray-800 hover:text-gray-200"
              id="cancel-upload-btn"
            >
              Cancel
            </button>
            <button
              onClick={upload}
              className="inline-flex items-center gap-2 rounded-xl bg-brand-600 px-6 py-2.5 text-sm font-semibold text-white shadow-lg shadow-brand-600/20 transition-all hover:bg-brand-500 hover:shadow-brand-500/30 active:scale-[0.98]"
              id="start-upload-btn"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
              </svg>
              Upload & Analyze
            </button>
          </div>
        </div>
      )}

      {/* Uploading / Success / Error states */}
      {(status === 'uploading' || status === 'success' || status === 'error') && (
        <div className="space-y-4">
          <UploadProgress
            file={file}
            progress={progress}
            status={status}
            error={error}
            onCancel={reset}
          />

          {status === 'success' && (
            <div className="card p-6 text-center animate-slide-up">
              <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-emerald-500/10">
                <svg className="h-7 w-7 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold text-gray-100">Upload Successful</h3>
              <p className="mt-2 text-sm text-gray-500">
                Your invoice is being processed. You'll see the results shortly.
              </p>
              <div className="mt-6 flex items-center justify-center gap-3">
                <button
                  onClick={reset}
                  className="rounded-xl px-5 py-2.5 text-sm font-medium text-gray-400 transition-colors hover:bg-gray-800 hover:text-gray-200"
                  id="upload-another-btn"
                >
                  Upload Another
                </button>
                <button
                  onClick={() => navigate('/history')}
                  className="rounded-xl bg-brand-600 px-5 py-2.5 text-sm font-semibold text-white transition-all hover:bg-brand-500"
                  id="view-history-btn"
                >
                  View History
                </button>
              </div>
            </div>
          )}

          {status === 'error' && (
            <div className="flex items-center justify-center gap-3">
              <button
                onClick={reset}
                className="rounded-xl bg-gray-800 px-5 py-2.5 text-sm font-medium text-gray-300 transition-colors hover:bg-gray-700"
                id="try-again-btn"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      )}

      {/* Validation error */}
      {status === 'error' && !file && error && (
        <div className="card border-red-500/20 bg-red-500/5 p-5 animate-slide-up">
          <div className="flex items-start gap-3">
            <svg className="mt-0.5 h-5 w-5 shrink-0 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
            <div>
              <p className="text-sm font-medium text-red-400">{error}</p>
              <button
                onClick={reset}
                className="mt-2 text-sm font-medium text-red-300 underline underline-offset-2 hover:text-red-200"
              >
                Try again
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
