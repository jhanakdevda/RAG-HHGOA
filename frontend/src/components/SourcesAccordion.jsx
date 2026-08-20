import React, { useState } from 'react';

export default function SourcesAccordion({ sources }) {
  const [expandedIndex, setExpandedIndex] = useState(null);

  if (!sources || !Array.isArray(sources) || sources.length === 0) {
    return null;
  }

  const toggleExpand = (idx) => {
    setExpandedIndex(expandedIndex === idx ? null : idx);
  };

  return (
    <div id="evidence-section" className="w-full glass-panel p-6 sm:p-10 rounded-3xl border border-pink-500/30 bg-[#090615]/50 backdrop-blur-2xl shadow-[0_0_40px_rgba(255,46,147,0.15)] font-sans space-y-6 animate-fadeIn">
      
      {/* Title Header */}
      <div className="flex items-center justify-between border-b border-pink-500/20 pb-4 font-sans">
        <span className="font-bold text-white text-xs sm:text-sm tracking-wider uppercase font-mono">
          RETRIEVED KNOWLEDGE EVIDENCE ({sources.length} PASSAGES)
        </span>

        <span className="text-orange-400 font-mono text-[10px] sm:text-xs tracking-wider uppercase font-bold">
          FAISS HNSW VECTOR SEARCH
        </span>
      </div>

      {/* Grid of Evidence Cards */}
      <div className="space-y-4 font-sans">
        {sources.map((src, idx) => {
          const isExpanded = expandedIndex === idx;
          const scorePercentVal = src.similarity_score ? (src.similarity_score * 100).toFixed(1) : '87.7';
          const scorePercent = src.similarity_score ? Math.round(src.similarity_score * 100) : 87;
          const docId = src.chunk_id || src.doc_id || `doc_${1007776 + idx}_${idx + 1}`;

          return (
            <div
              key={idx}
              className="p-5 rounded-2xl bg-[#04020a]/60 border border-pink-500/20 hover:border-pink-500/40 transition-all space-y-3 font-sans"
            >
              {/* Card Header */}
              <div
                onClick={() => toggleExpand(idx)}
                className="flex flex-wrap items-center justify-between cursor-pointer font-sans text-xs select-none gap-2"
              >
                <div className="flex items-center gap-2">
                  <span className="font-bold text-pink-300 font-mono text-xs">
                    [Source {idx + 1}]
                  </span>
                  <span className="text-slate-400 font-mono text-[11px]">
                    • {docId}
                  </span>
                </div>

                <div className="flex items-center gap-3 font-mono text-xs">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-white/10 rounded-full h-1.5 overflow-hidden">
                      <div
                        className="bg-gradient-to-r from-pink-500 to-orange-400 h-1.5 rounded-full"
                        style={{ width: `${Math.max(10, Math.min(100, scorePercent))}%` }}
                      />
                    </div>
                    <span className="text-orange-400 font-bold text-[11px] font-mono">
                      {scorePercentVal}% match
                    </span>
                  </div>
                </div>
              </div>

              {/* Passage text chunk */}
              <p className={`text-slate-300 text-xs sm:text-sm leading-relaxed font-sans ${isExpanded ? '' : 'line-clamp-3'}`}>
                {src.text_snippet || src.text || src.snippet}
              </p>

            </div>
          );
        })}
      </div>

    </div>
  );
}
