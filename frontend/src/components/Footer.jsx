import React from 'react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/10 py-6 font-mono text-xs text-slate-400">
      <div className="page-container flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Left */}
        <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 text-slate-400">
          <span className="font-bold text-white">RAGE</span>
          <span>&bull;</span>
          <span>Voice-Enabled Multilingual RAG</span>
          <span className="hidden sm:inline">&bull;</span>
          <span className="text-slate-500 hidden sm:inline">Built for Hacker House Goa 2026</span>
        </div>

        {/* Center Tag */}
        <div className="px-3 py-1 rounded-full bg-white/[0.04] border border-white/10 text-cyan-400 font-bold text-[11px] tracking-widest">
          HH GOA TASK 2
        </div>

        {/* Right Feature Badges */}
        <div className="flex items-center gap-3 text-[11px] text-slate-400">
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/5">Safety</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/5">Grounding</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/5">Multilingual</span>
          <span className="px-2 py-0.5 rounded bg-white/5 border border-white/5 text-purple-300">Voice</span>
        </div>

      </div>
    </footer>
  );
}
