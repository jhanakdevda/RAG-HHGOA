import React from 'react';
import { ShieldCheck, ShieldAlert, AlertCircle, CheckCircle2 } from 'lucide-react';

export default function GroundingMeter({ status, score }) {
  if (!status) return null;

  // Determine percentage from backend score (score is between 0.0 and 1.0)
  const percent = typeof score === 'number' ? Math.round(score * 100) : null;

  let badgeLabel = '✓ GROUNDED';
  let badgeColorClass = 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
  let barColorClass = 'from-emerald-500 to-teal-400';
  let descText = 'Answer fully supported by retrieved context';

  if (status === 'PARTIALLY_GROUNDED') {
    badgeLabel = '◐ PARTIALLY GROUNDED';
    badgeColorClass = 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    barColorClass = 'from-amber-500 to-yellow-400';
    descText = 'Answer partially supported by retrieved context';
  } else if (status === 'NO_CONTEXT' || status === 'UNGROUNDED' || status === 'LOW_CONFIDENCE') {
    badgeLabel = '○ NO CONTEXT';
    badgeColorClass = 'text-sky-400 border-sky-500/30 bg-sky-500/10';
    barColorClass = 'from-sky-500 to-blue-400';
    descText = 'No sufficient knowledge base evidence found';
  }

  return (
    <div className="w-full mb-6 glass-card p-4 border border-white/10 animate-fadeIn font-mono">
      <div className="flex items-center justify-between mb-2">
        <span className="text-xs font-bold text-slate-300 tracking-wider flex items-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          GROUNDING VERIFICATION
        </span>
        <div className={`px-2.5 py-0.5 rounded-full border text-xs font-bold ${badgeColorClass}`}>
          {badgeLabel}
        </div>
      </div>

      {/* Progress Bar visualization */}
      {percent !== null && status !== 'NO_CONTEXT' && (
        <div className="space-y-1.5 my-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Context Alignment</span>
            <span className="text-white font-bold">{percent}%</span>
          </div>
          <div className="w-full h-2.5 rounded-full bg-black/50 border border-white/10 overflow-hidden">
            <div
              className={`h-full bg-gradient-to-r ${barColorClass} transition-all duration-700 rounded-full`}
              style={{ width: `${Math.max(5, Math.min(100, percent))}%` }}
            />
          </div>
        </div>
      )}

      <p className="text-[11px] text-slate-400 mt-2 flex items-center gap-1.5">
        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
        <span>{descText}</span>
      </p>
    </div>
  );
}
