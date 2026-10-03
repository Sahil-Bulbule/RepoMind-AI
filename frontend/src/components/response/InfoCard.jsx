import React from 'react';
import { Info, HelpCircle } from 'lucide-react';

export default function InfoCard({ title = 'Details', children, icon: Icon = Info }) {
  return (
    <div className="my-3 rounded-xl border border-white/[0.08] bg-[#12141e] p-4 border-l-4 border-l-rose-500 shadow-sm">
      <div className="flex items-start gap-3">
        <div className="flex h-6 w-6 shrink-0 items-center justify-center text-rose-400">
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0 flex-1">
          {title && (
            <h4 className="text-xs font-semibold text-slate-100 mb-1">
              {title}
            </h4>
          )}
          <div className="text-xs text-slate-300 leading-relaxed">
            {children}
          </div>
        </div>
      </div>
    </div>
  );
}
