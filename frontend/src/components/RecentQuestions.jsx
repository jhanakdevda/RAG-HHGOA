import React, { useState, useEffect } from 'react';
import { History, Trash2, Sparkles } from 'lucide-react';

const STORAGE_KEY = 'rage_recent_questions_v1';

const DEFAULT_SAMPLE_QUESTIONS = [
  "What are renewable energy sources and their benefits?",
  "पर्यावरण संरक्षण क्यों महत्वपूर्ण है?",
  "पर्यावरण संवर्धनाचे महत्त्व काय आहे?",
  "What is a corporation and how does it function?",
  "How does photosynthesis work in green plants?",
  "માનવ શરીરમાં પાણીનું કાર્ય શું છે?"
];

export function saveRecentQuestion(qText) {
  if (!qText || !qText.trim()) return;
  try {
    const existing = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    const filtered = existing.filter(item => item.text.toLowerCase() !== qText.trim().toLowerCase());
    const updated = [{ text: qText.trim(), timestamp: Date.now() }, ...filtered].slice(0, 6);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (err) {
    console.error('Failed to save recent question:', err);
  }
}

export function loadRecentQuestions() {
  try {
    const loaded = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (loaded && loaded.length > 0) {
      return loaded.map(item => item.text);
    }
    return DEFAULT_SAMPLE_QUESTIONS;
  } catch (err) {
    return DEFAULT_SAMPLE_QUESTIONS;
  }
}

export default function RecentQuestions({ onSelectQuestion, activeQuery }) {
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    setQuestions(loadRecentQuestions());
  }, [activeQuery]);

  const handleClear = () => {
    localStorage.removeItem(STORAGE_KEY);
    setQuestions(DEFAULT_SAMPLE_QUESTIONS);
  };

  if (!questions || questions.length === 0) return null;

  return (
    <div className="w-full mt-10 mb-8 clean-card p-4 font-mono text-xs animate-fadeIn">
      <div className="flex items-center justify-between pb-2.5 mb-3 border-b border-white/5">
        <div className="flex items-center gap-2 font-bold text-slate-300">
          <History className="w-4 h-4 text-purple-400" />
          <span>Recent & Sample Questions</span>
        </div>

        <button
          onClick={handleClear}
          className="text-[11px] text-slate-400 hover:text-rose-400 transition-colors flex items-center gap-1"
          title="Reset sample list"
        >
          <Trash2 className="w-3 h-3" />
          <span>Reset</span>
        </button>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 font-sans">
        {questions.map((qText, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuestion(qText)}
            className="w-full text-left p-2.5 rounded-lg bg-white/[0.02] hover:bg-white/5 border border-white/5 hover:border-white/15 text-xs text-slate-300 hover:text-cyan-300 transition-all flex items-center gap-2.5 group"
          >
            <Sparkles className="w-3.5 h-3.5 text-purple-400 shrink-0 group-hover:text-cyan-400 transition-colors" />
            <span className="truncate leading-relaxed">{qText}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
