import { RouterProvider } from 'react-router-dom';
import { AppProvider } from './context';
import router from './routes';

/**
 * Root application component.
 */
export default function App() {
  return (
    <AppProvider>
      <RouterProvider router={router} />
    </AppProvider>
  );
}
