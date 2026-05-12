import { useApp } from '../../context';

/**
 * Top navigation bar with mobile hamburger toggle.
 */
export default function Navbar() {
  const { toggleSidebar, notification } = useApp();

  return (
    <header id="navbar" className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-gray-800 bg-gray-950/80 backdrop-blur-lg px-4 lg:px-8">
      {/* Mobile hamburger */}
      <button
        onClick={toggleSidebar}
        className="rounded-lg p-2 text-gray-400 transition-colors hover:bg-gray-800 hover:text-gray-200 lg:hidden"
        id="mobile-menu-btn"
        aria-label="Toggle navigation"
      >
        <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
        </svg>
      </button>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Notification toast */}
      {notification && (
        <div
          className={`animate-slide-up rounded-lg px-4 py-2 text-sm font-medium ${
            notification.type === 'error'
              ? 'bg-red-500/10 text-red-400 ring-1 ring-red-500/20'
              : notification.type === 'success'
                ? 'bg-emerald-500/10 text-emerald-400 ring-1 ring-emerald-500/20'
                : 'bg-brand-500/10 text-brand-400 ring-1 ring-brand-500/20'
          }`}
        >
          {notification.message}
        </div>
      )}

      {/* Search (decorative placeholder) */}
      <div className="hidden items-center gap-2 rounded-lg bg-gray-900 px-3 py-2 text-sm text-gray-500 ring-1 ring-gray-800 md:flex">
        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
          <path strokeLinecap="round" strokeLinejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
        <span>Search…</span>
        <kbd className="ml-4 rounded bg-gray-800 px-1.5 py-0.5 text-[11px] font-medium text-gray-500">⌘K</kbd>
      </div>

      {/* Avatar */}
      <div className="h-8 w-8 rounded-full bg-gradient-to-br from-brand-400 to-purple-500 ring-2 ring-gray-800" />
    </header>
  );
}
