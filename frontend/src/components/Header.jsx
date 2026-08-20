import React from 'react';
import { Mic, Settings } from 'lucide-react';

export default function Header({
  isOnline,
  onToggleHowItWorks
}) {
  return (
    <header className="sticky top-0 z-40 w-full h-16 bg-[#060314]/90 backdrop-blur-2xl border-b border-purple-500/20 font-sans shadow-xl">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 h-full flex items-center justify-between">
        
        {/* Left: Purple Mic Logo + Title & Subtitle */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-purple-700 via-indigo-600 to-pink-600 border border-purple-300/40 flex items-center justify-center shadow-[0_0_20px_rgba(168,85,247,0.5)]">
            <Mic className="w-4 h-4 text-white drop-shadow-[0_0_8px_rgba(255,255,255,0.9)]" />
          </div>
          
          <div className="flex flex-col font-sans">
            <span className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
              Voice RAG
            </span>
            <span className="text-[10px] font-mono tracking-wider text-purple-400 uppercase font-semibold">
              MULTILINGUAL NEURAL INTELLIGENCE
            </span>
          </div>
        </div>

        {/* Right: Online Pill + Architecture Settings Button matching image */}
        <div className="flex items-center gap-3 font-mono text-xs">
          <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-xs font-mono font-bold transition-all ${
            isOnline
              ? "bg-emerald-950/60 border border-emerald-500/40 text-emerald-400 shadow-[0_0_12px_rgba(16,185,129,0.2)]"
              : "bg-rose-950/60 border border-rose-500/40 text-rose-400"
          }`}>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>{isOnline ? "Online" : "Offline"}</span>
          </div>

          <button
            onClick={onToggleHowItWorks}
            className="px-4 py-1.5 rounded-xl bg-purple-950/60 hover:bg-purple-900/80 border border-purple-500/40 text-white font-sans text-xs font-bold transition-all shadow-md flex items-center gap-1.5"
          >
            <Settings className="w-3.5 h-3.5 text-purple-300" />
            <span>Architecture</span>
          </button>
        </div>

      </div>
    </header>
  );
}
