import React from 'react';
import { Shield, Terminal } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="mt-auto w-full border-t border-rose-500/30 bg-[#111113] px-4 py-4 font-mono text-xs text-slate-300 sm:px-6 lg:px-8">
      <div className="mx-auto flex max-w-7xl flex-col items-center justify-between gap-3 sm:flex-row">

        <div className="flex items-center gap-2">
          <span className="font-semibold text-rose-400">Ask My GitHub</span>
          <span className="text-slate-500">|</span>
          <span className="text-slate-300">RAG Engine</span>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[11px]">
          <span className="flex items-center gap-1.5 text-slate-300">
            <Shield className="h-3.5 w-3.5 text-rose-400" />
            GitHub Intelligence
          </span>
          <span className="text-slate-500">|</span>
          <span className="text-rose-400">Real-Time Repository Analysis</span>
        </div>
      </div>
    </footer>
  );
}
