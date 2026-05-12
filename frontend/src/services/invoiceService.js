import { apiClient } from '../api';

/**
 * Invoice service — handles all invoice-related API calls.
 */
const invoiceService = {
  /**
   * Fetch all invoices with optional filters.
   * @param {Object} params — { page, limit, status, search, startDate, endDate }
   * @returns {Promise<{ data: Array, total: number, page: number, totalPages: number }>}
   */
  getAll(params = {}) {
    return apiClient.get('/invoices', { params });
  },

  /**
   * Fetch a single invoice by ID.
   * @param {string} invoiceId
   * @returns {Promise<Object>}
   */
  getById(invoiceId) {
    return apiClient.get(`/invoice/${invoiceId}`);
  },

  /**
   * Fetch dashboard stats.
   * @returns {Promise<{ total: number, processed: number, failed: number, totalAmount: number }>}
   */
  getStats() {
    return apiClient.get('/invoices/stats');
  },

  /**
   * Fetch recent invoices for the dashboard.
   * @param {number} limit
   * @returns {Promise<Array>}
   */
  getRecent(limit = 5) {
    return apiClient.get('/invoices', { params: { limit, sort: 'created_at:desc' } });
  },
};

export default invoiceService;
