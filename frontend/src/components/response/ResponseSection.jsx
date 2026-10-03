import React, { useState } from 'react';
import { Copy, Check, ChevronDown, ChevronUp } from 'lucide-react';

export default function ResponseSection({
  icon: Icon,
  emoji,
  title,
  badge,
  badgeVariant = 'rose',
  children,
  defaultExpanded = true,
  collapsible = false,
  rawText = '',
}) {
  const [expanded, setExpanded] = useState(defaultExpanded);
  const [copied, setCopied] = useState(false);

  const handleCopySection = (e) => {
    e.stopPropagation();
    if (!rawText) return;
    navigator.clipboard.writeText(rawText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const badgeStyles = {
    rose: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
    crimson: 'border-rose-700/40 bg-rose-950/40 text-rose-200',
    slate: 'border-white/[0.1] bg-white/[0.04] text-slate-300',
    emerald: 'border-rose-500/30 bg-rose-500/10 text-rose-300',
  }[badgeVariant] || 'border-rose-500/30 bg-rose-500/10 text-rose-300';

  return (
    <div className="group/section my-4 rounded-xl border border-white/[0.08] bg-[#11131c]/90 transition-all duration-200 hover:border-rose-500/30 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.5)] overflow-hidden">
                            
      <div
        onClick={() => collapsible && setExpanded(!expanded)}
        className={`flex items-center justify-between gap-3 px-4 py-3 bg-[#151824]/90 border-b border-white/[0.06] ${
          collapsible ? 'cursor-pointer select-none hover:bg-[#181c2b]' : ''
        }`}
      >
        <div className="flex items-center gap-2.5 min-w-0">
          {emoji ? (
            <span className="text-base select-none">{emoji}</span>
          ) : Icon ? (
            <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-rose-500/25 bg-rose-500/10 text-rose-400">
              <Icon className="h-4 w-4" />
            </div>
          ) : (
            <span className="h-2 w-2 rounded-full bg-rose-500" />
          )}

          <h3 className="text-sm font-semibold tracking-tight text-slate-100 truncate">
            {title}
          </h3>

          {badge && (
            <span className={`rounded-md border px-2 py-0.5 text-[10px] font-mono font-medium ${badgeStyles}`}>
              {badge}
            </span>
          )}
        </div>

        <div className="flex items-center gap-1.5 shrink-0">
          {rawText && (
            <button
              onClick={handleCopySection}
              className="flex items-center gap-1 rounded-md px-2 py-1 text-[11px] font-mono text-slate-400 transition-colors hover:bg-slate-800 hover:text-slate-200"
              title="Copy section content"
            >
              {copied ? (
                <>
                  <Check className="h-3 w-3 text-rose-400" />
                  <span className="text-rose-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="h-3 w-3" />
                  <span className="hidden sm:inline">Copy</span>
                </>
              )}
            </button>
          )}

          {collapsible && (
            <button className="p-1 text-slate-400 hover:text-slate-200">
              {expanded ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>
          )}
        </div>
      </div>

                             
      {(!collapsible || expanded) && (
        <div className="p-4 sm:p-5 text-sm text-slate-200">
          {children}
        </div>
      )}
    </div>
  );
}
