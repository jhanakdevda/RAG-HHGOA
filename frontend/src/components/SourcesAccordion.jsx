import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp } from 'lucide-react';

export default function SourcesAccordion({ sources }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!sources || !Array.isArray(sources) || sources.length === 0) {
    return null;
  }

  return (
    <div className="w-full mb-3 clean-card p-3 font-mono text-xs animate-fadeIn">
      
      {/* Header Toggle */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <div className="flex items-center gap-2">
          <BookOpen className="w-3.5 h-3.5 text-cyan-400" />
          <span className="font-bold text-slate-200">
            Sources ({sources.length})
          </span>
        </div>
        
        {isOpen ? (
          <ChevronUp className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {/* Expanded List */}
      {isOpen && (
        <div className="mt-3 pt-2 border-t border-white/5 space-y-2 font-sans animate-fadeIn">
          {sources.map((src, idx) => (
            <div key={src.chunk_id || idx} className="p-2.5 rounded-lg bg-black/40 border border-white/5 text-xs text-slate-300">
              <div className="flex items-center justify-between font-mono text-[11px] text-cyan-400 font-bold mb-1">
                <span>{idx + 1}. MS MARCO-XI {src.domain ? `(${src.domain})` : ''}</span>
                {src.similarity_score && (
                  <span className="text-emerald-400">{Math.round(src.similarity_score * 100)}% match</span>
                )}
              </div>
              <p className="text-slate-300 font-mono text-[11px] leading-relaxed line-clamp-2">
                {src.text_snippet || src.snippet}
              </p>
            </div>
          ))}
        </div>
      )}

    </div>
  );
}
