import { apiClient } from '../api';

/**
 * Upload service — handles all upload-related API calls.
 */
const uploadService = {
  /**
   * Request a pre-signed upload URL from the backend.
   * @param {string} fileName
   * @param {string} fileType
   * @returns {Promise<{ upload_url: string, file_key: string }>}
   */
  getUploadUrl(fileName, fileType) {
    return apiClient.post('/generate-upload-url', { file_name: fileName, file_type: fileType });
  },

  /**
   * Upload a file directly to S3 using the pre-signed URL.
   * IMPORTANT: Must use native fetch — NOT axios — because:
   *   1. The pre-signed URL is absolute (not relative to VITE_API_BASE_URL)
   *   2. Axios would add Content-Type: application/json, breaking the S3 signature
   *   3. S3 pre-signed PUT requires exact headers matching the signature
   *
   * @param {string} uploadUrl  — The full pre-signed S3 PUT URL
   * @param {File} file
   * @param {function} onProgress — callback receiving percentage (0–100)
   * @returns {Promise<void>}
   */
  async uploadToS3(uploadUrl, file, onProgress) {
    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable && onProgress) {
          onProgress(Math.round((event.loaded * 100) / event.total));
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status >= 200 && xhr.status < 300) {
          resolve();
        } else {
          reject(new Error(`S3 upload failed with status ${xhr.status}`));
        }
      });

      xhr.addEventListener('error', () => {
        reject(new Error('S3 upload network error'));
      });

      xhr.open('PUT', uploadUrl);
      xhr.setRequestHeader('Content-Type', file.type);
      xhr.send(file);
    });
  },
};

export default uploadService;
