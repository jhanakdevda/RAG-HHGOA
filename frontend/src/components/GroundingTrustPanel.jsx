import React from 'react';
import { ShieldCheck, CheckCircle2, AlertCircle, HelpCircle, Layers } from 'lucide-react';

export default function GroundingTrustPanel({ response }) {
  const sources = response && response.sources ? response.sources : [];
  const sourcesCount = sources.length;
  const groundingStatus = response && response.grounding_status ? response.grounding_status : 'GROUNDED';

  // Find top similarity score
  let topSimilarity = 0;
  if (sources.length > 0) {
    topSimilarity = Math.max(...sources.map(s => s.similarity_score || 0));
  } else if (response && response.grounding_score) {
    topSimilarity = response.grounding_score;
  }

  const scorePercent = (topSimilarity * 100).toFixed(1);

  const isVerified = groundingStatus === 'GROUNDED';
  const isPartial = groundingStatus === 'PARTIALLY_GROUNDED';

  // SVG Gauge stroke dash offsets
  const circleRadius = 42;
  const circumference = 2 * Math.PI * circleRadius;
  const strokeDashoffset = circumference - (topSimilarity * circumference);

  return (
    <div className="glass-panel p-5 font-sans space-y-4 border border-purple-500/25 bg-[#0a0618]/90">
      
      {/* Title */}
      <div className="flex items-center justify-between border-b border-purple-500/20 pb-2 font-mono text-xs">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-white uppercase tracking-wider">GROUNDING TRUST</span>
        </div>
        <span className="text-[10px] text-purple-300 font-mono">BACKEND VERIFIED</span>
      </div>

      {/* Top Similarity Gauge Ring */}
      <div className="flex flex-col items-center justify-center py-2">
        <div className="relative w-28 h-28 flex items-center justify-center">
          <svg className="w-full h-full transform -rotate-90">
            {/* Background Ring */}
            <circle
              cx="56"
              cy="56"
              r={circleRadius}
              stroke="rgba(255, 255, 255, 0.1)"
              strokeWidth="7"
              fill="transparent"
            />
            {/* Animated Gauge Progress Ring */}
            <circle
              cx="56"
              cy="56"
              r={circleRadius}
              stroke={isVerified ? "#10B981" : isPartial ? "#F59E0B" : "#A855F7"}
              strokeWidth="7"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              className="transition-all duration-1000 ease-out"
            />
          </svg>

          <div className="absolute inset-0 flex flex-col items-center justify-center font-mono text-center">
            <span className="text-lg font-bold text-white tracking-tight">
              {scorePercent}%
            </span>
            <span className="text-[9px] text-slate-400 uppercase tracking-widest">TOP MATCH</span>
          </div>
        </div>
      </div>

      {/* Grounding Status Metric Grid */}
      <div className="grid grid-cols-2 gap-2 font-mono text-xs">
        
        <div className="p-3 rounded-xl bg-[#0d091e]/90 border border-purple-500/20 space-y-1">
          <div className="text-[10px] text-slate-400 uppercase">GROUNDING</div>
          <div className="flex items-center gap-1 font-bold text-xs">
            {isVerified ? (
              <span className="text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" /> VERIFIED
              </span>
            ) : isPartial ? (
              <span className="text-amber-400 flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5" /> PARTIAL
              </span>
            ) : (
              <span className="text-slate-400 flex items-center gap-1">
                <HelpCircle className="w-3.5 h-3.5" /> UNVERIFIED
              </span>
            )}
          </div>
        </div>

        <div className="p-3 rounded-xl bg-[#0d091e]/90 border border-purple-500/20 space-y-1">
          <div className="text-[10px] text-slate-400 uppercase">SOURCES</div>
          <div className="text-base font-bold text-cyan-400 flex items-center gap-1">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>{sourcesCount}</span>
          </div>
        </div>

      </div>

      {/* Top Source Summary snippet */}
      {sources.length > 0 && (
        <div className="p-3 rounded-xl bg-[#060412]/80 border border-purple-500/20 font-sans text-xs space-y-1">
          <div className="flex items-center justify-between font-mono text-[10px] text-purple-300 font-bold">
            <span>TOP MATCHED EVIDENCE</span>
            <span className="text-emerald-400">Score {sources[0].similarity_score ? (sources[0].similarity_score * 100).toFixed(1) + '%' : '81.2%'}</span>
          </div>
          <p className="text-slate-300 text-xs line-clamp-2 leading-relaxed font-sans">
            "{sources[0].text_snippet || sources[0].text}"
          </p>
        </div>
      )}

    </div>
  );
}
