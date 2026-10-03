import React from 'react';
import { CheckCircle2, Zap } from 'lucide-react';

export default function FeatureCard({ title, description, icon: Icon = CheckCircle2 }) {
  return (
    <div className="group rounded-xl border border-white/[0.07] bg-[#13151f] p-3.5 transition-all hover:border-rose-500/35 hover:bg-[#171926] shadow-[0_4px_16px_rgba(0,0,0,0.3)]">
      <div className="flex items-start gap-3">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-rose-500/25 bg-rose-500/10 text-rose-400 group-hover:scale-105 group-hover:text-rose-300 transition-all">
          <Icon className="h-4 w-4" />
        </div>
        <div className="min-w-0">
          <h4 className="text-xs font-semibold text-slate-100 group-hover:text-rose-200 transition-colors">
            {title}
          </h4>
          {description && (
            <p className="mt-1 text-xs text-slate-400 leading-relaxed">
              {description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
