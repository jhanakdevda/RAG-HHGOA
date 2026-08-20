import React from 'react';
import { X, History, Trash2, ArrowUpRight, Clock } from 'lucide-react';
import { loadRecentQuestions } from './RecentQuestions';

const STORAGE_KEY = 'rage_recent_questions_v1';

export default function HistoryDrawer({ isOpen, onClose, onSelectQuestion }) {
  if (!isOpen) return null;

  const rawHistory = (() => {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    } catch (e) {
      return [];
    }
  })();

  const handleClearHistory = () => {
    localStorage.removeItem(STORAGE_KEY);
    window.location.reload();
  };

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/70 backdrop-blur-sm animate-fadeIn font-sans">
      <div className="w-full max-w-md bg-[#0B0F14] border-l border-white/10 h-full flex flex-col justify-between shadow-2xl relative font-sans">
        
        {/* Header */}
        <div className="p-5 border-b border-white/10 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
              <History className="w-4 h-4" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wide">
                Query History
              </h2>
              <p className="text-[11px] text-slate-400 font-mono">
                Recent user questions
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
            aria-label="Close history drawer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content List */}
        <div className="flex-1 overflow-y-auto p-5 space-y-2.5">
          {rawHistory && rawHistory.length > 0 ? (
            rawHistory.map((item, idx) => {
              const text = typeof item === 'string' ? item : item.text;
              const dateStr = item.timestamp ? new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : 'Recent';
              return (
                <button
                  key={idx}
                  onClick={() => {
                    onSelectQuestion(text);
                    onClose();
                  }}
                  className="w-full text-left p-3 rounded-lg bg-[#10151C] hover:bg-[#161D26] border border-white/5 hover:border-cyan-500/30 text-xs text-slate-200 transition-all flex items-start justify-between group"
                >
                  <div className="space-y-1 pr-2">
                    <p className="font-medium text-slate-200 group-hover:text-cyan-300 leading-relaxed">
                      {text}
                    </p>
                    <div className="flex items-center gap-1 text-[10px] font-mono text-slate-500">
                      <Clock className="w-3 h-3 text-slate-500" />
                      <span>{dateStr}</span>
                    </div>
                  </div>

                  <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 shrink-0 transition-colors" />
                </button>
              );
            })
          ) : (
            <div className="text-center py-12 text-slate-500 font-mono text-xs">
              No recent history recorded.
            </div>
          )}
        </div>

        {/* Footer */}
        {rawHistory && rawHistory.length > 0 && (
          <div className="p-4 border-t border-white/10 flex justify-end">
            <button
              onClick={handleClearHistory}
              className="px-3 py-1.5 rounded bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/20 text-rose-300 text-xs font-mono flex items-center gap-1.5 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Clear History</span>
            </button>
          </div>
        )}

      </div>
    </div>
  );
}
