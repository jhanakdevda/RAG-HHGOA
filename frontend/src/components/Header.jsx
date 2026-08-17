import React, { useState } from 'react';
import { Cpu, HelpCircle, Menu, X, Info } from 'lucide-react';

export default function Header({ isOnline, onOpenAbout }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const scrollToHowItWorks = (e) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    const element = document.getElementById('how-it-works');
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <header className="sticky top-0 z-40 w-full backdrop-blur-xl bg-[#050816]/80 border-b border-white/10 transition-all">
      <div className="page-container flex items-center justify-between h-16">
        
        {/* Left Branding */}
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-emerald-500/20 border border-cyan-500/40 flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.25)]">
            <Cpu className="w-5 h-5 text-cyan-400" />
          </div>
          
          <div className="flex items-center gap-2.5">
            <span className="font-extrabold text-lg tracking-tight text-white font-mono">
              RAGE
            </span>
            <span className="text-white/20 hidden sm:inline font-mono">|</span>
            <span className="text-xs sm:text-sm font-medium text-slate-300 tracking-wide hidden sm:inline">
              Voice-Enabled Multilingual RAG
            </span>
          </div>
        </div>

        {/* Center / Right Controls (Desktop) */}
        <div className="hidden md:flex items-center gap-6">
          {/* Status Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-white/[0.04] border border-white/10 text-xs font-mono">
            {isOnline ? (
              <>
                <span className="status-dot-online" />
                <span className="text-emerald-400 font-semibold tracking-wider">SYSTEM ONLINE</span>
              </>
            ) : (
              <>
                <span className="status-dot-offline" />
                <span className="text-rose-400 font-semibold tracking-wider">SYSTEM OFFLINE</span>
              </>
            )}
          </div>

          <button
            onClick={onOpenAbout}
            className="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-white/5"
          >
            <Info className="w-3.5 h-3.5" />
            <span>About</span>
          </button>

          <a
            href="#how-it-works"
            onClick={scrollToHowItWorks}
            className="text-xs font-medium text-slate-300 hover:text-cyan-400 transition-colors flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg hover:bg-white/5"
          >
            <HelpCircle className="w-3.5 h-3.5" />
            <span>How It Works</span>
          </a>
        </div>

        {/* Mobile Toggle */}
        <div className="flex items-center gap-3 md:hidden">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-white/[0.04] border border-white/10 text-[10px] font-mono">
            <span className={isOnline ? "status-dot-online" : "status-dot-offline"} />
            <span className={isOnline ? "text-emerald-400 font-bold" : "text-rose-400 font-bold"}>
              {isOnline ? "ONLINE" : "OFFLINE"}
            </span>
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-slate-300 hover:text-white rounded-lg bg-white/5 border border-white/10"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-white/10 bg-[#080b14]/95 backdrop-blur-2xl px-4 py-4 flex flex-col gap-3 font-mono text-xs">
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenAbout();
            }}
            className="flex items-center gap-2 p-2.5 rounded-lg text-slate-200 hover:bg-white/5 text-left"
          >
            <Info className="w-4 h-4 text-cyan-400" />
            <span>About RAGE</span>
          </button>

          <a
            href="#how-it-works"
            onClick={scrollToHowItWorks}
            className="flex items-center gap-2 p-2.5 rounded-lg text-slate-200 hover:bg-white/5"
          >
            <HelpCircle className="w-4 h-4 text-purple-400" />
            <span>How It Works Architecture</span>
          </a>
        </div>
      )}
    </header>
  );
}
