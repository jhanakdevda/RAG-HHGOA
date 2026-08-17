import React from 'react';
import { X, Cpu, ShieldCheck, Globe, Mic, Database } from 'lucide-react';

export default function AboutModal({ isOpen, onClose }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
      <div className="glass-card max-w-xl w-full p-6 border border-cyan-500/30 bg-[#080d1e]/95 shadow-[0_20px_60px_rgba(0,0,0,0.8)] relative font-sans">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          aria-label="Close modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 mb-4 font-mono">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/40 flex items-center justify-center text-cyan-400">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white tracking-wide">
              RAGE — Voice-Enabled Multilingual RAG
            </h2>
            <p className="text-xs text-cyan-400 font-semibold">
              Hacker House Goa 2026 &bull; Task 2
            </p>
          </div>
        </div>

        {/* Modal Description */}
        <div className="space-y-4 text-xs text-slate-300 leading-relaxed font-sans mb-6">
          <p>
            RAGE is an ultra-low latency, voice-enabled Retrieval-Augmented Generation (RAG) system built for accurate multilingual knowledge discovery across English and 15 Indic languages.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 font-mono text-[11px]">
            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-cyan-300">
                <Mic className="w-3.5 h-3.5" /> Sarvam Speech-to-Text
              </div>
              <p className="text-slate-400 font-sans text-[11px]">
                High-accuracy Indic speech transcription with automatic dialect and script recognition.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-purple-300">
                <Database className="w-3.5 h-3.5" /> FAISS Vector Store
              </div>
              <p className="text-slate-400 font-sans text-[11px]">
                Dense vector retrieval over MS MARCO-XI multilingual passage embeddings.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-emerald-300">
                <Cpu className="w-3.5 h-3.5" /> Groq Llama 3.1 8B
              </div>
              <p className="text-slate-400 font-sans text-[11px]">
                Ultra-fast LLM answer generation with strictly context-grounded prompt templates.
              </p>
            </div>

            <div className="p-3 rounded-xl bg-white/[0.03] border border-white/5 space-y-1">
              <div className="flex items-center gap-1.5 font-bold text-amber-300">
                <ShieldCheck className="w-3.5 h-3.5" /> Grounding Verifier
              </div>
              <p className="text-slate-400 font-sans text-[11px]">
                Automated claim verification engine that measures context alignment and prevents hallucinations.
              </p>
            </div>
          </div>
        </div>

        {/* Footer info */}
        <div className="pt-4 border-t border-white/10 flex items-center justify-between font-mono text-[10px] text-slate-500">
          <span>Version 2.4.0 (Production)</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 border border-cyan-500/40 text-cyan-300 font-semibold"
          >
            Got it
          </button>
        </div>

      </div>
    </div>
  );
}
