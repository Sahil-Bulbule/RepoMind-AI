import React, { useState } from 'react';
import {
  FolderGit2,
  FileCode,
  Binary,
  RotateCw,
  ExternalLink,
  Search,
  Bot,
  Cpu,
  Layers,
  Database
} from 'lucide-react';
import RepoCard from '../components/RepoCard';
import TechBadge from '../components/TechBadge';
import RepoDetailModal from '../components/RepoDetailModal';
import ProfileAvatar from '../components/ProfileAvatar';

export default function DashboardPage({
  username,
  profileData,
  repositories = [],
  onRefresh,
  isRefreshing,
  onOpenChat,
  onOpenSearch
}) {
  const [selectedRepoForModal, setSelectedRepoForModal] = useState(null);

  const handleAskAboutRepo = (repo) => {
    onOpenChat(repo);
  };

  const handleTechClick = (tech) => {
    onOpenSearch(tech);
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 animate-fade-in">

      <div className="relative overflow-hidden rounded-2xl border border-rose-100 bg-white p-6 sm:p-8 shadow-sm">

        <div className="absolute -top-24 -right-24 w-72 h-72 bg-rose-100 rounded-full blur-3xl pointer-events-none opacity-50" />
        <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-rose-50 rounded-full blur-3xl pointer-events-none opacity-50" />

        <div className="relative flex flex-col md:flex-row md:items-center justify-between gap-6">

          <div className="flex items-start sm:items-center gap-5">
            <div className="relative shrink-0">
              <ProfileAvatar
                key={profileData?.avatar_url || username}
                src={profileData?.avatar_url}
                username={username}
                className="h-20 w-20 sm:h-24 sm:w-24 rounded-2xl border border-rose-200 text-xl shadow-sm"
              />
              <span className="absolute -bottom-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-rose-400 ring-2 ring-[#111113]">
                <span className="h-2 w-2 rounded-full bg-white animate-pulse" />
              </span>
            </div>

            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-gray-900">
                  {profileData?.name || username}
                </h1>
                <a
                  href={`https://github.com/${username}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="rounded-lg p-1.5 text-gray-400 transition-colors hover:text-rose-500 hover:bg-rose-50"
                  title="Open GitHub Profile"
                >
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
              <p className="mt-0.5 font-mono text-sm text-rose-500">@{username}</p>
              {profileData?.bio && (
                <p className="mt-2.5 max-w-2xl text-xs sm:text-sm text-gray-500 leading-relaxed font-sans">
                  {profileData.bio}
                </p>
              )}
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-3 shrink-0">
            <button
              onClick={() => onOpenChat(null)}
              className="rose-glow-btn flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold active:scale-95 transition-all"
            >
              <Bot className="w-4 h-4" />
              <span>Ask AI About Profile</span>
            </button>

            <button
              onClick={onRefresh}
              disabled={isRefreshing}
              className="flex items-center gap-2 rounded-xl border border-rose-100 bg-white px-4 py-2.5 text-xs font-medium text-gray-600 transition-colors hover:border-rose-300 hover:bg-rose-50 disabled:opacity-50 shadow-sm"
            >
              <RotateCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-rose-500' : 'text-gray-400'}`} />
              <span>Sync GitHub Data</span>
            </button>
          </div>
        </div>

        <div className="relative mt-8 grid grid-cols-2 gap-3.5 border-t border-rose-100 pt-6 sm:grid-cols-4">
          <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-4 transition-all hover:border-rose-300 hover:bg-rose-50">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1.5">
              <FolderGit2 className="w-3.5 h-3.5 text-rose-400" />
              <span>Public Repos</span>
            </div>
            <p className="text-xl sm:text-2xl font-bold font-mono text-gray-800">
              {profileData?.public_repos || 0}
            </p>
          </div>

          <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-4 transition-all hover:border-rose-300 hover:bg-rose-50">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1.5">
              <Layers className="w-3.5 h-3.5 text-rose-400" />
              <span>Indexed Repos</span>
            </div>
            <p className="text-xl sm:text-2xl font-bold font-mono text-gray-800">
              {profileData?.indexed_repos ?? 0}
            </p>
          </div>

          <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-4 transition-all hover:border-rose-300 hover:bg-rose-50">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1.5">
              <FileCode className="w-3.5 h-3.5 text-rose-400" />
              <span>Files Indexed</span>
            </div>
            <p className="text-xl sm:text-2xl font-bold font-mono text-gray-800">
              {profileData?.total_files || 0}
            </p>
          </div>

          <div className="rounded-xl border border-rose-100 bg-rose-50/50 p-4 transition-all hover:border-rose-300 hover:bg-rose-50">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-mono mb-1.5">
              <Database className="w-3.5 h-3.5 text-rose-400" />
              <span>ChromaDB Chunks</span>
            </div>
            <p className="text-xl sm:text-2xl font-bold font-mono text-gray-800">
              {profileData?.total_chunks || 0}
            </p>
          </div>
        </div>
      </div>

      {profileData?.detected_languages && profileData.detected_languages.length > 0 && (
        <div className="space-y-3.5 rounded-2xl border border-rose-100 bg-white p-5 sm:p-6 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Cpu className="h-4 w-4 text-rose-500" />
              <h3 className="font-mono text-xs font-semibold uppercase tracking-wider text-gray-700">
                Detected Technologies & Languages
              </h3>
            </div>
            <span className="font-mono text-[11px] text-gray-400 hidden sm:inline">
              Click any tech to search codebase
            </span>
          </div>

          <div className="flex flex-wrap gap-2 pt-1">
            {profileData.detected_languages.map((tech, idx) => (
              <TechBadge
                key={idx}
                tech={tech}
                onClick={handleTechClick}
              />
            ))}
          </div>
        </div>
      )}

      <div className="space-y-4">
        {profileData?.status === 'indexing' && (
          <p className="rounded-xl border border-rose-100 bg-rose-50 px-4 py-3 text-xs text-gray-600">
            All public repositories are shown. Code is still being indexed; chat and search will be ready when indexing finishes.
          </p>
        )}
        <div className="flex items-center justify-between">
          <h2 className="flex items-center gap-2 text-base sm:text-lg font-bold text-gray-900">
            <FolderGit2 className="h-5 w-5 text-rose-500" />
            <span>Public Repositories ({repositories.length})</span>
          </h2>
          <span className="text-xs font-mono text-gray-400">
            Sorted by stars
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {repositories.map((repo) => (
            <RepoCard
              key={repo.id}
              repo={repo}
              isIndexing={profileData?.status === 'indexing'}
              onSelectRepo={(r) => setSelectedRepoForModal(r)}
              onAskAboutRepo={handleAskAboutRepo}
            />
          ))}
        </div>
      </div>

      {selectedRepoForModal && (
        <RepoDetailModal
          username={username}
          repo={selectedRepoForModal}
          onClose={() => setSelectedRepoForModal(null)}
          onAskAboutRepo={handleAskAboutRepo}
        />
      )}
    </div>
  );
}
