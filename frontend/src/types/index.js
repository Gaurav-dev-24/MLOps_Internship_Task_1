/**
 * Type definitions and JSDoc type references for the project.
 * These serve as documentation for the data structures used throughout the app.
 */

/**
 * @typedef {Object} Invoice
 * @property {string} invoice_id - Unique identifier
 * @property {string} invoice_number - Human-readable invoice number
 * @property {string} vendor_name - Name of the vendor
 * @property {string} invoice_date - ISO date string
 * @property {string} due_date - ISO date string
 * @property {string} currency - Currency code (e.g., 'INR')
 * @property {number} total_amount - Total invoice amount
 * @property {number} tax_amount - Tax amount
 * @property {string} summary - AI-generated summary
 * @property {Object} extracted_json - Raw extracted JSON from Textract
 * @property {string} s3_path - S3 storage path
 * @property {string} status - 'processing' | 'completed' | 'failed'
 * @property {string} created_at - ISO timestamp
 * @property {LineItem[]} line_items - Invoice line items
 */

/**
 * @typedef {Object} LineItem
 * @property {string} name - Item name or description
 * @property {string} description - Item description
 * @property {number} quantity - Item quantity
 * @property {number} unit_price - Price per unit
 * @property {number} total - Line total
 */

/**
 * @typedef {Object} DashboardStats
 * @property {number} total - Total invoices
 * @property {number} processed - Successfully processed invoices
 * @property {number} failed - Failed invoices
 * @property {number} totalAmount - Total extracted amount
 */

/**
 * @typedef {Object} PaginatedResponse
 * @property {Invoice[]} data - Array of invoices
 * @property {number} total - Total count
 * @property {number} page - Current page
 * @property {number} totalPages - Total number of pages
 */

export {};
