import React from 'react';
import { Lightbulb } from 'lucide-react';

export default function TipCard({ title = 'Developer Pro-Tip', children }) {
  return (
    <div className="my-3 rounded-xl border border-rose-500/25 bg-gradient-to-r from-rose-950/20 to-[#141622] p-4 shadow-[0_4px_20px_rgba(244,63,94,0.08)]">
      <div className="flex items-start gap-3">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-rose-400/30 bg-rose-500/10 text-rose-300">
          <Lightbulb className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-300">
            {title}
          </h4>
          <div className="mt-1 text-xs text-slate-300 leading-relaxed">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
