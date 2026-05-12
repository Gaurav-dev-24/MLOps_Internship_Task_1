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
   * @param {string} uploadUrl
   * @param {File} file
   * @param {function} onProgress — callback receiving percentage (0–100)
   * @returns {Promise<void>}
   */
  uploadToS3(uploadUrl, file, onProgress) {
    return apiClient.put(uploadUrl, file, {
      baseURL: '',
      headers: { 'Content-Type': file.type },
      onUploadProgress: (event) => {
        if (event.total) {
          onProgress(Math.round((event.loaded * 100) / event.total));
        }
      },
    });
  },
};

export default uploadService;
