import React, { useState } from 'react';
import {
  FileCode2,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  Check,
  Copy
} from 'lucide-react';

export default function SourceCard({ source }) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleCopySnippet = (e) => {
    e.stopPropagation();
    if (!source.snippet) return;
    navigator.clipboard.writeText(source.snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="overflow-hidden rounded-xl border border-rose-100 bg-white text-xs transition-all duration-200 hover:border-rose-300 hover:shadow-sm shadow-sm">
      <div
        onClick={() => source.snippet && setIsExpanded(!isExpanded)}
        className={`flex items-center justify-between gap-3 p-3 select-none ${
          source.snippet ? 'cursor-pointer hover:bg-rose-50/50' : ''
        }`}
      >
        <div className="flex min-w-0 items-center gap-2">
          <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-rose-200 bg-rose-50 text-rose-500">
            <FileCode2 className="h-3.5 w-3.5" />
          </div>
          <span className="truncate font-mono font-medium text-gray-700">
            {source.file_path}
          </span>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {source.source_url && (
            <a
              href={source.source_url}
              target="_blank"
              rel="noopener noreferrer"
              onClick={(e) => e.stopPropagation()}
              className="flex shrink-0 items-center gap-1 font-mono text-[11px] text-rose-500 hover:text-rose-700 transition-colors"
              title="Open source file on GitHub"
            >
              <span>GitHub</span>
              <ExternalLink className="h-3 w-3" />
            </a>
          )}

          {source.snippet && (
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1 rounded-md text-gray-400 hover:text-rose-500 hover:bg-rose-50 transition-colors"
              title={isExpanded ? 'Collapse snippet' : 'Expand snippet'}
            >
              {isExpanded ? <ChevronUp className="h-3.5 w-3.5" /> : <ChevronDown className="h-3.5 w-3.5 text-rose-400" />}
            </button>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between gap-3 border-t border-rose-100 bg-rose-50/30 px-3 py-1.5 font-mono text-[10px] text-gray-400">
        <span className="truncate">
          {source.repository_full_name || source.repository_name}
        </span>
        <span className="shrink-0 rounded bg-rose-100 px-1.5 py-0.5 text-rose-500">
          {source.language || 'File'}
        </span>
      </div>

      {isExpanded && source.snippet && (
        <div className="relative border-t border-rose-100 bg-gray-50 p-3">
          <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-rose-100 text-[10px] font-mono text-gray-400">
            <span>Source Context</span>
            <button
              onClick={handleCopySnippet}
              className="flex items-center gap-1 text-gray-400 hover:text-rose-500 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3 text-rose-500" />
                  <span className="text-rose-500">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
          <pre className="overflow-x-auto whitespace-pre font-mono text-[11px] leading-relaxed text-gray-700 selection:bg-rose-100">
            <code>{source.snippet}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
