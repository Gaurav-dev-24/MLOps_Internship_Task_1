import { useState, useEffect, useCallback, useRef } from 'react';
import { invoiceService } from '../services';

/**
 * Custom hook for fetching invoices with filtering and pagination.
 */
export default function useInvoices(initialParams = {}) {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [params, setParams] = useState({
    page: 1,
    limit: 10,
    status: '',
    search: '',
    startDate: '',
    endDate: '',
    ...initialParams,
  });
  const [pagination, setPagination] = useState({
    total: 0,
    page: 1,
    totalPages: 1,
  });

  const fetchInvoices = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      const cleanParams = Object.fromEntries(
        Object.entries(params).filter(([, v]) => v !== '' && v != null),
      );

      const result = await invoiceService.getAll(cleanParams);
      const data = result?.data || result || [];
      setInvoices(Array.isArray(data) ? data : []);
      setPagination({
        total: result.total || 0,
        page: result.page || 1,
        totalPages: result.totalPages || 1,
      });
    } catch (err) {
      setError(err.message);
      setInvoices([]);
    } finally {
      setLoading(false);
    }
  }, [params]);

  // ✅ Fix: useRef se track karo, direct call nahi
  const fetchRef = useRef(fetchInvoices);
  useEffect(() => {
    fetchRef.current = fetchInvoices;
  }, [fetchInvoices]);

  useEffect(() => {
    fetchRef.current();
  }, [params]);  // ← fetchInvoices nahi, params pe depend karo

  const updateParams = useCallback((newParams) => {
    setParams((prev) => ({ ...prev, ...newParams, page: newParams.page || 1 }));
  }, []);

  const goToPage = useCallback((page) => {
    setParams((prev) => ({ ...prev, page }));
  }, []);

  return { invoices, loading, error, pagination, params, updateParams, goToPage, refetch: fetchInvoices };
}