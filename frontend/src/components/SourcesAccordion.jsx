import React, { useState } from 'react';
import { BookOpen, ChevronDown, ChevronUp, ExternalLink, ShieldAlert } from 'lucide-react';

export default function SourcesAccordion({ sources }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  // Strictly do NOT render if sources is missing or empty
  if (!sources || !Array.isArray(sources) || sources.length === 0) {
    return null;
  }

  const toggleSource = (idx) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  return (
    <div className="w-full mb-6 glass-card p-5 border border-white/10 animate-fadeIn">
      
      {/* Header */}
      <div className="flex items-center gap-2 mb-4 pb-2 border-b border-white/10 font-mono text-xs">
        <BookOpen className="w-4 h-4 text-cyan-400" />
        <span className="font-bold text-slate-200 tracking-wider">
          SOURCES ({sources.length})
        </span>
        <span className="text-slate-500 ml-auto text-[11px]">MS MARCO-XI Chunks</span>
      </div>

      {/* Sources List */}
      <div className="space-y-3">
        {sources.map((src, idx) => {
          const isExpanded = expandedIndex === idx;
          const scorePercent = src.similarity_score
            ? Math.round(src.similarity_score * 100)
            : null;

          return (
            <div
              key={src.chunk_id || idx}
              className={`rounded-xl border transition-all ${
                isExpanded
                  ? 'bg-white/[0.04] border-cyan-500/40 shadow-[0_0_15px_rgba(0,240,255,0.1)]'
                  : 'bg-white/[0.02] border-white/5 hover:border-white/15'
              }`}
            >
              {/* Accordion Header Bar */}
              <button
                onClick={() => toggleSource(idx)}
                className="w-full p-3.5 flex items-center justify-between text-left gap-3 focus:outline-none"
              >
                <div className="flex items-center gap-3 min-w-0">
                  <span className="px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 font-mono text-[11px] font-bold shrink-0">
                    SOURCE 0{idx + 1}
                  </span>

                  <div className="min-w-0">
                    <h4 className="text-xs sm:text-sm font-semibold text-slate-200 truncate">
                      {src.title || src.domain || `Chunk ID: ${src.chunk_id}`}
                    </h4>
                    <div className="flex items-center gap-2 text-[11px] font-mono text-slate-400">
                      {src.domain && <span>{src.domain}</span>}
                      {src.language_name && <span>&bull; {src.language_name}</span>}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-3 shrink-0">
                  {scorePercent !== null && (
                    <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-mono text-[10px] font-bold">
                      {scorePercent}% Match
                    </span>
                  )}
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </button>

              {/* Accordion Expanded Content */}
              {isExpanded && (
                <div className="px-4 pb-4 pt-1 border-t border-white/5 text-xs text-slate-300 leading-relaxed font-sans animate-fadeIn">
                  <div className="p-3 rounded-lg bg-black/40 border border-white/5 font-mono text-[11px] text-slate-300 whitespace-pre-wrap mb-2">
                    {src.text_snippet || src.snippet || 'No text snippet available.'}
                  </div>

                  <div className="flex items-center justify-between font-mono text-[10px] text-slate-500 pt-1">
                    <span>Target Lang: {src.target_lang || src.language_code || 'en'}</span>
                    {src.url && (
                      <a
                        href={src.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-cyan-400 hover:underline flex items-center gap-1"
                      >
                        View Link <ExternalLink className="w-3 h-3" />
                      </a>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

    </div>
  );
}
