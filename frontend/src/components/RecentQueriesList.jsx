import React from 'react';
import { History, ChevronRight } from 'lucide-react';

export default function RecentQueriesList({ onSelectQuery }) {
  const queries = [
    'मुंबई की ट्रैफिक समस्या क्या है?',
    'Corporate governance meaning',
    'AI in healthcare benefits',
    'విద్యుత్ શક્તિ વનવમુલુ એમીટી?'
  ];

  return (
    <div className="w-full glass-panel p-6 rounded-3xl border border-purple-500/30 bg-[#080518]/90 shadow-lg space-y-4 font-sans">
      
      <div className="flex items-center justify-between border-b border-purple-500/20 pb-3 font-mono text-xs">
        <div className="flex items-center gap-2 font-bold text-white uppercase tracking-wider">
          <History className="w-4 h-4 text-purple-400" />
          <span>Recent Queries</span>
        </div>
        <button
          onClick={() => onSelectQuery && onSelectQuery(queries[0])}
          className="text-xs font-mono text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-bold"
        >
          <span>View All History</span>
          <ChevronRight className="w-3.5 h-3.5" />
        </button>
      </div>

      <div className="space-y-2 font-sans text-xs">
        {queries.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelectQuery && onSelectQuery(q)}
            className="w-full p-3 rounded-2xl bg-[#050310]/90 border border-purple-500/20 hover:border-purple-400 transition-all text-left text-slate-200 hover:text-white flex items-center gap-3 font-sans shadow-sm"
          >
            <span className="font-mono text-purple-400 font-bold">{idx + 1}.</span>
            <span className="truncate">{q}</span>
          </button>
        ))}
      </div>

    </div>
  );
}
