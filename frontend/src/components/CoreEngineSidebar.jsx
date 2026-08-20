import React from 'react';
import { Mic, BookOpen, Database, Cpu, ShieldCheck } from 'lucide-react';

export default function CoreEngineSidebar({
  appState = 'IDLE',
  isVoiceActive = false
}) {
  const cards = [
    {
      num: '01',
      title: 'Sarvam STT',
      sub: 'Speech Recognition',
      desc: 'Indic speech-to-text',
      icon: Mic,
      isActive: isVoiceActive || appState === 'TRANSCRIBING',
      statusText: isVoiceActive || appState === 'TRANSCRIBING' ? '● ACTIVE' : '● READY'
    },
    {
      num: '02',
      title: 'MS MARCO-XI',
      sub: 'Multilingual Knowledge Corpus',
      desc: 'Multilingual evidence dataset',
      icon: BookOpen,
      isActive: appState === 'RETRIEVING',
      statusText: '● READY'
    },
    {
      num: '03',
      title: 'FAISS',
      sub: 'Dense Vector Retrieval',
      desc: '21,573 vectors (384-dim)',
      icon: Database,
      isActive: appState === 'RETRIEVING',
      statusText: '● READY'
    },
    {
      num: '04',
      title: 'Llama 3.1 8B',
      sub: 'Groq Generation',
      desc: 'Sub-second LLM inference',
      icon: Cpu,
      isActive: appState === 'GENERATING',
      statusText: appState === 'GENERATING' ? '● GENERATING' : '● READY'
    },
    {
      num: '05',
      title: 'Grounding Verification',
      sub: 'Claim Alignment',
      desc: 'Automated claim alignment',
      icon: ShieldCheck,
      isActive: appState === 'VERIFYING',
      statusText: '● READY'
    }
  ];

  return (
    <aside className="w-full lg:w-64 shrink-0 font-sans">
      
      {/* Core Engine Panel */}
      <div className="glass-panel p-4 space-y-3 font-sans border border-purple-500/25 bg-[#0a0618]/90">
        <div className="flex items-center justify-between font-mono text-xs text-white font-bold border-b border-purple-500/20 pb-2">
          <span className="tracking-wider uppercase">CORE ENGINE</span>
          <span className="text-[10px] text-cyan-400">5 MODULES</span>
        </div>

        <div className="space-y-2">
          {cards.map((card) => {
            const Icon = card.icon;
            return (
              <div
                key={card.num}
                className={`p-3 rounded-xl border transition-all duration-300 font-sans ${
                  card.isActive
                    ? 'bg-purple-950/80 border-cyan-400/60 shadow-[0_0_15px_rgba(0,240,255,0.25)]'
                    : 'bg-[#0c081d]/80 border-purple-500/20 hover:border-purple-500/40'
                }`}
              >
                <div className="flex items-center justify-between mb-1 font-mono text-xs">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold text-purple-400">{card.num}</span>
                    <Icon className={`w-3.5 h-3.5 ${card.isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                    <span className="font-bold text-slate-100 font-mono text-xs">{card.title}</span>
                  </div>

                  <span className={`text-[10px] font-mono font-bold ${
                    card.isActive ? 'text-cyan-400' : 'text-emerald-400'
                  }`}>
                    {card.statusText}
                  </span>
                </div>

                <div className="text-[11px] text-cyan-400 font-mono pl-5">{card.sub}</div>
              </div>
            );
          })}
        </div>
      </div>

    </aside>
  );
}
