import React, { useState } from 'react';
import {
  Bot,
  Check,
  Copy,
  Files,
  User,
} from 'lucide-react';
import SmartResponseRenderer from './response/SmartResponseRenderer';
import SourceCard from './SourceCard';
import ProfileAvatar from './ProfileAvatar';

export default function MessageBubble({ message, userAvatar, username }) {
  const isUser = message.role === 'user';
  const [copiedAnswer, setCopiedAnswer] = useState(false);

  const handleCopyAnswer = () => {
    navigator.clipboard.writeText(message.content);
    setCopiedAnswer(true);
    setTimeout(() => setCopiedAnswer(false), 2000);
  };

  return (
    <div className={`flex gap-3.5 sm:gap-4 ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start group animate-fade-in`}>

      <div className="shrink-0 mt-1 select-none">
        {isUser ? (
          userAvatar ? (
            <div className="relative">
              <ProfileAvatar
                key={userAvatar}
                src={userAvatar}
                username={username || "User"}
                className="w-8 h-8 rounded-xl border border-rose-200 text-xs"
              />
            </div>
          ) : (
            <div className="w-8 h-8 rounded-xl bg-rose-50 border border-rose-200 flex items-center justify-center text-rose-500">
              <User className="w-4 h-4" />
            </div>
          )
        ) : (
          <div className="w-8 h-8 rounded-xl bg-rose-500 border border-rose-400 flex items-center justify-center text-white shadow-sm">
            <Bot className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className={`flex flex-col ${isUser ? 'items-end max-w-[85%] sm:max-w-[75%]' : 'items-start w-full max-w-[94%] sm:max-w-[88%]'}`}>

        {isUser ? (
          <div className="rounded-2xl rounded-tr-sm border border-rose-100 bg-rose-50 px-4 py-3 text-gray-800 shadow-sm">
            <p className="text-sm leading-relaxed whitespace-pre-wrap font-sans">
              {message.content}
            </p>
          </div>
        ) : (
          <div className="w-full rounded-2xl rounded-tl-sm border border-rose-100 bg-white shadow-sm overflow-hidden">

            <div className="flex items-center justify-between border-b border-rose-100 bg-rose-50/50 px-4 py-2.5">
              <div className="flex items-center gap-2">
                <span className="flex items-center gap-1 text-xs font-semibold text-gray-700">
                  RepoLense AI
                </span>
              </div>

              <div className="flex items-center gap-1">
                <button
                  onClick={handleCopyAnswer}
                  className="flex items-center gap-1.5 rounded-lg border border-rose-100 bg-white px-2.5 py-1 text-[11px] font-mono text-gray-500 transition-colors hover:border-rose-200 hover:text-rose-500"
                  title="Copy full response"
                >
                  {copiedAnswer ? (
                    <>
                      <Check className="h-3.5 w-3.5 text-rose-500" />
                      <span className="text-rose-500 font-medium">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-3.5 w-3.5" />
                      <span className="hidden sm:inline">Copy</span>
                    </>
                  )}
                </button>
              </div>
            </div>

            <div className="p-4 sm:p-5">
              <SmartResponseRenderer content={message.content} />
            </div>

            {message.sources && message.sources.length > 0 && (
              <div className="border-t border-rose-100 bg-rose-50/30 p-4 sm:p-5 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-xs font-mono font-semibold text-gray-600">
                    <Files className="h-4 w-4 text-rose-500" />
                    <span>Source Citations</span>
                  </div>
                  <span className="rounded-md border border-rose-100 bg-white px-2 py-0.5 text-[10px] font-mono text-gray-500">
                    {message.sources.length} {message.sources.length === 1 ? 'file cited' : 'files cited'}
                  </span>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                  {message.sources.map((src, idx) => (
                    <SourceCard key={idx} source={src} />
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

      </div>
    </div>
  );
}
