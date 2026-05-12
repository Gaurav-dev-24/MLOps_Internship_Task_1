/**
 * Invoice status constants
 */
export const INVOICE_STATUS = {
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};

/**
 * Supported file types for upload
 */
export const SUPPORTED_FILE_TYPES = [
  'application/pdf',
  'image/png',
  'image/jpeg',
  'image/jpg',
];

export const SUPPORTED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg'];

/**
 * Max file size: 10 MB
 */
export const MAX_FILE_SIZE = 10 * 1024 * 1024;
