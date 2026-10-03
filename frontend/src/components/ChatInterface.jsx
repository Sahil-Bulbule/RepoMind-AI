import React, { useState, useRef, useEffect } from 'react';
import {
  Send,
  Loader2,
  Trash2,
  X,
  Info,
  Terminal,
  Layers,
  ArrowUp,
  FolderGit2,
  ShieldCheck,
} from 'lucide-react';
import MessageBubble from './MessageBubble';
import { api } from '../services/api';

const DEFAULT_SUGGESTED_QUESTIONS = [
  "Summarize this GitHub profile & main engineering strengths",
  "Explain the most complex repository in detail",
  "Which repositories use Machine Learning or AI pipelines?",
  "Where is Python used and what architectures are implemented?",
  "Show the technology stack breakdown across all projects"
];

const QUICK_ACTIONS = [
  { label: 'Explain Architecture', query: 'Explain the architecture and main components of this repository' },
  { label: 'Tech Stack', query: 'What technologies, libraries, and frameworks are used here?' },
  { label: 'Key Files', query: 'What are the most important files in this repository and what does each do?' },
  { label: 'How to Run', query: 'Give step-by-step installation and run instructions for this project' },
];

export default function ChatInterface({ username, profileData, repository, onClearRepoFilter }) {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [suggestedQuestions, setSuggestedQuestions] = useState(DEFAULT_SUGGESTED_QUESTIONS);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [inputText]);

  useEffect(() => {
    if (!repository?.id) {
      setSuggestedQuestions(DEFAULT_SUGGESTED_QUESTIONS);
      return;
    }

    const cacheKey = `repo-suggestions:${username}:${repository.id}:${repository.indexed_at || ''}`;
    const cached = localStorage.getItem(cacheKey);
    if (cached) {
      try {
        setSuggestedQuestions(JSON.parse(cached));
        return;
      } catch {
        localStorage.removeItem(cacheKey);
      }
    }

    setSuggestedQuestions([
      `Explain the purpose and architecture of ${repository.name}.`,
      `What are the critical files and entry points in ${repository.name}?`,
      `What technologies and frameworks power ${repository.name}?`,
      `Summarize key features and how ${repository.name} works.`,
    ]);

    api.getRepositorySuggestions(username, repository.id)
      .then((data) => {
        if (!data.questions?.length) return;
        setSuggestedQuestions(data.questions);
        localStorage.setItem(cacheKey, JSON.stringify(data.questions));
      })
      .catch((error) => console.error('Failed to load repository suggestions:', error));
  }, [username, repository]);

  const repoFilter = repository?.name || null;

  const handleSendMessage = async (textToSend) => {
    const query = (textToSend || inputText).trim();
    if (!query || isLoading) return;

    setErrorMsg(null);
    setInputText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }

    const newMessages = [...messages, { role: 'user', content: query }];
    setMessages(newMessages);
    setIsLoading(true);

    try {
      const historyForApi = newMessages.slice(-6).map((m) => ({
        role: m.role,
        content: m.content,
      }));

      const response = await api.sendChatMessage(
        username,
        query,
        historyForApi,
        repository
      );

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          sources: response.sources || [],
        },
      ]);
    } catch (err) {
      console.error('Chat error:', err);
      setErrorMsg(err.message || 'Failed to generate answer. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setErrorMsg(null);
  };

  return (
    <div className="flex flex-col h-[calc(100dvh-8rem)] max-lg:h-[calc(100dvh-11rem)] min-h-[24rem] max-w-5xl mx-auto bg-white rounded-2xl border border-rose-100 shadow-sm overflow-hidden">

      <div className="px-5 py-3.5 border-b border-rose-100 bg-white flex items-center justify-between gap-4 shrink-0">
        <div className="flex min-w-0 items-center gap-2.5">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-rose-200 bg-rose-50 text-rose-500">
            {repoFilter ? <FolderGit2 className="h-4 w-4" /> : <Layers className="h-4 w-4" />}
          </div>

          {repoFilter ? (
            <div className="flex min-w-0 flex-col">
              <div className="flex items-center gap-2">
                <span className="truncate text-xs font-semibold text-gray-800 sm:text-sm">
                  {repository.full_name || `${username}/${repoFilter}`}
                </span>
                <span className="rounded-full border border-rose-200 bg-rose-50 px-2 py-0.5 text-[10px] font-mono font-medium text-rose-500">
                  Scoped
                </span>
              </div>
              <span className="text-[10px] font-mono text-gray-400">
                {repository.file_count || 0} indexed files · RAG active
              </span>
            </div>
          ) : (
            <div className="flex min-w-0 items-center gap-2">
              <span className="text-xs sm:text-sm font-semibold text-gray-800">
                RepoLense AI
              </span>
              <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-0.5 text-[10px] font-mono text-gray-500">
                @{username}
              </span>
            </div>
          )}

          {repoFilter && (
            <button
              onClick={onClearRepoFilter}
              className="ml-2 flex items-center gap-1 rounded-md border border-rose-100 bg-rose-50 px-2 py-1 text-[11px] font-mono text-rose-400 transition-colors hover:border-rose-300 hover:text-rose-600"
              title="Switch to full profile chat"
            >
              <X className="h-3 w-3" />
              <span className="hidden sm:inline">Clear scope</span>
            </button>
          )}
        </div>

        <div className="flex items-center gap-2 shrink-0">
          <div className="hidden md:flex items-center gap-1.5 rounded-full border border-rose-200 bg-rose-50 px-2.5 py-1 text-[10px] font-mono text-rose-500">
            <span className="h-1.5 w-1.5 rounded-full bg-rose-400 animate-pulse" />
            <span>Online</span>
          </div>

          {messages.length > 0 && (
            <button
              onClick={clearChat}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg border border-rose-100 bg-white text-gray-400 hover:text-rose-500 hover:border-rose-200 hover:bg-rose-50 text-xs font-mono transition-all"
              title="Clear chat history"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear</span>
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-6 bg-gray-50/50">
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 max-w-2xl mx-auto animate-fade-in">
            <h3 className="text-xl sm:text-2xl font-bold tracking-tight text-gray-900 mb-2">
              {repoFilter ? `Ask about ${repository.name}` : `Ask about @${username}`}
            </h3>
            <p className="text-xs sm:text-sm text-gray-500 max-w-lg mb-8 leading-relaxed">
              Explore repository details, compare projects, and ask questions about indexed source code.
            </p>

            <div className="w-full space-y-2.5">
              <div className="flex items-center justify-between px-1">
                <span className="text-[11px] font-mono uppercase tracking-wider text-rose-500 font-semibold">
                  Suggested Questions
                </span>
                <span className="text-[10px] font-mono text-gray-400">Click to run</span>
              </div>

              <div className="grid grid-cols-1 gap-2 text-left">
                {suggestedQuestions.map((question, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(question)}
                    className="group relative flex items-center justify-between p-3.5 rounded-xl border border-rose-100 bg-white hover:border-rose-300 hover:bg-rose-50 transition-all text-xs text-gray-600 hover:text-gray-900 shadow-sm"
                  >
                    <span>{question}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <MessageBubble
              key={idx}
              message={msg}
              userAvatar={profileData?.avatar_url}
              username={username}
            />
          ))
        )}

        {isLoading && (
          <div className="flex gap-3.5 items-start animate-fade-in">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-rose-500 text-white mt-1">
              <Loader2 className="h-4 w-4 animate-spin" />
            </div>

            <div className="rounded-2xl rounded-tl-sm border border-rose-100 bg-white p-4 sm:p-5 shadow-sm w-full max-w-xl">
              <div className="flex items-center gap-2.5 text-xs font-mono text-rose-500 mb-3">
                <span className="h-2 w-2 rounded-full bg-rose-400 animate-ping" />
                <span className="font-semibold">Synthesizing answer...</span>
              </div>

              <div className="space-y-2 text-[11px] font-mono text-gray-400">
                <div className="flex items-center gap-2 text-gray-600">
                  <ShieldCheck className="h-3.5 w-3.5 text-rose-500 shrink-0" />
                  <span>1. Retrieved top-k repository chunks from ChromaDB</span>
                </div>
                <div className="flex items-center gap-2 text-rose-500">
                  <Loader2 className="h-3.5 w-3.5 animate-spin text-rose-400 shrink-0" />
                  <span>2. AI analyzing code structures & documentation...</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {errorMsg && (
          <div className="p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-600 text-xs font-mono flex items-start gap-3 shadow-sm animate-fade-in">
            <Info className="w-4 h-4 shrink-0 text-rose-400 mt-0.5" />
            <div className="flex-1">
              <p className="font-semibold text-rose-600 mb-0.5">Error</p>
              <p className="opacity-90">{errorMsg}</p>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-rose-100 bg-white space-y-2 shrink-0">

        {messages.length > 0 && (
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-[11px] font-mono no-scrollbar">
            <span className="text-gray-400 text-[10px] shrink-0 mr-1">Quick asks:</span>
            {QUICK_ACTIONS.map((action, idx) => (
              <button
                key={idx}
                onClick={() => handleSendMessage(action.query)}
                disabled={isLoading}
                className="shrink-0 rounded-lg border border-rose-100 bg-rose-50 px-2.5 py-1 text-rose-500 transition-colors hover:border-rose-300 hover:bg-rose-100 disabled:opacity-40"
              >
                {action.label}
              </button>
            ))}
          </div>
        )}

        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSendMessage();
          }}
          className="relative flex items-end gap-2 rounded-2xl border border-rose-200 bg-white p-2 focus-within:border-rose-400 focus-within:ring-2 focus-within:ring-rose-100 transition-all shadow-sm"
        >
          <div className="flex-1 min-w-0">
            <textarea
              ref={textareaRef}
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={
                repoFilter
                  ? `Ask about '${repoFilter}' codebase, structure, features, tech...`
                  : `Ask about @${username}'s repositories, code, architecture, or skills...`
              }
              className="w-full resize-none bg-transparent px-3 py-2 text-sm text-gray-800 placeholder-gray-400 focus:outline-none font-sans leading-relaxed max-h-36 overflow-y-auto"
            />
          </div>

          <button
            type="submit"
            disabled={!inputText.trim() || isLoading}
            className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-rose-500 text-white hover:bg-rose-600 disabled:opacity-30 disabled:cursor-not-allowed transition-all group active:scale-95"
            title="Send query (Enter)"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <ArrowUp className="w-4 h-4 group-hover:-translate-y-0.5 transition-transform" />
            )}
          </button>
        </form>

      </div>
    </div>
  );
}
