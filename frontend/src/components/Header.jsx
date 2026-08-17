import React, { useState } from 'react';
import { Cpu, Info, HelpCircle, Menu, X, ChevronDown, ChevronUp } from 'lucide-react';

export default function Header({ isOnline, onOpenAbout, isHowItWorksOpen, onToggleHowItWorks }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleHowItWorksClick = (e) => {
    e.preventDefault();
    setMobileMenuOpen(false);
    onToggleHowItWorks();
  };

  return (
    <header className="sticky top-0 z-40 w-full h-16 bg-[#070a14]/90 backdrop-blur-md border-b border-white/5 transition-all">
      <div className="main-container flex items-center justify-between h-full">
        
        {/* Left Branding */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-500/20 to-purple-500/20 border border-cyan-500/30 flex items-center justify-center">
            <Cpu className="w-4 h-4 text-cyan-400" />
          </div>
          
          <div className="flex items-center gap-2 font-sans">
            <span className="font-bold text-base tracking-tight text-white font-mono">
              RAGE
            </span>
            <span className="text-white/20 hidden sm:inline">|</span>
            <span className="text-xs font-medium text-slate-300 hidden sm:inline">
              Voice-Enabled Multilingual RAG
            </span>
          </div>
        </div>

        {/* Center / Right Controls (Desktop) */}
        <div className="hidden md:flex items-center gap-6">
          {/* Online/Offline indicator */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/[0.03] border border-white/5 text-xs font-mono">
            <span className={isOnline ? "dot-online" : "dot-offline"} />
            <span className={isOnline ? "text-emerald-400 font-semibold" : "text-rose-400 font-semibold"}>
              {isOnline ? "SYSTEM ONLINE" : "SYSTEM OFFLINE"}
            </span>
          </div>

          <button
            onClick={onOpenAbout}
            className="text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-white/5"
          >
            <Info className="w-3.5 h-3.5 text-slate-400" />
            <span>About</span>
          </button>

          <button
            onClick={handleHowItWorksClick}
            className="text-xs text-slate-300 hover:text-white transition-colors flex items-center gap-1.5 px-2 py-1 rounded-md hover:bg-white/5"
          >
            <HelpCircle className="w-3.5 h-3.5 text-slate-400" />
            <span>How It Works</span>
            {isHowItWorksOpen ? (
              <ChevronUp className="w-3.5 h-3.5 text-cyan-400" />
            ) : (
              <ChevronDown className="w-3.5 h-3.5 text-cyan-400" />
            )}
          </button>
        </div>

        {/* Mobile Toggle */}
        <div className="flex items-center gap-3 md:hidden">
          <div className="flex items-center gap-1.5 text-xs font-mono">
            <span className={isOnline ? "dot-online" : "dot-offline"} />
            <span className={isOnline ? "text-emerald-400" : "text-rose-400"}>
              {isOnline ? "ONLINE" : "OFFLINE"}
            </span>
          </div>

          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-1.5 text-slate-300 hover:text-white rounded-md bg-white/5 border border-white/5"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>

      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-b border-white/10 bg-[#070a14]/95 backdrop-blur-xl px-4 py-3 flex flex-col gap-2 font-mono text-xs">
          <button
            onClick={() => {
              setMobileMenuOpen(false);
              onOpenAbout();
            }}
            className="flex items-center gap-2 p-2 rounded-md text-slate-200 hover:bg-white/5 text-left"
          >
            <Info className="w-4 h-4 text-cyan-400" />
            <span>About RAGE</span>
          </button>

          <button
            onClick={handleHowItWorksClick}
            className="flex items-center justify-between p-2 rounded-md text-slate-200 hover:bg-white/5"
          >
            <div className="flex items-center gap-2">
              <HelpCircle className="w-4 h-4 text-purple-400" />
              <span>How It Works</span>
            </div>
            {isHowItWorksOpen ? <ChevronUp className="w-4 h-4 text-cyan-400" /> : <ChevronDown className="w-4 h-4 text-cyan-400" />}
          </button>
        </div>
      )}
    </header>
  );
}
