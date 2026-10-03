import React from 'react';
import { AlertTriangle, AlertOctagon } from 'lucide-react';

export default function WarningCard({ title = 'Important Notice', children }) {
  return (
    <div className="my-3 rounded-xl border border-rose-600/40 bg-rose-950/20 p-4 shadow-[0_4px_20px_rgba(225,29,72,0.1)]">
      <div className="flex items-start gap-3">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-rose-500/40 bg-rose-500/15 text-rose-400">
          <AlertTriangle className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          <h4 className="text-xs font-semibold uppercase tracking-wider text-rose-300">
            {title}
          </h4>
          <div className="mt-1 text-xs text-rose-100/90 leading-relaxed">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
