import React from 'react';
import { Terminal } from 'lucide-react';

export default function TechBadge({ tech, onClick }) {
  return (
    <button
      onClick={() => onClick && onClick(tech)}
      className="group flex items-center gap-1.5 rounded-lg border border-rose-200 bg-rose-50 px-3 py-1.5 text-xs font-mono font-medium text-rose-500 transition-all duration-150 hover:border-rose-400 hover:bg-rose-100 hover:scale-[1.02] active:scale-[0.98]"
      title={`Search code using ${tech}`}
    >
      <Terminal className="w-3 h-3 opacity-60 group-hover:opacity-100" />
      <span>{tech}</span>
    </button>
  );
}
