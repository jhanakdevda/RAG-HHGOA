import React from 'react';
import { Cpu, ShieldCheck, Zap, Globe, Database } from 'lucide-react';

export default function AboutSection() {
  const techStack = [
    { name: 'Sarvam STT', desc: 'Speech Recognition for 10+ Indian Languages', icon: Globe },
    { name: 'FAISS Vector Search', desc: 'Ultra-Fast 21.5k Chunk Dense Retrieval', icon: Database },
    { name: 'MS MARCO-XI', desc: 'Multilingual Evidence Corpus', icon: Database },
    { name: 'Groq Llama 3.1 8B', desc: 'Sub-Second LLM Generation', icon: Zap },
    { name: 'Grounding Verification', desc: 'Hallucination Screening & Attribution', icon: ShieldCheck },
  ];

  return (
    <section className="w-full mt-12 mb-8 pt-8 pb-6 border-t border-white/10 font-sans">
      <div className="text-center max-w-xl mx-auto mb-8">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-mono mb-3">
          <Cpu className="w-3.5 h-3.5" />
          <span>HACKER HOUSE GOA 2026</span>
        </div>

        <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight mb-2 font-mono uppercase">
          About RAGE
        </h2>
        <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
          RAGE is a Voice-Enabled Multilingual Retrieval-Augmented Generation system engineered for ultra-fast, grounded query answering across Indic scripts and English.
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-w-4xl mx-auto">
        {techStack.map((tech, idx) => {
          const Icon = tech.icon;
          return (
            <div key={idx} className="clean-card p-3.5 flex items-start gap-3">
              <div className="p-2 rounded-lg bg-white/5 border border-white/10 text-cyan-400 shrink-0">
                <Icon className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-xs font-bold text-slate-200 font-mono">{tech.name}</h3>
                <p className="text-[11px] text-slate-400 leading-tight mt-0.5">{tech.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
