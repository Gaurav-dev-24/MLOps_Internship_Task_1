import { createBrowserRouter } from 'react-router-dom';
import { DashboardLayout } from '../layouts';
import Dashboard from '../pages/Dashboard';
import Upload from '../pages/Upload';
import InvoiceDetails from '../pages/InvoiceDetails';
import History from '../pages/History';

/**
 * Application router configuration.
 */
const router = createBrowserRouter([
  {
    element: <DashboardLayout />,
    children: [
      { path: '/', element: <Dashboard /> },
      { path: '/upload', element: <Upload /> },
      { path: '/invoice/:id', element: <InvoiceDetails /> },
      { path: '/history', element: <History /> },
    ],
  },
]);

export default router;
