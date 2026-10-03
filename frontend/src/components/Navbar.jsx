import React from 'react';
import GithubIcon from './GithubIcon';
import ProfileAvatar from './ProfileAvatar';
import {
  Bot,
  FolderGit2,
  Layers,
  LogOut,
  RotateCw,
  Search
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Overview', icon: Layers },
  { id: 'chat', label: 'AI Chat', icon: Bot },
  { id: 'repositories', label: 'Repositories', icon: FolderGit2 },
  { id: 'search', label: 'Code Search', icon: Search },
];

export default function Navbar({
  currentUsername,
  profileData,
  currentView,
  setCurrentView,
  onResetProfile,
  onRefreshProfile,
  isRefreshing,
}) {
  return (
    <header className="sticky top-0 z-40 w-full border-b border-rose-100 bg-white shadow-sm">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">

        <button
          type="button"
          onClick={() => currentUsername && setCurrentView('dashboard')}
          className="group flex min-w-0 items-center gap-3 text-left focus:outline-none"
        >
          <div className="relative flex h-10 w-10 shrink-0 items-center justify-center rounded-xl border border-rose-200 bg-rose-50 text-rose-500 transition-all duration-300 group-hover:border-rose-400 group-hover:bg-rose-100">
            <GithubIcon className="h-5 w-5" />
            <span className="absolute -top-0.5 -right-0.5 h-2.5 w-2.5 rounded-full bg-rose-500 ring-2 ring-white" />
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="truncate text-base font-bold tracking-tight text-rose-400 sm:text-lg">
                RepoMind AI
              </span>
            </div>
            <span className="hidden font-mono text-[11px] text-gray-400 sm:block">
              AI-Powered GitHub Repository Intelligence
            </span>
          </div>
        </button>

        {currentUsername && (
          <nav aria-label="Main navigation" className="hidden items-center gap-1 rounded-xl border border-rose-100 bg-rose-50/50 p-1 lg:flex">
            {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
              const isActive = currentView === id;
              return (
                <button
                  key={id}
                  type="button"
                  onClick={() => setCurrentView(id)}
                  aria-current={isActive ? 'page' : undefined}
                  className={`relative flex items-center gap-2 rounded-lg px-3.5 py-1.5 text-xs font-medium transition-all ${
                    isActive
                      ? 'bg-rose-500 text-white shadow-sm'
                      : 'text-gray-500 hover:bg-white hover:text-gray-800 hover:shadow-sm'
                  }`}
                >
                  <Icon className={`h-3.5 w-3.5 ${isActive ? 'text-white' : 'text-gray-400'}`} />
                  <span>{label}</span>
                </button>
              );
            })}
          </nav>
        )}

        <div className="flex shrink-0 items-center gap-2 sm:gap-3">
          {currentUsername ? (
            <>
              <div className="hidden items-center gap-2 rounded-xl border border-rose-100 bg-rose-50 px-3 py-1.5 sm:flex">
                <ProfileAvatar
                  key={profileData?.avatar_url || currentUsername}
                  src={profileData?.avatar_url}
                  username={currentUsername}
                  className="h-6 w-6 rounded-full border border-rose-200 text-[10px]"
                />
                <span className="max-w-32 truncate font-mono text-xs font-medium text-rose-500">
                  @{currentUsername}
                </span>
              </div>

              <button
                type="button"
                onClick={onRefreshProfile}
                disabled={isRefreshing}
                title="Re-index and refresh GitHub data"
                className="flex items-center gap-1.5 rounded-xl border border-rose-100 bg-white p-2 text-gray-500 transition-all hover:border-rose-300 hover:bg-rose-50 hover:text-rose-500 disabled:opacity-50 shadow-sm"
              >
                <RotateCw className={`h-4 w-4 ${isRefreshing ? 'animate-spin text-rose-500' : ''}`} />
              </button>

              <button
                type="button"
                onClick={onResetProfile}
                title="Switch GitHub profile"
                className="flex items-center gap-1.5 rounded-xl border border-rose-100 bg-white p-2 text-gray-500 transition-all hover:border-rose-300 hover:bg-rose-50 hover:text-rose-500 shadow-sm"
              >
                <LogOut className="h-4 w-4" />
              </button>
            </>
          ) : null}
        </div>
      </div>

      {currentUsername && (
        <nav aria-label="Mobile navigation" className="grid grid-cols-4 border-t border-rose-100 bg-white px-2 py-1.5 lg:hidden">
          {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
            const isActive = currentView === id;
            return (
              <button
                key={id}
                type="button"
                onClick={() => setCurrentView(id)}
                aria-current={isActive ? 'page' : undefined}
                className={`flex min-w-0 flex-col items-center gap-1 rounded-lg px-1 py-1.5 text-[10px] transition-colors ${
                  isActive ? 'text-rose-500 font-semibold bg-rose-50' : 'text-gray-400 hover:text-gray-700'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span className="max-w-full truncate">{label}</span>
              </button>
            );
          })}
        </nav>
      )}
    </header>
  );
}