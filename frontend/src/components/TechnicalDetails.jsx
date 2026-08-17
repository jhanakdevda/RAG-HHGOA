import React, { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function TechnicalDetails({ response, sttLatency }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!response) return null;

  const retrievalMs = (response.retrieval_latency_ms || 0).toFixed(1);
  const genMs = (response.generation_latency_ms || 0).toFixed(1);
  const verifMs = (response.verification_latency_ms || response.guardrail_latency_ms || 0).toFixed(1);
  const ragTotalMs = (response.total_latency_ms || 0).toFixed(1);

  const isVoiceRequest = Boolean(sttLatency && sttLatency > 0);
  const totalE2EMs = isVoiceRequest ? (sttLatency + (response.total_latency_ms || 0)).toFixed(1) : null;

  return (
    <div className="w-full mb-3 clean-card p-3 font-mono text-xs animate-fadeIn">
      
      {/* Toggle Header */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <span className="font-bold text-slate-300">
          Technical Details {isOpen ? '▴' : '▾'}
        </span>
        <span className="text-slate-400 text-[11px]">
          Total RAG: <strong className="text-cyan-400 font-semibold">{ragTotalMs} ms</strong>
        </span>
      </button>

      {/* Expanded Table */}
      {isOpen && (
        <div className="mt-3 pt-2 border-t border-white/5 space-y-3 animate-fadeIn text-[11px] text-slate-300">
          
          {/* Voice metrics if applicable */}
          {isVoiceRequest && (
            <div className="p-2 rounded bg-purple-950/20 border border-purple-500/20 space-y-1">
              <div className="font-bold text-purple-300">Voice Pipeline</div>
              <div className="flex justify-between">
                <span>Sarvam STT</span>
                <span className="text-purple-300">{sttLatency.toFixed(1)} ms</span>
              </div>
              <div className="flex justify-between">
                <span>RAG /ask</span>
                <span className="text-cyan-300">{ragTotalMs} ms</span>
              </div>
              <div className="flex justify-between pt-1 border-t border-purple-500/20 font-bold text-emerald-400">
                <span>Total End-to-End</span>
                <span>{totalE2EMs} ms</span>
              </div>
            </div>
          )}

          {/* RAG Breakdown */}
          <div className="space-y-1">
            <div className="flex justify-between">
              <span>Retrieval</span>
              <span className="font-semibold text-slate-200">{retrievalMs} ms</span>
            </div>
            <div className="flex justify-between">
              <span>LLM</span>
              <span className="font-semibold text-slate-200">
                {response.grounding_status === 'NO_CONTEXT' ? 'Not executed (0 ms)' : `${genMs} ms`}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Verification</span>
              <span className="font-semibold text-slate-200">
                {response.grounding_status === 'NO_CONTEXT' ? 'Not executed (0 ms)' : `${verifMs} ms`}
              </span>
            </div>
            <div className="flex justify-between pt-1 border-t border-white/5 font-bold text-cyan-400">
              <span>Total RAG</span>
              <span>{ragTotalMs} ms</span>
            </div>
          </div>

          {/* Model & Retrieval Metadata */}
          <div className="pt-2 border-t border-white/5 space-y-1 text-slate-400">
            <div className="flex justify-between">
              <span>Model:</span>
              <span className="text-slate-200">{response.model_used || 'Llama 3.1 8B — Groq'}</span>
            </div>
            <div className="flex justify-between">
              <span>Retrieval:</span>
              <span className="text-slate-200">FAISS</span>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
