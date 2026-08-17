import React from 'react';
import { Mic, FileText, Globe, Search, Layers, Cpu, ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      num: '01',
      title: 'Voice / Text Input',
      desc: 'Ask questions using microphone or keyboard in English or 15 Indic languages.',
      icon: Mic,
      color: 'from-purple-500/20 to-pink-500/20 text-purple-400 border-purple-500/30'
    },
    {
      num: '02',
      title: 'Sarvam STT',
      desc: 'Converts spoken Indic speech to text using Sarvam Speech-to-Text API.',
      icon: FileText,
      color: 'from-blue-500/20 to-cyan-500/20 text-cyan-400 border-cyan-500/30'
    },
    {
      num: '03',
      title: 'Language Detection',
      desc: 'Identifies input language script and configures target response language.',
      icon: Globe,
      color: 'from-cyan-500/20 to-teal-500/20 text-teal-400 border-teal-500/30'
    },
    {
      num: '04',
      title: 'FAISS Retrieval',
      desc: 'Queries dense vector index using SentenceTransformers embeddings.',
      icon: Search,
      color: 'from-emerald-500/20 to-green-500/20 text-emerald-400 border-emerald-500/30'
    },
    {
      num: '05',
      title: 'MS MARCO-XI',
      desc: 'Retrieves top-k relevant multilingual knowledge passages.',
      icon: Layers,
      color: 'from-yellow-500/20 to-amber-500/20 text-amber-400 border-amber-500/30'
    },
    {
      num: '06',
      title: 'Groq Llama 3.1 8B',
      desc: 'Generates context-bound grounded response via Groq TLS Llama LLM.',
      icon: Cpu,
      color: 'from-purple-500/20 to-indigo-500/20 text-indigo-400 border-indigo-500/30'
    },
    {
      num: '07',
      title: 'Grounding Verification',
      desc: 'Evaluates claim-to-context alignment score to eliminate hallucinations.',
      icon: ShieldCheck,
      color: 'from-blue-500/20 to-violet-500/20 text-violet-400 border-violet-500/30'
    },
    {
      num: '08',
      title: 'Trusted Answer',
      desc: 'Delivers grounded multilingual answer with source attribution cards.',
      icon: CheckCircle2,
      color: 'from-emerald-500/20 to-teal-500/20 text-emerald-400 border-emerald-500/30'
    }
  ];

  return (
    <section id="how-it-works" className="pt-20 pb-16 border-t border-white/10 mt-16 scroll-mt-20">
      
      {/* Section Header */}
      <div className="text-center max-w-3xl mx-auto mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/30 text-purple-300 text-xs font-mono mb-3">
          <span>ARCHITECTURE PIPELINE</span>
        </div>
        <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight mb-3">
          How It Works
        </h2>
        <p className="text-slate-400 text-sm sm:text-base">
          From your voice to a verified, grounded answer.
        </p>
      </div>

      {/* Grid Layout (Desktop 4 cols x 2 rows / Mobile 1 col) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {steps.map((step) => {
          const StepIcon = step.icon;
          return (
            <div
              key={step.num}
              className="glass-card glass-card-interactive p-5 border border-white/10 relative flex flex-col justify-between"
            >
              <div>
                {/* Step Number & Icon */}
                <div className="flex items-center justify-between mb-4 font-mono">
                  <span className="text-xs font-bold text-slate-500">
                    STEP {step.num}
                  </span>
                  <div className={`w-9 h-9 rounded-xl bg-gradient-to-br border flex items-center justify-center ${step.color}`}>
                    <StepIcon className="w-4 h-4" />
                  </div>
                </div>

                <h3 className="text-sm font-bold text-slate-100 mb-2 font-mono">
                  {step.title}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed font-sans">
                  {step.desc}
                </p>
              </div>
            </div>
          );
        })}
      </div>

    </section>
  );
}
