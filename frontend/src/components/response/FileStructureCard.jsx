import React from 'react';
import { Folder, FileCode, ChevronRight, FileText, Settings, Database } from 'lucide-react';

function getFileIcon(path = '') {
  if (path.endsWith('/') || !path.includes('.')) {
    return <Folder className="h-3.5 w-3.5 text-rose-400 shrink-0" />;
  }
  if (path.endsWith('.py') || path.endsWith('.js') || path.endsWith('.jsx') || path.endsWith('.ts') || path.endsWith('.tsx')) {
    return <FileCode className="h-3.5 w-3.5 text-rose-300 shrink-0" />;
  }
  if (path.endsWith('.json') || path.endsWith('.yaml') || path.endsWith('.yml') || path.endsWith('.env')) {
    return <Settings className="h-3.5 w-3.5 text-rose-300 shrink-0" />;
  }
  if (path.endsWith('.sql') || path.includes('db')) {
    return <Database className="h-3.5 w-3.5 text-rose-300 shrink-0" />;
  }
  return <FileText className="h-3.5 w-3.5 text-slate-400 shrink-0" />;
}

export default function FileStructureCard({ items = [] }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="my-3 overflow-hidden rounded-xl border border-white/[0.08] bg-[#0c0d13]">
      <div className="flex items-center justify-between border-b border-white/[0.06] bg-[#12141d] px-3.5 py-2 text-[11px] font-mono text-slate-400">
        <span className="flex items-center gap-1.5 text-slate-300 font-medium">
          <Folder className="h-3.5 w-3.5 text-rose-400" />
          Project File Tree & Structure
        </span>
        <span className="text-[10px] text-slate-500">{items.length} items</span>
      </div>

      <div className="divide-y divide-white/[0.04] p-1 font-mono text-xs">
        {items.map((item, idx) => {
          const path = typeof item === 'string' ? item : item.path || item.name;
          const desc = typeof item === 'object' ? item.description : null;

          return (
            <div
              key={idx}
              className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 sm:gap-4 px-3 py-2 hover:bg-[#161824] rounded-lg transition-colors"
            >
              <div className="flex items-center gap-2 min-w-0">
                {getFileIcon(path)}
                <span className="font-mono text-xs text-rose-200 truncate">
                  {path}
                </span>
              </div>
              {desc && (
                <span className="text-[11px] text-slate-400 font-sans sm:text-right line-clamp-1">
                  {desc}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
