import React from 'react';
import {
  FolderGit2,
  Star,
  GitFork,
  ExternalLink,
  MessageSquare,
  FileCode2,
  BookOpen
} from 'lucide-react';

export default function RepoCard({ repo, onSelectRepo, onAskAboutRepo, isIndexing = false }) {
  return (
    <div className="group flex min-h-[250px] flex-col justify-between rounded-2xl border border-rose-100 bg-white p-5 transition-all duration-300 hover:-translate-y-1 hover:border-rose-300 hover:shadow-md shadow-sm">

      <div>
        <div className="mb-3 flex items-start justify-between gap-3">
          <div className="flex min-w-0 items-start gap-3">
            <div className="shrink-0 rounded-xl border border-rose-200 bg-rose-50 p-2 text-rose-500 transition-colors group-hover:border-rose-400 group-hover:bg-rose-100">
              <FolderGit2 className="w-4 h-4" />
            </div>
            <h3 className="min-w-0 break-words pt-0.5 text-sm font-semibold text-gray-800 transition-colors group-hover:text-rose-600">
              {repo.name}
            </h3>
          </div>

          <a
            href={repo.html_url}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0 rounded-lg p-1.5 text-gray-400 transition-colors hover:bg-rose-50 hover:text-rose-500"
            title="Open on GitHub"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        <p className="mb-4 line-clamp-2 min-h-9 break-words text-xs leading-relaxed text-gray-500 font-sans">
          {repo.description || 'No description provided for this repository.'}
        </p>

        <div className="mb-5 flex flex-wrap items-center gap-x-3 gap-y-2 font-mono text-xs text-gray-400">
          {repo.language && (
            <span className="flex items-center gap-1.5 rounded-md border border-rose-200 bg-rose-50 px-2 py-0.5 text-[11px] text-rose-500">
              <span className="h-1.5 w-1.5 rounded-full bg-rose-400"></span>
              {repo.language}
            </span>
          )}

          <div className="flex items-center gap-1">
            <Star className="w-3.5 h-3.5 text-rose-400" />
            <span>{repo.stars}</span>
          </div>

          <div className="flex items-center gap-1">
            <GitFork className="w-3.5 h-3.5 text-gray-400" />
            <span>{repo.forks}</span>
          </div>

          <div className="flex items-center gap-1 text-gray-400">
            <FileCode2 className="w-3.5 h-3.5" />
            <span>{repo.file_count} files</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2 border-t border-rose-100 pt-3.5">
        <button
          onClick={() => onSelectRepo(repo)}
          disabled={isIndexing}
          title={isIndexing ? 'Available when indexing completes' : 'Explore repository'}
          className="flex items-center justify-center gap-1.5 rounded-xl border border-gray-200 bg-gray-50 px-3 py-2 text-xs font-medium text-gray-600 transition-colors hover:border-gray-300 hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <BookOpen className="w-3.5 h-3.5 text-gray-400" />
          <span>Explore</span>
        </button>

        <button
          onClick={() => onAskAboutRepo(repo)}
          disabled={isIndexing}
          title={isIndexing ? 'Available when indexing completes' : 'Ask AI about repository'}
          className="flex items-center justify-center gap-1.5 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs font-semibold text-rose-500 transition-all hover:border-rose-400 hover:bg-rose-100 hover:text-rose-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>Ask AI</span>
        </button>
      </div>
    </div>
  );
}
