import React, { useState, useEffect } from 'react';
import { Sparkles, History, Trash2, ArrowUpRight } from 'lucide-react';

const STORAGE_KEY = 'rage_recent_questions_v1';

const SAMPLE_QUESTIONS = [
  "What is a corporation?",
  "What is machine learning?",
  "पर्यावरण संरक्षण क्यों महत्वपूर्ण है?",
  "नमस्ते, भारत के बारे में बताइए",
  "What is artificial intelligence?"
];

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
    const loaded = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (loaded && loaded.length > 0) {
      return loaded.map(item => typeof item === 'string' ? item : item.text);
    }
    return SAMPLE_QUESTIONS;
  } catch (err) {
    return SAMPLE_QUESTIONS;
  }
}

export default function RecentQuestions({ onSelectQuestion, activeQuery }) {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    setQuestions(loadRecentQuestions());
  }, [activeQuery]);

  const handleClear = () => {
    localStorage.removeItem(STORAGE_KEY);
    setQuestions(SAMPLE_QUESTIONS);
  };

  return (
    <div className="w-full space-y-4 font-sans animate-fadeIn">
      
      {/* Section Header */}
      <div className="flex items-center justify-between font-mono text-xs text-slate-400 pb-1">
        <div className="flex items-center gap-2">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200 tracking-wide uppercase">
            Recent & Sample Questions
          </span>
        </div>

        <button
          onClick={handleClear}
          className="text-[11px] text-slate-500 hover:text-rose-400 transition-colors flex items-center gap-1"
          title="Reset sample list"
        >
          <Trash2 className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      {/* Grid of Compact Question Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
        {SAMPLE_QUESTIONS.map((qText, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(qText)}
            className="text-left p-3 rounded-lg bg-[#10151C] hover:bg-[#161D26] border border-white/10 hover:border-cyan-500/30 text-xs text-slate-200 hover:text-cyan-300 transition-all flex items-center justify-between group font-sans shadow-sm"
          >
            <span className="truncate pr-2 font-medium leading-relaxed">{qText}</span>
            <ArrowUpRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-cyan-400 shrink-0 transition-colors" />
          </button>
        ))}
      </div>

      {/* Previously Asked Questions by User if any */}
      {questions && questions.length > 0 && (
        <div className="pt-3 border-t border-white/5">
          <div className="flex items-center gap-1.5 font-mono text-[11px] text-slate-400 mb-2">
            <History className="w-3 h-3 text-purple-400" />
            <span>YOUR RECENT HISTORY</span>
          </div>

          <div className="flex flex-wrap gap-2 font-sans">
            {questions.slice(0, 6).map((qText, idx) => (
              <button
                key={idx}
                onClick={() => onSelectQuestion(qText)}
                className="px-2.5 py-1 rounded bg-[#10151C] hover:bg-[#161D26] border border-white/5 text-xs text-slate-300 hover:text-white transition-colors truncate max-w-xs"
              >
                {qText}
              </button>
            ))}
          </div>
        </div>
      )}

    </div>
  );
}
