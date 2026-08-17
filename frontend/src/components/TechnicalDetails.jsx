import React, { useState } from 'react';
import { Gauge, ChevronDown, ChevronUp, Cpu, Server, Mic, Database, ShieldCheck } from 'lucide-react';
import { getLanguageName } from './LanguageSelector';

export default function TechnicalDetails({ response, sttLatency }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!response) return null;

  const retrievalMs = (response.retrieval_latency_ms || 0).toFixed(1);
  const genMs = (response.generation_latency_ms || 0).toFixed(1);
  const verifMs = (response.verification_latency_ms || response.guardrail_latency_ms || 0).toFixed(1);
  const ragTotalMs = (response.total_latency_ms || 0).toFixed(1);

  // Voice End-to-End calculation (separate from RAG latency)
  const isVoiceRequest = Boolean(sttLatency && sttLatency > 0);
  const totalE2EMs = isVoiceRequest ? (sttLatency + (response.total_latency_ms || 0)).toFixed(1) : null;

  const langName = getLanguageName(response.answer_language || response.detected_language);
  const sourcesCount = response.sources ? response.sources.length : 0;
  const modelName = response.model_used || 'Llama 3.1 8B';
  const providerName = response.provider_used || 'Groq';

  return (
    <div className="w-full mb-6 glass-card p-4 border border-cyan-500/20 font-mono text-xs animate-fadeIn">
      
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between text-left focus:outline-none"
      >
        <div className="flex items-center gap-2">
          <Gauge className="w-4 h-4 text-cyan-400" />
          <span className="font-bold text-slate-200 tracking-wider">
            TECHNICAL DETAILS & LATENCY
          </span>
        </div>

        <div className="flex items-center gap-2">
          <span className="px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 font-semibold">
            {ragTotalMs} ms
          </span>
          {isExpanded ? (
            <ChevronUp className="w-4 h-4 text-slate-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-slate-400" />
          )}
        </div>
      </button>

      {/* Compact View Summary when collapsed */}
      {!isExpanded && (
        <div className="mt-3 pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 text-[11px] text-slate-400">
          <span>Model: <strong className="text-slate-200">{modelName}</strong></span>
          <span>Status: <strong className="text-emerald-400">{response.grounding_status}</strong></span>
        </div>
      )}

      {/* Expanded Breakdown Table */}
      {isExpanded && (
        <div className="mt-4 pt-3 border-t border-white/10 space-y-4 animate-fadeIn">
          
          {/* 1. Voice Pipeline Latency (If Voice Request) */}
          {isVoiceRequest && (
            <div className="p-3 rounded-xl bg-purple-950/30 border border-purple-500/30 space-y-2">
              <div className="flex items-center justify-between font-bold text-purple-300 pb-1 border-b border-purple-500/20">
                <span className="flex items-center gap-1.5">
                  <Mic className="w-3.5 h-3.5 text-purple-400" />
                  VOICE PIPELINE
                </span>
                <span className="text-[10px] text-purple-400">SEPARATE STT METRICS</span>
              </div>

              <div className="flex justify-between text-slate-300">
                <span>Sarvam STT</span>
                <span className="text-purple-300 font-semibold">{sttLatency.toFixed(1)} ms</span>
              </div>
              
              <div className="flex justify-between text-slate-300">
                <span>RAG /ask</span>
                <span className="text-cyan-300 font-semibold">{ragTotalMs} ms</span>
              </div>

              <div className="flex justify-between pt-1 border-t border-purple-500/20 font-bold text-white">
                <span>Total End-to-End</span>
                <span className="text-emerald-400">{totalE2EMs} ms</span>
              </div>
            </div>
          )}

          {/* 2. RAG Execution Breakdown */}
          <div className="space-y-2 text-slate-300">
            <div className="text-slate-400 text-[10px] font-bold tracking-wider uppercase mb-1">
              RAG LATENCY BREAKDOWN
            </div>

            <div className="flex justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <Database className="w-3 h-3 text-cyan-400" /> Retrieval (FAISS)
              </span>
              <span className="font-semibold text-slate-200">{retrievalMs} ms</span>
            </div>

            <div className="flex justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <Cpu className="w-3 h-3 text-purple-400" /> LLM Generation
              </span>
              <span className="font-semibold text-slate-200">
                {response.grounding_status === 'NO_CONTEXT' ? 'Not executed (0 ms)' : `${genMs} ms`}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="flex items-center gap-1 text-slate-400">
                <ShieldCheck className="w-3 h-3 text-emerald-400" /> Verification
              </span>
              <span className="font-semibold text-slate-200">
                {response.grounding_status === 'NO_CONTEXT' ? 'Not executed (0 ms)' : `${verifMs} ms`}
              </span>
            </div>

            <div className="flex justify-between pt-2 border-t border-white/10 font-bold text-white">
              <span>Total RAG Latency</span>
              <span className="text-cyan-400">{ragTotalMs} ms</span>
            </div>
          </div>

          {/* 3. System Specs */}
          <div className="p-3 rounded-xl bg-black/40 border border-white/5 space-y-1.5 text-[11px] text-slate-400">
            <div className="flex justify-between">
              <span>Model Architecture</span>
              <span className="text-slate-200 font-semibold">{modelName}</span>
            </div>

            <div className="flex justify-between">
              <span>LLM Provider</span>
              <span className="text-slate-200 font-semibold uppercase">{providerName}</span>
            </div>

            <div className="flex justify-between">
              <span>Language</span>
              <span className="text-slate-200 font-semibold">{langName}</span>
            </div>

            <div className="flex justify-between">
              <span>Attributed Chunks</span>
              <span className="text-slate-200 font-semibold">{sourcesCount}</span>
            </div>

            <div className="flex justify-between">
              <span>Grounding Status</span>
              <span className="text-emerald-400 font-semibold">{response.grounding_status}</span>
            </div>
          </div>

        </div>
      )}

    </div>
  );
}
