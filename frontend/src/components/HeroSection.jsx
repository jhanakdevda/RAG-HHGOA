import React from 'react';
import { Mic, Zap, Database, ShieldCheck, Lock } from 'lucide-react';

export default function HeroSection() {
  return (
    <section className="font-sans space-y-4 pt-2 pb-2 text-center max-w-3xl mx-auto">
      
      {/* Title */}
      <h1 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white tracking-tight leading-tight">
        Voice-Enabled{' '}
        <span className="bg-gradient-to-r from-pink-400 via-orange-400 to-purple-400 bg-clip-text text-transparent">
          Multilingual RAG
        </span>
      </h1>

      {/* Subtitle */}
      <p className="text-xs sm:text-sm text-slate-300 font-sans leading-relaxed">
        Speak or search in <span className="text-white font-semibold">14 Indic languages</span> &amp; English. Powered by Sarvam STT, multilingual dense embeddings, sub-millisecond FAISS vector retrieval, and multi-tier guardrails.
      </p>

      {/* Badges Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 pt-2 font-sans text-xs">
        <div className="p-2.5 rounded-2xl bg-white/5 border border-white/10 text-slate-200 flex items-center justify-center gap-2 shadow-sm">
          <Mic className="w-4 h-4 text-pink-400 shrink-0" />
          <div className="text-left">
            <strong className="text-white block">Sarvam AI STT</strong>
            <span className="text-[10px] text-slate-400 font-mono">(1 min)</span>
          </div>
        </div>

        <div className="p-2.5 rounded-2xl bg-white/5 border border-white/10 text-slate-200 flex items-center justify-center gap-2 shadow-sm">
          <Zap className="w-4 h-4 text-amber-400 shrink-0" />
          <div className="text-left">
            <strong className="text-white block">multilingual-e5</strong>
            <span className="text-[10px] text-slate-400 font-mono">Dense Embeddings</span>
          </div>
        </div>

        <div className="p-2.5 rounded-2xl bg-white/5 border border-white/10 text-slate-200 flex items-center justify-center gap-2 shadow-sm">
          <Database className="w-4 h-4 text-orange-400 shrink-0" />
          <div className="text-left">
            <strong className="text-white block">FAISS HNSW</strong>
            <span className="text-[10px] text-slate-400 font-mono">Vector DB</span>
          </div>
        </div>

        <div className="p-2.5 rounded-2xl bg-white/5 border border-white/10 text-slate-200 flex items-center justify-center gap-2 shadow-sm">
          <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
          <div className="text-left">
            <strong className="text-white block">4-Tier</strong>
            <span className="text-[10px] text-slate-400 font-mono">Safety Guardrails</span>
          </div>
        </div>
      </div>

      {/* Rate Limiter Bar */}
      <div className="p-2.5 rounded-2xl bg-white/5 border border-white/10 text-slate-300 font-mono text-xs flex items-center justify-center gap-2 shadow-sm">
        <Lock className="w-3.5 h-3.5 text-pink-400" />
        <span><strong className="text-white">5 Req/Min</strong> Rate Limiter</span>
      </div>

    </section>
  );
}
