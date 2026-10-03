import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  X, 
  ExternalLink, 
  FileCode, 
  BookOpen, 
  MessageSquare, 
  Loader2, 
  Star, 
  GitFork 
} from 'lucide-react';
import { api } from '../services/api';
import CodeBlock from './response/CodeBlock';

export default function RepoDetailModal({ 
  username, 
  repo, 
  onClose, 
  onAskAboutRepo 
}) {
  const [activeTab, setActiveTab] = useState('readme');
  const [detailData, setDetailData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDetail() {
      try {
        setLoading(true);
        const data = await api.getRepositoryDetail(username, repo.name);
        setDetailData(data);
      } catch (err) {
        console.error('Failed to load repo detail:', err);
      } finally {
        setLoading(false);
      }
    }
    if (username && repo) {
      fetchDetail();
    }
  }, [username, repo]);

  if (!repo) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fade-in">
      <div className="w-full max-w-4xl max-h-[85vh] glass-panel rounded-2xl border border-white/[0.08] bg-[#0c0e16] flex flex-col shadow-[0_25px_70px_rgba(0,0,0,0.85)] overflow-hidden">
        
                      
        <div className="p-6 border-b border-white/[0.06] bg-[#11131e]/90 flex items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <h2 className="text-xl font-bold tracking-tight text-white">{repo.name}</h2>
              <a
                href={repo.html_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs font-mono text-rose-300 hover:text-rose-100"
              >
                <span>GitHub</span>
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <p className="text-xs text-slate-400 mt-1 max-w-2xl font-sans">
              {repo.description || 'No description provided.'}
            </p>
            <div className="flex items-center gap-4 text-xs font-mono text-slate-400 mt-3">
              <span className="flex items-center gap-1">
                <Star className="w-3.5 h-3.5 text-rose-400" />
                {repo.stars}
              </span>
              <span className="flex items-center gap-1">
                <GitFork className="w-3.5 h-3.5 text-slate-400" />
                {repo.forks}
              </span>
              <span>Default branch: <strong className="text-slate-300">{repo.default_branch}</strong></span>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                onClose();
                onAskAboutRepo(repo);
              }}
              className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl border border-rose-500/40 bg-rose-500/10 hover:bg-rose-500/20 text-xs font-semibold text-rose-200 transition-colors"
            >
              <MessageSquare className="w-3.5 h-3.5 text-rose-400" />
              <span>Ask about repo</span>
            </button>

            <button
              onClick={onClose}
              className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-white/[0.06] transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

                            
        <div className="flex items-center gap-2 px-6 pt-2 border-b border-white/[0.06] bg-[#0f111a]">
          <button
            onClick={() => setActiveTab('readme')}
            className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-xs font-medium transition-all ${
              activeTab === 'readme'
                ? 'border-rose-500 text-rose-300 font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <BookOpen className="w-4 h-4" />
            README.md
          </button>
          <button
            onClick={() => setActiveTab('files')}
            className={`flex items-center gap-2 px-4 py-2.5 border-b-2 text-xs font-medium transition-all ${
              activeTab === 'files'
                ? 'border-rose-500 text-rose-300 font-semibold'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCode className="w-4 h-4" />
            Indexed Files ({detailData?.important_files?.length || repo.file_count})
          </button>
        </div>

                            
        <div className="flex-1 overflow-y-auto p-6 bg-[#090a10]">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-16 text-slate-400">
              <Loader2 className="w-8 h-8 animate-spin text-rose-400 mb-3" />
              <p className="text-xs font-mono">Loading repository data...</p>
            </div>
          ) : activeTab === 'readme' ? (
            detailData?.readme_content ? (
              <div className="prose-custom text-sm">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    code({ node, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return match ? (
                        <CodeBlock language={match[1]} value={String(children).replace(/\n$/, '')} />
                      ) : (
                        <code className={className} {...props}>{children}</code>
                      );
                    }
                  }}
                >
                  {detailData.readme_content}
                </ReactMarkdown>
              </div>
            ) : (
              <div className="text-center py-16 text-slate-400 text-xs font-mono">
                No README.md found in this repository.
              </div>
            )
          ) : (
            <div className="space-y-2">
              {detailData?.important_files && detailData.important_files.length > 0 ? (
                detailData.important_files.map((file, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-xl border border-white/[0.06] bg-[#10121d] text-xs font-mono hover:border-rose-500/30 transition-colors"
                  >
                    <div className="flex items-center gap-2.5 truncate max-w-lg">
                      <FileCode className="w-4 h-4 text-rose-400 shrink-0" />
                      <span className="text-slate-200 truncate">{file.file_path}</span>
                    </div>

                    <div className="flex items-center gap-4 shrink-0">
                      <span className="text-[11px] text-slate-400">
                        {Math.round(file.size / 1024)} KB
                      </span>
                      <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-slate-300">
                        {file.language || 'Code'}
                      </span>
                      <a
                        href={file.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-rose-300 hover:text-rose-100"
                        title="View on GitHub"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-16 text-slate-400 text-xs font-mono">
                  No source files indexed for this repository.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
