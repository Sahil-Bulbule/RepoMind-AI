import React, { useState } from 'react';
import { 
  Search, 
  Loader2, 
  FolderGit2,
  ExternalLink, 
  MessageSquare,
  FileSearch,
  AlertCircle,
} from 'lucide-react';
import { api } from '../services/api';

const QUICK_SEARCH_TERMS = [
  "authentication",
  "database connection",
  "FastAPI",
  "React hooks",
  "machine learning",
  "docker"
];

function groupRepositoryResults(results, username) {
  const repositoriesByName = new Map();

  for (const item of results) {
    if (!item?.repository_name) continue;

    const key = item.repository_name.trim().toLocaleLowerCase();
    let repository = repositoriesByName.get(key);
    if (!repository) {
      repository = {
        ...item,
        repository_full_name: item.repository_full_name || `${username}/${item.repository_name}`,
        html_url: item.html_url || `https://github.com/${username}/${item.repository_name}`,
        matching_files: Number.isFinite(item.matching_files) ? item.matching_files : 0,
        evidence_by_path: new Map(),
      };
      repositoriesByName.set(key, repository);
    }

    repository.score = Math.max(repository.score || 0, item.score || 0);
    repository.description ||= item.description;
    repository.language ||= item.language;
    repository.html_url ||= item.html_url;
    repository.matching_files = Math.max(
      repository.matching_files,
      Number.isFinite(item.matching_files) ? item.matching_files : 0,
    );

    const evidenceFiles = Array.isArray(item.evidence_files)
      ? item.evidence_files
      : item.file_path
        ? [{
          file_path: item.file_path,
          source_url: item.source_url || '',
          language: item.language || 'Code',
          score: item.score || 0,
        }]
        : [];

    for (const file of evidenceFiles) {
      if (!file?.file_path) continue;
      const evidenceKey = file.file_path.toLocaleLowerCase();
      const existing = repository.evidence_by_path.get(evidenceKey);
      if (!existing || (file.score || 0) > (existing.score || 0)) {
        repository.evidence_by_path.set(evidenceKey, file);
      }
    }
  }

  return [...repositoriesByName.values()]
    .map((repository) => {
      const evidence_files = [...repository.evidence_by_path.values()]
        .sort((left, right) => (right.score || 0) - (left.score || 0))
        .slice(0, 3);
      return {
        ...repository,
        matching_files: Math.max(repository.matching_files, repository.evidence_by_path.size),
        evidence_files,
      };
    })
    .sort((left, right) => right.score - left.score);
}

