import React, { useState } from 'react';
import { ChevronDown, ChevronUp, BarChart2 } from 'lucide-react';

export default function LatencyMeter({ response }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!response) return null;

  const retrieval = Number(response.retrieval_latency_ms ?? 0);
  const prompt = Number(response.prompt_construction_latency_ms ?? 0);
  const llmGen = Number(response.llm_request_latency_ms ?? response.generation_latency_ms ?? 0);
  const verify = Number(response.verification_latency_ms ?? response.guardrail_latency_ms ?? 0);
  const total = Number(response.total_latency_ms ?? (retrieval + prompt + llmGen + verify));
  const sttLatency = response.stt_latency_ms ? Number(response.stt_latency_ms) : null;
  const groundingScore = Math.round((response.grounding_score ?? 0) * 100);

  return (
    <div className="w-full mb-10 font-mono text-xs">
      {/* Reference Technical Details Trigger */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between p-4 rounded-xl bg-[#0c162e] hover:bg-[#121f40] border border-cyan-500/20 text-slate-200 transition-colors shadow-sm"
      >
        <div className="flex items-center gap-2 font-semibold">
          <BarChart2 className="w-4 h-4 text-cyan-400" />
          <span>Technical Details</span>
        </div>
        {isOpen ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
      </button>

      {/* Expanded Telemetry Grid */}
      {isOpen && (
        <div className="p-5 rounded-xl bg-[#0c162e]/90 border border-slate-800 mt-2 space-y-3">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <span className="text-slate-500 block text-[10px] font-bold">TOTAL</span>
              <span className="font-bold text-cyan-400 text-sm">{total.toFixed(0)} ms</span>
            </div>

            {sttLatency && (
              <div>
                <span className="text-slate-500 block text-[10px] font-bold">SARVAM STT</span>
                <span className="font-bold text-rose-400 text-sm">{sttLatency.toFixed(0)} ms</span>
              </div>
            )}

            <div>
              <span className="text-slate-500 block text-[10px] font-bold">RETRIEVAL</span>
              <span className="font-bold text-slate-200 text-sm">{retrieval.toFixed(0)} ms</span>
            </div>

            <div>
              <span className="text-slate-500 block text-[10px] font-bold">LLM</span>
              <span className="font-bold text-slate-200 text-sm">{llmGen.toFixed(0)} ms</span>
            </div>

            <div>
              <span className="text-slate-500 block text-[10px] font-bold">VERIFICATION</span>
              <span className="font-bold text-emerald-400 text-sm">{verify.toFixed(0)} ms</span>
            </div>

            <div>
              <span className="text-slate-500 block text-[10px] font-bold">GROUNDING</span>
              <span className="font-bold text-emerald-400 text-sm">{groundingScore}%</span>
            </div>

            <div>
              <span className="text-slate-500 block text-[10px] font-bold">MODEL</span>
              <span className="font-bold text-slate-300 text-sm">
                {response.provider_used === 'groq'
                  ? 'Llama 3.1 8B / Groq' 
                  : 'None / Unavailable'}
              </span>
            </div>

            <div>
              <span className="text-slate-500 block text-[10px] font-bold">CORPUS</span>
              <span className="font-bold text-slate-300 text-sm">MS MARCO-XI</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
