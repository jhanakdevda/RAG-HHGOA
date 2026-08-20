import React from 'react';
import { ShieldCheck, ArrowRight } from 'lucide-react';

export default function SecurityFooterBanner() {
  return (
    <footer className="w-full py-6 font-sans">
      <div className="max-w-xl mx-auto p-4 rounded-3xl bg-[#080518]/90 border border-purple-500/30 shadow-lg text-center space-y-2">
        <div className="flex items-center justify-center gap-2 font-mono text-xs font-bold text-emerald-400 uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>Protected by 4-Tier Safety Guardrails</span>
        </div>

        <div className="flex flex-wrap items-center justify-center gap-2 font-mono text-[11px] text-slate-400">
          <span>Input Filter</span>
          <ArrowRight className="w-3 h-3 text-purple-400" />
          <span>Context Filter</span>
          <ArrowRight className="w-3 h-3 text-purple-400" />
          <span>Output Filter</span>
          <ArrowRight className="w-3 h-3 text-purple-400" />
          <span>Post-Response Filter</span>
        </div>
      </div>
    </footer>
  );
}
