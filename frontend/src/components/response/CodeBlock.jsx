import React, { useState } from 'react';
import { Terminal, Copy, Check, FileCode } from 'lucide-react';

export default function CodeBlock({ language = 'bash', value = '' }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const lines = value.split('\n');

  return (
    <div className="my-3 overflow-hidden rounded-xl border border-white/[0.08] bg-[#0a0b10] text-xs font-mono shadow-[0_6px_24px_rgba(0,0,0,0.4)]">
                             
      <div className="flex items-center justify-between border-b border-white/[0.06] bg-[#12141d] px-3.5 py-2 text-[11px] text-slate-400">
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 mr-1">
            <span className="h-2.5 w-2.5 rounded-full bg-rose-500/70 border border-rose-500" />
            <span className="h-2.5 w-2.5 rounded-full bg-rose-400/70 border border-rose-400" />
            <span className="h-2.5 w-2.5 rounded-full bg-rose-300/50 border border-rose-300/80" />
          </div>
          <div className="flex items-center gap-1 text-slate-300">
            <Terminal className="h-3.5 w-3.5 text-rose-400" />
            <span className="text-slate-200 font-medium">{language || 'code'}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-500">
            {lines.length} {lines.length === 1 ? 'line' : 'lines'}
          </span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1.5 rounded-md border border-white/[0.06] bg-[#181a24] px-2.5 py-1 text-[11px] text-slate-300 transition-colors hover:border-rose-500/30 hover:bg-[#202331] hover:text-white"
            title="Copy code"
          >
            {copied ? (
              <>
                <Check className="h-3 w-3 text-rose-400" />
                <span className="text-rose-400 font-medium">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="h-3 w-3 text-slate-400" />
                <span>Copy</span>
              </>
            )}
          </button>
        </div>
      </div>

                          
      <div className="relative overflow-x-auto p-4 text-[12px] leading-relaxed text-slate-200 selection:bg-rose-500/25 selection:text-white">
        <pre className="font-mono">
          <code>{value}</code>
        </pre>
      </div>
    </div>
  );
}
