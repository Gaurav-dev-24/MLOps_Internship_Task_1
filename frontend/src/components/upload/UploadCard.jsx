import { useCallback, useRef, useState } from 'react';
import { cn, SUPPORTED_EXTENSIONS } from '../../utils';

/**
 * Drag-and-drop upload card with file picker fallback.
 */
export default function UploadCard({ onFileSelect, disabled = false }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (!disabled) setIsDragging(true);
  }, [disabled]);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);
      if (disabled) return;

      const droppedFile = e.dataTransfer.files?.[0];
      if (droppedFile) onFileSelect(droppedFile);
    },
    [disabled, onFileSelect],
  );

  const handleClick = () => {
    if (!disabled) inputRef.current?.click();
  };

  const handleChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) onFileSelect(selectedFile);
    e.target.value = '';
  };

  return (
    <div
      id="upload-drop-zone"
      role="button"
      tabIndex={0}
      onClick={handleClick}
      onKeyDown={(e) => e.key === 'Enter' && handleClick()}
      onDragEnter={handleDragEnter}
      onDragLeave={handleDragLeave}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      className={cn(
        'group relative cursor-pointer rounded-2xl border-2 border-dashed p-12 text-center transition-all duration-300',
        isDragging
          ? 'border-brand-400 bg-brand-500/5 scale-[1.01]'
          : 'border-gray-700 bg-gray-900/40 hover:border-gray-600 hover:bg-gray-900/60',
        disabled && 'pointer-events-none opacity-50',
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept={SUPPORTED_EXTENSIONS.join(',')}
        onChange={handleChange}
        className="hidden"
        id="file-input"
      />

      {/* Icon */}
      <div
        className={cn(
          'mx-auto mb-5 flex h-16 w-16 items-center justify-center rounded-2xl transition-colors duration-300',
          isDragging ? 'bg-brand-500/20 text-brand-400' : 'bg-gray-800/60 text-gray-400 group-hover:bg-gray-800 group-hover:text-gray-300',
        )}
      >
        <svg className="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
        </svg>
      </div>

      {/* Text */}
      <p className="text-base font-medium text-gray-200">
        {isDragging ? 'Drop your file here' : 'Drag & drop your invoice'}
      </p>
      <p className="mt-2 text-sm text-gray-500">
        or <span className="text-brand-400 font-medium">browse files</span>
      </p>

      {/* Supported formats */}
      <div className="mt-5 flex items-center justify-center gap-2">
        {['PDF', 'PNG', 'JPG', 'JPEG'].map((ext) => (
          <span
            key={ext}
            className="rounded-md bg-gray-800/80 px-2 py-0.5 text-[11px] font-medium tracking-wide text-gray-400"
          >
            {ext}
          </span>
        ))}
        <span className="text-xs text-gray-600">• Max 10 MB</span>
      </div>
    </div>
  );
}
