import React from 'react';
import GithubIcon from './GithubIcon';
import {
  CheckCircle2,
  Loader2,
  AlertCircle,
  FolderGit2,
  FileText,
  Binary,
  Database,
  ArrowRight
} from 'lucide-react';

const PIPELINE_STEPS = [
  { id: 'profile', label: 'GitHub Profile Found', icon: GithubIcon, threshold: 20 },
  { id: 'repos', label: 'Repositories Discovered & Cloned', icon: FolderGit2, threshold: 35 },
  { id: 'files', label: 'Files Filtered & Logic Extracted', icon: FileText, threshold: 65 },
  { id: 'embeddings', label: 'Vector Embeddings Generated', icon: Binary, threshold: 85 },
  { id: 'database', label: 'ChromaDB Knowledge Base Ready', icon: Database, threshold: 100 },
];

export default function LiveProgress({ username, statusData, onRetry, onContinueToChat }) {
  const isError = statusData?.status === 'error';
  const isCompleted = statusData?.status === 'completed';
  const progressPct = Math.min(100, Math.max(0, statusData?.progress_pct || 5));

  return (
    <div className="max-w-xl mx-auto my-12 px-4 animate-fade-in">
      <div className="bg-white rounded-2xl border border-rose-200 shadow-[0_8px_40px_-8px_rgba(244,63,94,0.15)] p-8 relative overflow-hidden">

        <div className="absolute -top-16 left-1/2 -translate-x-1/2 w-64 h-32 bg-rose-100/60 rounded-full blur-3xl pointer-events-none" />

        <div className="text-center mb-8 relative">
          <div className={`inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 ${
            isError ? 'bg-rose-100 border border-rose-200' :
            isCompleted ? 'bg-gradient-to-br from-rose-500 to-rose-600 shadow-[0_8px_20px_-4px_rgba(244,63,94,0.4)]' :
            'bg-rose-50 border border-rose-200'
          }`}>
            {isError ? (
              <AlertCircle className="w-8 h-8 text-rose-500" />
            ) : isCompleted ? (
              <CheckCircle2 className="w-8 h-8 text-white" />
            ) : (
              <Loader2 className="w-8 h-8 animate-spin text-rose-500" />
            )}
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-gray-900">
            {isError ? 'Indexing Interrupted' : isCompleted ? 'Index Complete!' : 'Indexing Portfolio...'}
          </h2>
          <p className="text-sm font-mono text-rose-500 mt-1">@{username}</p>
        </div>

        <div className="mb-8">
          <div className="flex justify-between items-center text-xs font-mono text-gray-500 mb-2">
            <span>{statusData?.current_step || 'Building vector representations...'}</span>
            <span className="text-rose-500 font-bold">{progressPct}%</span>
          </div>
          <div className="w-full bg-rose-50 rounded-full h-2.5 overflow-hidden border border-rose-100">
            <div
              className={`h-full transition-all duration-500 rounded-full ${
                isError
                  ? 'bg-rose-400'
                  : isCompleted
                  ? 'bg-gradient-to-r from-rose-400 to-rose-600'
                  : 'bg-gradient-to-r from-rose-400 to-rose-500'
              }`}
              style={{ width: `${progressPct}%` }}
            />
          </div>
          {statusData?.step_detail && (
            <p className="text-xs text-gray-400 font-mono mt-2 truncate text-center">
              {statusData.step_detail}
            </p>
          )}
        </div>

        <div className="space-y-2.5 mb-8">
          {PIPELINE_STEPS.map((step) => {
            const Icon = step.icon;
            const isDone = progressPct >= step.threshold || isCompleted;
            const isActive = !isDone && progressPct >= (step.threshold - 25);

            return (
              <div
                key={step.id}
                className={`flex items-center justify-between p-3.5 rounded-xl border transition-all ${
                  isDone
                    ? 'bg-rose-50 border-rose-200 text-gray-700'
                    : isActive
                    ? 'bg-white border-rose-300 text-gray-800 shadow-sm'
                    : 'bg-gray-50 border-gray-100 text-gray-400'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-2 rounded-lg ${
                    isDone
                      ? 'bg-rose-100 text-rose-500'
                      : isActive
                      ? 'bg-rose-50 text-rose-400'
                      : 'bg-gray-100 text-gray-400'
                  }`}>
                    <Icon className="w-4 h-4" />
                  </div>
                  <span className="text-xs sm:text-sm font-medium">{step.label}</span>
                </div>

                <div>
                  {isDone ? (
                    <CheckCircle2 className="w-4.5 h-4.5 text-rose-500" />
                  ) : isActive ? (
                    <Loader2 className="w-4.5 h-4.5 text-rose-400 animate-spin" />
                  ) : (
                    <div className="w-2 h-2 rounded-full bg-gray-200" />
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {isError && (
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-600 text-xs font-mono mb-6">
            <p className="font-semibold mb-1">Error during indexing:</p>
            <p className="opacity-90">{statusData?.error_message || 'Could not complete indexing.'}</p>
            <button
              onClick={onRetry}
              className="mt-3 px-4 py-2 bg-rose-500 hover:bg-rose-600 text-white rounded-lg font-sans font-medium text-xs transition-all"
            >
              Retry Indexing
            </button>
          </div>
        )}

        {isCompleted && (
          <button
            onClick={onContinueToChat}
            className="w-full rose-glow-btn flex items-center justify-center gap-2 py-3.5 px-4 rounded-xl text-sm transition-all active:scale-95"
          >
            <span>Open AI Dashboard</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>
    </div>
  );
}
