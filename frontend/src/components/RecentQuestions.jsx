import React, { useState, useEffect } from 'react';
import { Clock, Trash2, ArrowUpRight, History } from 'lucide-react';

const STORAGE_KEY = 'rage_recent_questions_v1';

export function saveRecentQuestion(qText) {
  if (!qText || !qText.trim()) return;
  try {
    const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const filtered = existing.filter(item => item.text.toLowerCase() !== qText.trim().toLowerCase());
    const updated = [{ text: qText.trim(), timestamp: Date.now() }, ...filtered].slice(0, 8);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.error('Failed to save recent question:', err);
  }
}

export function loadRecentQuestions() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch (err) {
    return [];
  }
}

export function formatTimeAgo(timestamp) {
  if (!timestamp) return 'Recently';
  const diffSecs = Math.floor((Date.now() - timestamp) / 1000);
  if (diffSecs < 60) return 'Just now';
  const diffMins = Math.floor(diffSecs / 60);
  if (diffMins < 60) return `${diffMins} min ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours} hr ago`;
  return `${Math.floor(diffHours / 24)} days ago`;
}

export default function RecentQuestions({ onSelectQuestion, activeQuery }) {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    setQuestions(loadRecentQuestions());
  }, [activeQuery]);

  const handleClear = () => {
    localStorage.removeItem(STORAGE_KEY);
    setQuestions([]);
  };

  if (!questions || questions.length === 0) return null;

  return (
    <div className="w-full mb-6 glass-card p-4 border border-white/10 font-mono text-xs animate-fadeIn">
      
      {/* Header Bar */}
      <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-white/10">
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-purple-400" />
          <span className="font-bold text-slate-200 tracking-wider">
            RECENT QUESTIONS
          </span>
        </div>

        <button
          onClick={handleClear}
          className="text-[11px] text-slate-400 hover:text-rose-400 flex items-center gap-1 transition-colors hover:underline"
          title="Clear history"
        >
          <Trash2 className="w-3 h-3" />
          <span>Clear history</span>
        </button>
      </div>

      {/* Questions list */}
      <div className="space-y-1.5 font-sans">
        {questions.map((item, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(item.text)}
            className="w-full p-2.5 rounded-xl bg-white/[0.02] hover:bg-white/[0.06] border border-white/5 hover:border-cyan-500/30 text-left transition-all flex items-center justify-between group"
          >
            <span className="text-xs text-slate-200 font-medium truncate pr-2 group-hover:text-cyan-300">
              {item.text}
            </span>
            <div className="flex items-center gap-2 shrink-0 font-mono text-[10px] text-slate-500">
              <span>{formatTimeAgo(item.timestamp)}</span>
              <ArrowUpRight className="w-3 h-3 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            </div>
          </button>
        ))}
      </div>

    </div>
  );
}
