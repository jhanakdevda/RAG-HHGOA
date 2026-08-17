import React, { useEffect, useState } from 'react';
import { Check, Loader2, Database, Cpu, ShieldCheck, Mic, FileText } from 'lucide-react';

export default function ProcessingPipeline({ isLoading, isVoice }) {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const voiceSteps = [
    { label: 'Listening...', icon: Mic },
    { label: 'Transcribing...', icon: FileText },
    { label: 'Retrieving knowledge...', icon: Database },
    { label: 'Generating answer...', icon: Cpu },
    { label: 'Verifying answer...', icon: ShieldCheck },
  ];

  const textSteps = [
    { label: 'Retrieving knowledge...', icon: Database },
    { label: 'Generating answer...', icon: Cpu },
    { label: 'Verifying answer...', icon: ShieldCheck },
  ];

  const steps = isVoice ? voiceSteps : textSteps;

  useEffect(() => {
    if (!isLoading) {
      setCurrentStepIndex(0);
      return;
    }

    // Step progression animation loop
    const interval = setInterval(() => {
      setCurrentStepIndex((prev) => (prev < steps.length - 1 ? prev + 1 : prev));
    }, 450);

    return () => clearInterval(interval);
  }, [isLoading, isVoice, steps.length]);

  if (!isLoading) return null;

  return (
    <div className="w-full mb-6 glass-card p-4 border border-cyan-500/30 bg-[#0a1226]/80 animate-fadeIn">
      <div className="flex items-center justify-between mb-3 px-1">
        <span className="text-xs font-mono font-semibold text-cyan-400 uppercase tracking-wider flex items-center gap-2">
          <Loader2 className="w-3.5 h-3.5 animate-spin" />
          RAG Pipeline Processing
        </span>
        <span className="text-[11px] font-mono text-slate-400">
          Step {currentStepIndex + 1} of {steps.length}
        </span>
      </div>

      {/* Steps Visual Progress Chain */}
      <div className="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-5 gap-2 font-mono text-xs">
        {steps.map((step, idx) => {
          const isDone = idx < currentStepIndex;
          const isActive = idx === currentStepIndex;
          const StepIcon = step.icon;

          return (
            <div
              key={idx}
              className={`p-2.5 rounded-xl border transition-all flex items-center gap-2 ${
                isDone
                  ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300'
                  : isActive
                  ? 'bg-cyan-500/20 border-cyan-400 text-cyan-200 shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                  : 'bg-white/[0.02] border-white/5 text-slate-500'
              }`}
            >
              <div className="shrink-0">
                {isDone ? (
                  <div className="w-4 h-4 rounded-full bg-emerald-500/20 flex items-center justify-center">
                    <Check className="w-3 h-3 text-emerald-400" />
                  </div>
                ) : isActive ? (
                  <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />
                ) : (
                  <StepIcon className="w-3.5 h-3.5 text-slate-600" />
                )}
              </div>
              <span className="truncate text-[11px] font-medium">{step.label}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
