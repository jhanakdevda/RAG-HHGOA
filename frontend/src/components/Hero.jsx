import React from 'react';
import { Sparkles } from 'lucide-react';

export default function Hero() {
  return (
    <section className="pt-8 pb-6 text-center max-width-xl mx-auto">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/25 text-cyan-400 text-xs font-mono mb-4 shadow-[0_0_15px_rgba(0,240,255,0.15)]">
        <Sparkles className="w-3.5 h-3.5" />
        <span>MS MARCO-XI &bull; Groq Llama 3.1 8B &bull; Sarvam STT</span>
      </div>

      <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight mb-3">
        <span className="bg-gradient-to-r from-purple-400 to-violet-500 bg-clip-text text-transparent">Ask. </span>
        <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Listen. </span>
        <span className="bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">Discover.</span>
      </h1>

      <p className="text-slate-300 text-sm sm:text-base max-w-2xl mx-auto font-normal leading-relaxed">
        Ask questions in English or your preferred Indian language and get grounded answers from trusted knowledge sources.
      </p>
    </section>
  );
}