export default function SearchModal({ 
  username, 
  repositories = [], 
  initialQuery = '',
  onAskAboutRepository
}) {
  const [query, setQuery] = useState(initialQuery);
  const [selectedRepo, setSelectedRepo] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleSearch = async (overrideQuery) => {
    const q = (overrideQuery !== undefined ? overrideQuery : query).trim();
    if (!q || isLoading) return;

    if (overrideQuery !== undefined) {
      setQuery(overrideQuery);
    }

    setIsLoading(true);
    setHasSearched(true);
    setErrorMessage('');

    try {
      const data = await api.search(
        username,
        q,
        selectedRepo || null,
        3
      );
      setResults(groupRepositoryResults(data.results || [], username));
    } catch (err) {
      console.error('Search error:', err);
      setResults([]);
      setErrorMessage(err.message || 'Search failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 animate-fade-in">
      
                                   
      <div className="glass-panel p-6 sm:p-7 rounded-2xl border border-white/[0.08] bg-[#0d0f17]/95 shadow-2xl space-y-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Search className="w-5 h-5 text-rose-400" />
            <h2 className="text-xl font-bold tracking-tight text-white">
              Find relevant repositories
            </h2>
          </div>
          <p className="text-xs text-slate-400 font-sans">
            Search for exact keywords in indexed source files. Results show only repositories with matching content.
          </p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSearch();
          }}
          className="flex flex-col sm:flex-row gap-2.5"
        >
          <div className="flex-1 relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. JWT authentication, database migration, CNN architecture..."
              className="w-full rounded-xl border border-white/[0.08] bg-[#131522] px-4 py-3 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-rose-500/60 focus:ring-2 focus:ring-rose-500/20 transition-all font-sans"
            />
          </div>

                                      
          <div className="sm:w-56 relative">
            <select
              value={selectedRepo}
              onChange={(e) => setSelectedRepo(e.target.value)}
              className="w-full appearance-none rounded-xl border border-white/[0.08] bg-[#131522] px-3.5 py-3 text-xs text-slate-200 focus:outline-none focus:border-rose-500/60 font-mono"
            >
              <option value="">All Repositories</option>
              {repositories.map((r) => (
                <option key={r.id} value={r.name}>
                  {r.name}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={!query.trim() || isLoading}
            className="rose-glow-btn flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold text-xs disabled:opacity-40 transition-all shrink-0 active:scale-95"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Search className="w-4 h-4" />
            )}
            <span>Search</span>
          </button>
        </form>

                                  
        <div className="flex flex-wrap items-center gap-2 pt-1 border-t border-white/[0.04]">
          <span className="text-[11px] font-mono text-slate-400">Quick ideas:</span>
          {QUICK_SEARCH_TERMS.map((term, idx) => (
            <button
              key={idx}
              onClick={() => handleSearch(term)}
              className="px-2.5 py-1 rounded-lg border border-white/[0.06] bg-[#141624] text-[11px] font-mono text-slate-300 hover:border-rose-500/40 hover:text-rose-200 transition-colors"
            >
              {term}
            </button>
          ))}
        </div>
      </div>

                          
      <div className="space-y-3">
        {isLoading ? (
          <div className="glass-panel p-12 rounded-2xl border border-white/[0.08] bg-[#0e1018] flex flex-col items-center justify-center text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin text-rose-400 mb-3" />
            <p className="text-xs font-mono">Finding repositories related to your search...</p>
          </div>
        ) : results.length > 0 ? (
          <div className="space-y-3">
            <p className="text-xs font-mono text-slate-400 px-1">
              Found <strong className="text-rose-300">{results.length}</strong> related {results.length === 1 ? 'repository' : 'repositories'}:
            </p>
            {results.map((repository) => (
              <div
                key={repository.repository_full_name || repository.repository_name}
                className="glass-card p-5 rounded-xl border border-white/[0.08] bg-[#0e1018] hover:border-rose-500/35 transition-all space-y-4 group"
              >
                <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <FolderGit2 className="w-4 h-4 text-rose-400 shrink-0" />
                      <h3 className="font-semibold text-sm text-slate-100">
                        {repository.repository_full_name || repository.repository_name}
                      </h3>
                      {repository.language && (
                        <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300 font-mono">
                          {repository.language}
                        </span>
                      )}
                      <span className="px-2 py-0.5 rounded border border-rose-500/30 bg-rose-500/10 text-rose-300 text-[10px] font-mono">
                        {Math.round(repository.score * 100)}% relevance
                      </span>
                    </div>
                    {repository.description && (
                      <p className="mt-2 text-xs text-slate-400 leading-relaxed">
                        {repository.description}
                      </p>
                    )}
                  </div>

                  <div className="flex items-center gap-3 shrink-0">
                    {onAskAboutRepository && (
                      <button
                        onClick={() => onAskAboutRepository(repository.repository_name)}
                        className="flex items-center gap-1 text-xs font-mono text-rose-300 hover:text-white"
                      >
                        <MessageSquare className="w-3 h-3" />
                        <span>Ask about repo</span>
                      </button>
                    )}
                    {repository.html_url && (
                      <a
                        href={repository.html_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-1 text-xs font-mono text-slate-400 hover:text-rose-300"
                      >
                        <span>Open repo</span>
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    )}
                  </div>
                </div>

                <div className="rounded-lg border border-white/[0.06] bg-[#101119] p-3.5">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-200">
                    <FileSearch className="w-3.5 h-3.5 text-rose-400" />
                    Why this repository matched
                  </div>
                  <p className="mt-1.5 text-xs text-slate-400">
                    Your search terms were found in {repository.matching_files} indexed {repository.matching_files === 1 ? 'file' : 'files'}.
                  </p>
                  <ul className="mt-2 flex flex-wrap gap-2">
                    {repository.evidence_files.map((file) => (
                      <li key={file.file_path}>
                        {file.source_url ? (
                          <a
                            href={file.source_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-flex max-w-full items-center gap-1 rounded-md border border-white/[0.08] bg-[#171923] px-2 py-1 font-mono text-[10px] text-slate-300 hover:border-rose-500/40 hover:text-rose-200"
                          >
                            <span className="truncate">{file.file_path}</span>
                            <ExternalLink className="h-3 w-3 shrink-0" />
                          </a>
                        ) : (
                          <span className="inline-flex max-w-full rounded-md border border-white/[0.08] bg-[#171923] px-2 py-1 font-mono text-[10px] text-slate-300">
                            {file.file_path}
                          </span>
                        )}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        ) : hasSearched ? (
          <div className="glass-panel p-12 rounded-2xl border border-white/[0.08] bg-[#0e1018] text-center text-slate-400">
            {errorMessage ? (
              <>
                <AlertCircle className="mx-auto mb-3 h-5 w-5 text-rose-400" />
                <p className="text-sm font-medium text-rose-200">{errorMessage}</p>
              </>
            ) : (
              <>
                <p className="text-sm font-medium text-slate-200">No related repositories found.</p>
                <p className="text-xs font-mono mt-1 text-slate-400">
              Try searching with different keywords or clearing the repository filter.
                </p>
              </>
            )}
          </div>
        ) : null}
      </div>
    </div>
  );
}
