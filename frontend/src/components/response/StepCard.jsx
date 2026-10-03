import React from 'react';

export default function StepCard({ number = 1, title, children }) {
  return (
    <div className="group my-2 flex items-start gap-3.5 rounded-xl border border-white/[0.06] bg-[#11131c] p-3.5 transition-all hover:border-rose-500/30 hover:bg-[#151724]">
      <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-rose-500/30 bg-rose-500/10 font-mono text-xs font-bold text-rose-300 group-hover:scale-105 group-hover:bg-rose-500 group-hover:text-white transition-all shadow-[0_0_10px_rgba(244,63,94,0.15)]">
        {number}
      </div>
      <div className="min-w-0 flex-1">
        {title && (
          <h4 className="text-xs font-semibold text-slate-100 group-hover:text-rose-200 transition-colors mb-1">
            {title}
          </h4>
        )}
        <div className="text-xs text-slate-300 leading-relaxed">
          {children}
        </div>
      </div>
    </div>
  );
}
