import React from 'react';

export default function KeyValueCard({ items = [] }) {
  if (!items || items.length === 0) return null;

  return (
    <div className="my-3 grid grid-cols-1 sm:grid-cols-2 gap-2">
      {items.map((item, idx) => (
        <div
          key={idx}
          className="flex items-center justify-between rounded-lg border border-white/[0.06] bg-[#12141d] px-3.5 py-2 text-xs"
        >
          <span className="font-mono text-slate-400">{item.key || item.label}:</span>
          <span className="font-semibold text-rose-200">{item.value}</span>
        </div>
      ))}
    </div>
  );
}
