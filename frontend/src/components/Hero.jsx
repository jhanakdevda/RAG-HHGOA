import React from 'react';
import { Mic, Zap, Search, Shield, Lock } from 'lucide-react';

export default function Hero() {
  const badges = [
    { label: 'Sarvam AI STT', detail: '(1 min)', icon: Mic },
    { label: 'multilingual-MiniLM', detail: 'Dense Embeddings', icon: Zap },
    { label: 'FAISS Vector DB', detail: '21.5k chunks', icon: Search },
    { label: '4-Tier', detail: 'Safety Guardrails', icon: Shield },
    { label: 'Live Grounding', detail: 'Verifier', icon: Lock },
  ];

  return (
    <section className="pt-8 pb-6 sm:pt-12 sm:pb-8 text-center max-w-4xl mx-auto px-4 font-sans">
      
      {/* Reference Image Title */}
      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-4 leading-tight">
        <span className="text-white">Voice-Enabled </span>
        <span className="gradient-title">Multilingual RAG</span>
      </h1>

      {/* Reference Subtitle */}
      <p className="text-slate-300 text-sm sm:text-base font-normal leading-relaxed max-w-3xl mx-auto mb-6">
        Speak or search in <strong>4 Indic languages</strong> & English. Powered by Sarvam STT, multilingual dense embeddings, sub-millisecond FAISS vector retrieval, and multi-tier guardrails.
      </p>

      {/* Reference Pill Badges Row */}
      <div className="flex flex-wrap items-center justify-center gap-2 font-mono text-xs">
        {badges.map((badge, idx) => {
          const Icon = badge.icon;
          return (
            <div
              key={idx}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#120e24]/80 border border-purple-500/25 text-slate-300 backdrop-blur-md shadow-sm"
            >
              <Icon className="w-3.5 h-3.5 text-purple-400" />
              <span className="font-semibold text-white">{badge.label}</span>
              <span className="text-slate-400 text-[11px] font-normal">{badge.detail}</span>
            </div>
          );
        })}
      </div>

    </section>
  );
}
