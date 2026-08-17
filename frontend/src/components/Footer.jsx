import React from 'react';

export default function Footer() {
  return (
    <footer className="w-full border-t border-white/5 py-5 font-mono text-xs text-slate-400">
      <div className="main-container flex flex-col sm:flex-row items-center justify-between gap-3 text-center sm:text-left">
        
        <div>
          <span className="font-bold text-white">RAGE — Voice-Enabled Multilingual RAG</span>
          <span className="text-slate-500 block text-[11px]">Built for Hacker House Goa 2026</span>
        </div>

        <div className="text-[11px] text-slate-400">
          <span>Safety</span> &bull; <span>Grounding</span> &bull; <span>Multilingual</span> &bull; <span className="text-purple-300">Voice</span>
        </div>

      </div>
    </footer>
  );
}
