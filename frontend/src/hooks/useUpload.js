import { useState, useCallback } from 'react';
import { uploadService } from '../services';
import { validateFile } from '../utils';

/**
 * Custom hook for invoice file upload with progress tracking.
 */
export default function useUpload() {
  const [file, setFile] = useState(null);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('idle'); // idle | validating | uploading | success | error
  const [error, setError] = useState(null);

  const reset = useCallback(() => {
    setFile(null);
    setProgress(0);
    setStatus('idle');
    setError(null);
  }, []);

  const selectFile = useCallback((selectedFile) => {
    setError(null);
    setStatus('validating');

    const validation = validateFile(selectedFile);
    if (!validation.valid) {
      setError(validation.error);
      setStatus('error');
      return false;
    }

    setFile(selectedFile);
    setStatus('idle');
    return true;
  }, []);

  const upload = useCallback(async () => {
    if (!file) {
      setError('No file selected.');
      setStatus('error');
      return;
    }

    try {
      setStatus('uploading');
      setProgress(0);

      // Step 1: Get pre-signed URL
      const { data } = await uploadService.getUploadUrl(file.name, file.type);

      // Step 2: Upload to S3
      await uploadService.uploadToS3(data.upload_url, file, setProgress);

      setStatus('success');
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
      setStatus('error');
    }
  }, [file]);

  return { file, progress, status, error, selectFile, upload, reset };
}
