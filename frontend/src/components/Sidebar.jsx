import React, { useState } from 'react';
import { Mic, BookOpen, Database, Cpu, ShieldCheck, Settings, ChevronRight, Sliders } from 'lucide-react';

export default function Sidebar({ onOpenAbout, onToggleHowItWorks, onOpenHistory }) {
  const [controlNexus, setControlNexus] = useState(true);
  const [guardrailLevel, setGuardrailLevel] = useState('Strict (0.55)');

  const aboutCards = [
    { title: 'Sarvam STT', sub: 'Speech Recognition', desc: 'Real-time Indic speech-to-text', icon: Mic, color: 'text-cyan-400' },
    { title: 'MS MARCO-XI', sub: 'Knowledge Retrieval', desc: 'Multilingual passage corpus', icon: BookOpen, color: 'text-purple-400' },
    { title: 'FAISS', sub: 'Vector Retrieval', desc: 'Sub-25ms L2 dense search', icon: Database, color: 'text-blue-400' },
    { title: 'Llama / Groq', sub: 'Answer Generation', desc: 'Sub-second LLM inference', icon: Cpu, color: 'text-emerald-400' },
    { title: 'Grounding Verification', sub: 'Hallucination Screening', desc: 'Automated claim alignment', icon: ShieldCheck, color: 'text-amber-400' }
  ];

  return (
    <aside className="w-full lg:w-72 shrink-0 space-y-5 font-sans">
      
      {/* 1. About RAG Box */}
      <div className="glass-panel p-4 space-y-3 font-sans">
        <div className="flex items-center justify-between font-mono text-xs text-white font-bold border-b border-purple-500/20 pb-2">
          <span>About RAG</span>
          <button onClick={onOpenAbout} className="text-[11px] text-purple-300 hover:text-white font-normal">View All</button>
        </div>

        <div className="space-y-2">
          {aboutCards.map((card, idx) => {
            const Icon = card.icon;
            return (
              <div key={idx} className="p-2.5 rounded-xl bg-[#0d091e]/90 border border-purple-500/20 hover:border-purple-500/40 transition-all flex items-start gap-2.5">
                <div className={`p-1.5 rounded-lg bg-white/5 ${card.color} shrink-0`}>
                  <Icon className="w-3.5 h-3.5" />
                </div>
                <div className="space-y-0.5">
                  <div className="text-xs font-bold text-slate-100 font-mono">{card.title}</div>
                  <div className="text-[10px] text-cyan-400 font-mono">{card.sub}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 2. Architecture & Models Box */}
      <div className="glass-panel p-4 space-y-3 font-sans">
        <div className="flex items-center justify-between font-mono text-xs text-white font-bold border-b border-purple-500/20 pb-2">
          <span>Architecture &amp; Models</span>
          <Settings className="w-3.5 h-3.5 text-purple-400" />
        </div>

        <button
          onClick={onToggleHowItWorks}
          className="w-full p-3 rounded-xl bg-gradient-to-r from-purple-950/60 to-indigo-950/60 border border-purple-500/30 hover:border-purple-400 text-left space-y-1 transition-all group"
        >
          <div className="text-xs font-bold text-white font-mono flex items-center justify-between">
            <span>Pipeline Schema</span>
            <ChevronRight className="w-3.5 h-3.5 text-purple-400 group-hover:translate-x-1 transition-transform" />
          </div>
          <p className="text-[11px] text-slate-300 font-sans">
            End-to-end telemetry, 4-tier guardrails &amp; FAISS index
          </p>
        </button>
      </div>

      {/* 3. Settings & Privacy Controls */}
      <div className="glass-panel p-4 space-y-3 font-sans font-mono text-xs">
        <div className="flex items-center justify-between font-bold text-white border-b border-purple-500/20 pb-2">
          <span>Settings &amp; Privacy Controls</span>
          <Sliders className="w-3.5 h-3.5 text-cyan-400" />
        </div>

        <div className="space-y-2">
          <button
            onClick={onOpenHistory}
            className="w-full p-2.5 rounded-xl bg-[#0d091e]/90 border border-purple-500/20 hover:border-cyan-500/40 text-left flex items-center justify-between text-slate-200 transition-colors"
          >
            <span>History Management</span>
            <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
          </button>

          <div className="p-2.5 rounded-xl bg-[#0d091e]/90 border border-purple-500/20 space-y-1">
            <div className="flex justify-between text-slate-200">
              <span>Guardrail Strength</span>
              <span className="text-emerald-400 font-bold">{guardrailLevel}</span>
            </div>
          </div>

          <div className="p-2.5 rounded-xl bg-[#0d091e]/90 border border-purple-500/20 flex items-center justify-between">
            <span className="text-slate-200">Control Nexus</span>
            <button
              onClick={() => setControlNexus(!controlNexus)}
              className={`w-9 h-5 rounded-full p-0.5 transition-colors ${
                controlNexus ? 'bg-cyan-500' : 'bg-slate-700'
              }`}
            >
              <div className={`w-4 h-4 rounded-full bg-white transition-transform ${
                controlNexus ? 'translate-x-4' : 'translate-x-0'
              }`} />
            </button>
          </div>
        </div>
      </div>

    </aside>
  );
}
