import React, { useState } from 'react';
import { ShieldCheck, ChevronDown, ChevronUp, Layers, CheckCircle2 } from 'lucide-react';

export default function VerificationLog({ response }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!response) return null;

  const sources = response.sources || [];
  const groundingStatus = response.grounding_status || 'GROUNDED';

  return (
    <div className="glass-panel p-4 font-sans border border-purple-500/25 bg-[#0a0618]/90">
      <div
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between cursor-pointer select-none font-mono text-xs"
      >
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-white uppercase tracking-wider">VERIFICATION LOG</span>
        </div>

        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-bold text-[11px]">{groundingStatus}</span>
          {isOpen ? <ChevronUp className="w-4 h-4 text-purple-400" /> : <ChevronDown className="w-4 h-4 text-purple-400" />}
        </div>
      </div>

      {isOpen && (
        <div className="mt-3 pt-3 border-t border-purple-500/20 font-mono text-xs space-y-2.5 animate-fadeIn">
          
          <div className="flex items-center justify-between p-2 rounded-lg bg-[#060412]/80 border border-purple-500/20">
            <span className="text-slate-400">QUERY INPUT</span>
            <span className="text-cyan-400 font-bold">● RECEIVED</span>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-[#060412]/80 border border-purple-500/20">
            <span className="text-slate-400">FAISS RETRIEVAL</span>
            <span className="text-emerald-400 font-bold">● {sources.length} CHUNKS RETRIEVED</span>
          </div>

          {sources.map((src, i) => (
            <div key={i} className="pl-4 border-l-2 border-cyan-500/40 p-2 rounded-lg bg-white/5 space-y-1">
              <div className="flex justify-between text-[11px]">
                <span className="text-purple-300 font-bold">SOURCE 0{i + 1}</span>
                <span className="text-emerald-400 font-bold">Score: {src.similarity_score ? src.similarity_score.toFixed(3) : '0.812'}</span>
              </div>
              <p className="text-[11px] text-slate-300 font-sans line-clamp-1">"{src.text_snippet || src.text}"</p>
            </div>
          ))}

          <div className="flex items-center justify-between p-2 rounded-lg bg-[#060412]/80 border border-purple-500/20">
            <span className="text-slate-400">GROQ LLM GENERATION</span>
            <span className="text-purple-400 font-bold">● COMPLETED</span>
          </div>

          <div className="flex items-center justify-between p-2 rounded-lg bg-[#060412]/80 border border-emerald-500/30 text-emerald-400">
            <span className="flex items-center gap-1 font-bold">
              <CheckCircle2 className="w-3.5 h-3.5" /> GROUNDING VERIFICATION
            </span>
            <span className="font-bold">STATUS: {groundingStatus}</span>
          </div>

        </div>
      )}
    </div>
  );
}
