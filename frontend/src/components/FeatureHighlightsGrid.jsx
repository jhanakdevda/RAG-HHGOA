import React from 'react';
import { Globe, Zap, ShieldCheck, BarChart3 } from 'lucide-react';

export default function FeatureHighlightsGrid() {
  const features = [
    { icon: Globe, title: '14 Indic Languages + English', desc: 'Multilingual neural support' },
    { icon: Zap, title: 'Sub-millisecond Retrieval', desc: 'FAISS HNSW dense search' },
    { icon: ShieldCheck, title: 'Enterprise-Grade Guardrails', desc: '4-tier automated safety' },
    { icon: BarChart3, title: 'Real-time Analytics', desc: 'Telemetry & P99 latency HUD' },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 font-sans">
      {features.map((f, i) => {
        const Icon = f.icon;
        return (
          <div
            key={i}
            className="p-4 rounded-2xl bg-[#080518]/90 border border-purple-500/20 hover:border-purple-500/40 transition-all space-y-1 font-sans shadow-sm"
          >
            <div className="flex items-center gap-2">
              <Icon className="w-4 h-4 text-cyan-400 shrink-0" />
              <span className="font-bold text-white text-xs">{f.title}</span>
            </div>
            <p className="text-[11px] text-slate-400 font-sans pl-6">{f.desc}</p>
          </div>
        );
      })}
    </div>
  );
}
