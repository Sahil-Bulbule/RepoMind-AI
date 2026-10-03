import React from 'react';

export default function SummaryCard({ title = 'Executive Summary', children }) {
  return (
    <div className="relative my-4 overflow-hidden rounded-xl border border-rose-500/30 bg-gradient-to-br from-[#18121a] to-[#0e1017] p-4.5 sm:p-5 shadow-[0_8px_30px_rgba(225,29,72,0.1)]">
      <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-rose-500 to-transparent opacity-80" />
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs font-mono font-semibold uppercase tracking-wider text-rose-300">
          {title}
        </span>
      </div>
      <div className="text-sm text-slate-200 leading-relaxed font-sans">
        {children}
      </div>
    </div>
  );
}
