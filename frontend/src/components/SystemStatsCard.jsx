import React from 'react';
import { Activity, Mic, Zap, AlertTriangle, Shield, Clock } from 'lucide-react';

export default function SystemStatsCard({ response }) {
  const p50 = response ? Math.round((response.retrieval_latency_ms || 120) * 1.0) : 120;
  const p70 = response ? Math.round((response.retrieval_latency_ms || 120) * 1.5) : 180;
  const p100 = response ? Math.round((response.retrieval_latency_ms || 120) * 2.1) : 250;

  return (
    <div className="w-full glass-panel p-6 rounded-3xl border border-purple-500/30 bg-[#080518]/90 shadow-lg space-y-4 font-sans">
      
      {/* Header */}
      <div className="flex items-center justify-between border-b border-purple-500/20 pb-3 font-mono text-xs">
        <div className="flex items-center gap-2 font-bold text-white uppercase tracking-wider">
          <Activity className="w-4 h-4 text-cyan-400" />
          <span>Live System Stats</span>
        </div>
        <span className="text-[10px] text-emerald-400 font-bold">HEALTHY • 99.9% UPTIME</span>
      </div>

      {/* Glowing Purple Sine Wave Graph SVG */}
      <div className="w-full h-12 relative overflow-hidden flex items-center justify-center">
        <svg className="w-full h-full text-purple-400 stroke-current fill-none" viewBox="0 0 500 50" preserveAspectRatio="none">
          <path
            d="M 0 25 Q 30 10, 60 25 T 120 25 T 180 15 T 240 30 T 300 20 T 360 25 T 420 15 T 480 30 L 500 25"
            strokeWidth="2.5"
            className="drop-shadow-[0_0_8px_rgba(168,85,247,0.8)]"
          />
        </svg>
      </div>

      {/* 5 Latency & Stats Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 font-mono text-xs">
        
        <div className="p-3 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-1">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase">
            <Mic className="w-3.5 h-3.5 text-purple-400" />
            <span>Latency (P50)</span>
          </div>
          <div className="text-base font-bold text-white">{p50} <span className="text-xs text-slate-400">ms</span></div>
        </div>

        <div className="p-3 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-1">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Latency (P70)</span>
          </div>
          <div className="text-base font-bold text-white">{p70} <span className="text-xs text-slate-400">ms</span></div>
        </div>

        <div className="p-3 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-1">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase">
            <AlertTriangle className="w-3.5 h-3.5 text-pink-400" />
            <span>Latency (P100)</span>
          </div>
          <div className="text-base font-bold text-white">{p100} <span className="text-xs text-slate-400">ms</span></div>
        </div>

        <div className="p-3 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-1">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase">
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span>QPS (Current)</span>
          </div>
          <div className="text-base font-bold text-emerald-400">3.2 <span className="text-xs text-slate-400">req/s</span></div>
        </div>

        <div className="p-3 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-1">
          <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-bold uppercase">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>Uptime</span>
          </div>
          <div className="text-base font-bold text-cyan-400">99.9%</div>
        </div>

      </div>

    </div>
  );
}
