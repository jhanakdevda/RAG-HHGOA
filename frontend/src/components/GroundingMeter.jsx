import React from 'react';
import { ShieldCheck, CheckCircle2 } from 'lucide-react';

export default function GroundingMeter({ status, score }) {
  if (!status) return null;

  const percent = typeof score === 'number' ? Math.round(score * 100) : null;

  let label = '✓ Grounded';
  let colorClass = 'text-emerald-400';
  let barColorClass = 'from-emerald-500 to-teal-400';

  if (status === 'PARTIALLY_GROUNDED') {
    label = '◐ Partially Grounded';
    colorClass = 'text-amber-400';
    barColorClass = 'from-amber-500 to-yellow-400';
  } else if (status === 'NO_CONTEXT' || status === 'UNGROUNDED') {
    label = '○ No Context';
    colorClass = 'text-sky-400';
    barColorClass = 'from-sky-500 to-blue-400';
  }

  return (
    <div className="w-full mb-3 clean-card p-3 font-mono text-xs animate-fadeIn">
      <div className="flex items-center justify-between mb-1.5">
        <span className={`font-bold flex items-center gap-1.5 ${colorClass}`}>
          <ShieldCheck className="w-3.5 h-3.5" />
          {label}
        </span>
        {percent !== null && status !== 'NO_CONTEXT' && (
          <span className="text-white font-bold">{percent}%</span>
        )}
      </div>

      {percent !== null && status !== 'NO_CONTEXT' && (
        <div className="w-full h-1.5 rounded-full bg-black/50 overflow-hidden border border-white/5">
          <div
            className={`h-full bg-gradient-to-r ${barColorClass} rounded-full transition-all duration-500`}
            style={{ width: `${Math.max(5, Math.min(100, percent))}%` }}
          />
        </div>
      )}
    </div>
  );
}
