import React from 'react';

const TECH_META = {
  python: { label: 'Python', color: 'border-rose-500/30 text-rose-300 bg-rose-500/10' },
  react: { label: 'React', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  fastapi: { label: 'FastAPI', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  typescript: { label: 'TypeScript', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  javascript: { label: 'JavaScript', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  docker: { label: 'Docker', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  chromadb: { label: 'ChromaDB', color: 'border-rose-500/40 text-rose-200 bg-rose-900/20' },
  pytorch: { label: 'PyTorch', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  tensorflow: { label: 'TensorFlow', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  tailwind: { label: 'Tailwind CSS', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  nextjs: { label: 'Next.js', color: 'border-slate-500/30 text-slate-200 bg-slate-500/10' },
  nodejs: { label: 'Node.js', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  postgresql: { label: 'PostgreSQL', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  mongodb: { label: 'MongoDB', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  langchain: { label: 'LangChain', color: 'border-rose-500/20 text-rose-200 bg-rose-950/20' },
  redis: { label: 'Redis', color: 'border-rose-600/30 text-rose-400 bg-rose-600/10' },
};

export default function TechnologyBadge({ name, onClick, size = 'sm' }) {
  const normalized = (name || '').toLowerCase().replace(/[^a-z0-9]/g, '');
  const meta = TECH_META[normalized] || {
    label: name,
    color: 'border-rose-500/20 text-rose-200 bg-rose-950/20',
  };

  const isClickable = typeof onClick === 'function';

  return (
    <span
      onClick={() => isClickable && onClick(name)}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      className={`inline-flex items-center gap-1.5 rounded-lg border font-mono font-medium transition-all ${
        size === 'lg' ? 'px-3.5 py-1.5 text-xs' : 'px-2.5 py-1 text-[11px]'
      } ${meta.color} ${
        isClickable
          ? 'cursor-pointer hover:border-rose-500/60 hover:bg-rose-500/20 hover:scale-[1.02] active:scale-[0.98]'
          : ''
      }`}
    >
      <span className="h-1.5 w-1.5 rounded-full bg-current opacity-80" />
      <span>{meta.label || name}</span>
    </span>
  );
}
