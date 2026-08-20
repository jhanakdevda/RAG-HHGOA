import React, { useState, useEffect } from 'react';
import { Search, Database, Cpu, Sparkles } from 'lucide-react';

export default function ProcessingState({ isVoice }) {
  const [stepIndex, setStepIndex] = useState(0);

  const steps = [
    { label: 'Searching evidence', detail: 'Dense vector retrieval over 21.5k passage chunks', icon: Search },
    { label: 'Ranking relevant context', detail: 'Evaluating semantic similarity & score thresholding', icon: Database },
    { label: 'Generating grounded response', detail: 'Formulating context-bounded Groq Llama 3.1 8B answer', icon: Cpu }
  ];

  useEffect(() => {
    const timer1 = setTimeout(() => setStepIndex(1), 600);
    const timer2 = setTimeout(() => setStepIndex(2), 1400);
    return () => {
      clearTimeout(timer1);
      clearTimeout(timer2);
    };
  }, []);

  const CurrentIcon = steps[stepIndex].icon;

  return (
    <div className="w-full mb-6 tech-panel p-6 border border-cyan-500/30 bg-[#0B0F14]/95 shadow-[0_0_30px_rgba(0,240,255,0.1)] text-center animate-fadeIn font-sans">
      
      {/* Animated Icon Ring */}
      <div className="w-12 h-12 rounded-full bg-cyan-500/10 border border-cyan-500/40 flex items-center justify-center text-cyan-400 mx-auto mb-4 relative">
        <CurrentIcon className="w-6 h-6 animate-pulse" />
        <div className="absolute inset-0 rounded-full border-2 border-cyan-400/30 animate-ping opacity-25" />
      </div>

      {/* Title */}
      <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider mb-3">
        {isVoice ? 'TRANSCRIBING & RETRIEVING KNOWLEDGE' : 'RETRIEVING KNOWLEDGE'}
      </h3>

      {/* Animated Pipeline Steps */}
      <div className="max-w-md mx-auto space-y-2 font-mono text-xs text-left pt-2">
        {steps.map((step, idx) => {
          const isDone = idx < stepIndex;
          const isCurrent = idx === stepIndex;
          return (
            <div
              key={idx}
              className={`p-2.5 rounded-lg border transition-all flex items-center justify-between ${
                isCurrent
                  ? 'bg-cyan-500/10 border-cyan-500/40 text-cyan-300 shadow-sm'
                  : isDone
                  ? 'bg-white/5 border-white/5 text-slate-400'
                  : 'bg-transparent border-transparent text-slate-600'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <span className={`w-2 h-2 rounded-full ${
                  isCurrent ? 'bg-cyan-400 animate-ping' : isDone ? 'bg-emerald-400' : 'bg-slate-700'
                }`} />
                <span className="font-semibold text-xs">{step.label}</span>
              </div>

              <span className="text-[10px] text-slate-500 font-normal hidden sm:inline">
                {step.detail}
              </span>
            </div>
          );
        })}
      </div>

      {/* Bottom Pulse Bar */}
      <div className="w-full bg-white/5 rounded-full h-1 mt-5 max-w-md mx-auto overflow-hidden">
        <div className="bg-gradient-to-r from-cyan-500 via-blue-500 to-purple-500 h-1 rounded-full animate-pulse w-full" />
      </div>

    </div>
  );
}
