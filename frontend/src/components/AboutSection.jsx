import React from 'react';
import { Mic, Database, BookOpen, Cpu, ShieldCheck } from 'lucide-react';

export default function AboutSection() {
  const techCards = [
    {
      name: 'Sarvam STT',
      role: 'Speech Recognition',
      desc: 'High-accuracy Indic speech transcription for English, Hindi, Marathi, and Gujarati.',
      icon: Mic,
      color: 'text-cyan-400'
    },
    {
      name: 'FAISS',
      role: 'Vector Retrieval',
      desc: 'Sub-25ms L2 normalized dense vector search across 21,573 passage embeddings.',
      icon: Database,
      color: 'text-purple-400'
    },
    {
      name: 'MS MARCO-XI',
      role: 'Knowledge Retrieval',
      desc: 'Authentic multilingual evidence corpus with rich metadata provenance.',
      icon: BookOpen,
      color: 'text-blue-400'
    },
    {
      name: 'Llama / Groq',
      role: 'Answer Generation',
      desc: 'Sub-second LLM answer synthesis with context-bounded prompt templates.',
      icon: Cpu,
      color: 'text-emerald-400'
    },
    {
      name: 'Grounding Verification',
      role: 'Hallucination Screening',
      desc: 'Automated claim verification engine preventing unverified AI responses.',
      icon: ShieldCheck,
      color: 'text-amber-400'
    }
  ];

  return (
    <section className="w-full mt-10 mb-8 pt-8 border-t border-white/10 font-sans">
      
      {/* Header */}
      <div className="text-center max-w-xl mx-auto mb-8">
        <h2 className="text-sm font-bold text-cyan-400 font-mono tracking-widest uppercase mb-2">
          ABOUT RAG
        </h2>
        <p className="text-xs sm:text-sm text-slate-300 leading-relaxed font-normal">
          RAG is a voice-enabled multilingual Retrieval-Augmented Generation system designed to provide fast, grounded answers across English and Indian languages.
        </p>
      </div>

      {/* Technology Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        {techCards.map((tech, idx) => {
          const Icon = tech.icon;
          return (
            <div key={idx} className="tech-panel p-4 flex items-start gap-3.5 hover:border-white/20 transition-all">
              <div className={`p-2.5 rounded-lg bg-white/5 border border-white/10 ${tech.color} shrink-0`}>
                <Icon className="w-4 h-4" />
              </div>
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h3 className="text-xs font-bold text-white font-mono">{tech.name}</h3>
                </div>
                <div className="text-[11px] font-mono text-cyan-400 font-medium">{tech.role}</div>
                <p className="text-[11px] text-slate-400 leading-relaxed font-sans">{tech.desc}</p>
              </div>
            </div>
          );
        })}
      </div>

    </section>
  );
}
