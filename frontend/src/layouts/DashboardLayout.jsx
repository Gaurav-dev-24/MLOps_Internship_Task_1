import { Outlet } from 'react-router-dom';
import { Sidebar } from '../components/layout';
import { Navbar } from '../components/layout';

/**
 * Main dashboard layout with sidebar + navbar + content area.
 */
export default function DashboardLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-gray-950">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-y-auto">
          <div className="mx-auto max-w-7xl px-4 py-6 lg:px-8 lg:py-8">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
