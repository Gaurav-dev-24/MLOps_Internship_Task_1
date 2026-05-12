import { createContext, useState, useCallback } from 'react';

export const AppContext = createContext(null);

/**
 * Global application context provider.
 * Provides sidebar state and global notifications.
 */
export function AppProvider({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notification, setNotification] = useState(null);

  const toggleSidebar = useCallback(() => {
    setSidebarOpen((prev) => !prev);
  }, []);

  const closeSidebar = useCallback(() => {
    setSidebarOpen(false);
  }, []);

  const notify = useCallback((message, type = 'info') => {
    setNotification({ message, type });

    setTimeout(() => {
      setNotification(null);
    }, 4000);
  }, []);

  return (
    <AppContext.Provider
      value={{
        sidebarOpen,
        toggleSidebar,
        closeSidebar,
        notification,
        notify,
      }}
    >
      {children}
    </AppContext.Provider>
  );
}