import React from 'react';
import { ArrowRight, ArrowDown } from 'lucide-react';

export default function HowItWorks({ isOpen }) {
  if (!isOpen) return null;

  const steps = [
    { title: 'Voice / Text', desc: 'Input query' },
    { title: 'Sarvam STT', desc: 'Speech to text' },
    { title: 'Language Detection', desc: 'Script & dialect' },
    { title: 'FAISS Retrieval', desc: 'Dense vector search' },
    { title: 'MS MARCO-XI', desc: 'Multilingual context' },
    { title: 'Groq Llama 3.1 8B', desc: 'LLM generation' },
    { title: 'Grounding Verification', desc: 'Claim alignment' },
    { title: 'Trusted Answer', desc: 'Grounded response' },
  ];

  return (
    <section id="how-it-works" className="w-full mt-10 mb-8 pt-6 pb-8 border-t border-white/10 animate-fadeIn font-sans">
      
      <div className="text-center max-w-xl mx-auto mb-8">
        <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight mb-1 font-mono uppercase">
          How It Works
        </h2>
        <p className="text-xs text-slate-400">
          From your voice or text to a trusted, grounded answer.
        </p>
      </div>

      {/* Desktop Horizontal Flow */}
      <div className="hidden lg:flex items-center justify-between gap-1 max-w-5xl mx-auto">
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div className="clean-card p-2.5 text-center flex-1 min-w-0">
              <div className="text-[10px] font-mono text-purple-400 font-bold">0{idx + 1}</div>
              <div className="text-[11px] font-bold text-slate-200 truncate font-mono">{step.title}</div>
              <div className="text-[10px] text-slate-400 truncate">{step.desc}</div>
            </div>

            {idx < steps.length - 1 && (
              <ArrowRight className="w-3.5 h-3.5 text-slate-500 shrink-0" />
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Mobile & Tablet Vertical Flow */}
      <div className="lg:hidden flex flex-col items-center gap-2 max-w-sm mx-auto">
        {steps.map((step, idx) => (
          <React.Fragment key={idx}>
            <div className="clean-card p-2.5 text-center w-full">
              <div className="text-[10px] font-mono text-purple-400 font-bold">0{idx + 1}</div>
              <div className="text-xs font-bold text-slate-200 font-mono">{step.title}</div>
              <div className="text-[11px] text-slate-400">{step.desc}</div>
            </div>

            {idx < steps.length - 1 && (
              <ArrowDown className="w-3.5 h-3.5 text-slate-500 my-0.5" />
            )}
          </React.Fragment>
        ))}
      </div>

    </section>
  );
}
