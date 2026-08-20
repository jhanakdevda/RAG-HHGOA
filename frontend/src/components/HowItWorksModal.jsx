import React, { useState } from 'react';
import { X, Settings, Zap, Shield, Lock, Globe, Clock, Mic, Scissors, Database, Cpu } from 'lucide-react';

export default function HowItWorksModal({ isOpen, onClose }) {
  const [activeTab, setActiveTab] = useState('pipeline');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xl animate-fadeIn font-sans">
      <div className="relative w-full max-w-3xl glass-panel p-6 sm:p-8 rounded-3xl border border-purple-500/30 bg-[#080518]/95 shadow-[0_0_60px_rgba(168,85,247,0.25)] space-y-6 max-h-[90vh] overflow-y-auto">
        
        {/* Modal Header */}
        <div className="flex items-start justify-between border-b border-purple-500/20 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-2xl bg-purple-950/80 border border-purple-500/40 flex items-center justify-center">
              <Settings className="w-5 h-5 text-cyan-300" />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight">
                System Architecture &amp; Technical Specs
              </h2>
              <p className="text-xs text-slate-400 font-sans">
                End-to-end pipeline, 4-tier guardrails, edge security &amp; telemetry
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-2 font-mono text-xs border-b border-purple-500/20 pb-3">
          <button
            onClick={() => setActiveTab('pipeline')}
            className={`px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all ${
              activeTab === 'pipeline'
                ? 'bg-purple-900/80 border border-purple-400 text-white shadow-md'
                : 'bg-white/5 text-slate-400 hover:text-white'
            }`}
          >
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Pipeline</span>
          </button>

          <button
            onClick={() => setActiveTab('guardrails')}
            className={`px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all ${
              activeTab === 'guardrails'
                ? 'bg-purple-900/80 border border-purple-400 text-white shadow-md'
                : 'bg-white/5 text-slate-400 hover:text-white'
            }`}
          >
            <Shield className="w-3.5 h-3.5 text-emerald-400" />
            <span>Guardrails</span>
          </button>

          <button
            onClick={() => setActiveTab('security')}
            className={`px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all ${
              activeTab === 'security'
                ? 'bg-purple-900/80 border border-purple-400 text-white shadow-md'
                : 'bg-white/5 text-slate-400 hover:text-white'
            }`}
          >
            <Lock className="w-3.5 h-3.5 text-pink-400" />
            <span>Security</span>
          </button>

          <button
            onClick={() => setActiveTab('languages')}
            className={`px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all ${
              activeTab === 'languages'
                ? 'bg-purple-900/80 border border-purple-400 text-white shadow-md'
                : 'bg-white/5 text-slate-400 hover:text-white'
            }`}
          >
            <Globe className="w-3.5 h-3.5 text-cyan-400" />
            <span>Languages</span>
          </button>

          <button
            onClick={() => setActiveTab('latency')}
            className={`px-4 py-2 rounded-xl flex items-center gap-1.5 transition-all ${
              activeTab === 'latency'
                ? 'bg-purple-900/80 border border-purple-400 text-white shadow-md'
                : 'bg-white/5 text-slate-400 hover:text-white'
            }`}
          >
            <Clock className="w-3.5 h-3.5 text-indigo-400" />
            <span>Latency</span>
          </button>
        </div>

        {/* Tab Contents */}
        {activeTab === 'pipeline' && (
          <div className="space-y-3 font-sans">
            {/* Card 01 */}
            <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-bold">01</span>
                  <Mic className="w-4 h-4 text-purple-400" />
                  <span className="font-bold text-white text-sm">Voice Ingestion &amp; STT Layer</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                  Sarvam AI + Web Audio API
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans pl-7">
                Real-time microphone capture via browser MediaRecorder (Opus WebM) with live 48-bar frequency waveform visualization. Streams directly to Sarvam AI STT for high-accuracy multilingual transcription across 14 Indic languages.
              </p>
            </div>

            {/* Card 02 */}
            <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-bold">02</span>
                  <Scissors className="w-4 h-4 text-pink-400" />
                  <span className="font-bold text-white text-sm">4 Vast Chunking Strategies</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                  Multi-Strategy Benchmark
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans pl-7">
                Evaluated across 4 distinct chunking paradigms on the MSMARCO-XI dataset: Semantic Chunking, Sentence-Window indexing, Recursive Character splitting, and Fixed-Size sliding windows.
              </p>
            </div>

            {/* Card 03 */}
            <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-bold">03</span>
                  <Zap className="w-4 h-4 text-amber-400" />
                  <span className="font-bold text-white text-sm">Vector Embedding Engine</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                  paraphrase-multilingual-MiniLM-L12-v2
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans pl-7">
                384-dimensional dense vectors with multilingual semantic alignment. Generates high-fidelity embeddings across all 14 Indic scripts in ~20ms.
              </p>
            </div>

            {/* Card 04 */}
            <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-bold">04</span>
                  <Database className="w-4 h-4 text-cyan-400" />
                  <span className="font-bold text-white text-sm">Fast 650k Vector Database</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                  FAISS IndexFlatIP (37.4ms)
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans pl-7">
                Indexed 509,110 passages (649,545 dense vector chunks) with normalized inner-product cosine similarity. Sub-40ms top-k retrieval across the entire dataset.
              </p>
            </div>

            {/* Card 05 */}
            <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-2">
              <div className="flex items-center justify-between font-mono text-xs">
                <div className="flex items-center gap-2">
                  <span className="px-2 py-0.5 rounded bg-purple-950 text-purple-300 font-bold">05</span>
                  <Cpu className="w-4 h-4 text-emerald-400" />
                  <span className="font-bold text-white text-sm">Natural Grounded Answer Generation</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-white/5 px-2.5 py-1 rounded-md border border-white/10">
                  Groq / Gemini / LM Studio
                </span>
              </div>
              <p className="text-xs text-slate-300 leading-relaxed font-sans pl-7">
                Generates clean, fluent answers in the exact language of the user's query. Output is rendered via progressive typewriter streaming, accompanied by dedicated source evidence cards.
              </p>
            </div>
          </div>
        )}

        {activeTab === 'guardrails' && (
          <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-3 font-sans text-xs text-slate-300">
            <h3 className="font-bold text-white font-mono text-sm">4-Tier Safety &amp; Grounding Guardrails</h3>
            <p>1. Prompt Injection &amp; Jailbreak Filter</p>
            <p>2. Untrusted Context XML Boundary Tagging</p>
            <p>3. Automatic Hallucination &amp; Claim Alignment Verification</p>
            <p>4. Source Attribution Integrity Check</p>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-3 font-sans text-xs text-slate-300">
            <h3 className="font-bold text-white font-mono text-sm">Edge Security &amp; Rate Limiting</h3>
            <p>• Maximum 5 requests / minute per client IP</p>
            <p>• Input token length ceiling (500 chars max)</p>
            <p>• Audio payload size thresholding (&lt; 10MB)</p>
          </div>
        )}

        {activeTab === 'languages' && (
          <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-3 font-sans text-xs text-slate-300">
            <h3 className="font-bold text-white font-mono text-sm">14 Supported Indic Languages &amp; English</h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 font-mono text-[11px] text-cyan-300">
              <div>• English (en)</div>
              <div>• Hindi (hi)</div>
              <div>• Bengali (bn)</div>
              <div>• Tamil (ta)</div>
              <div>• Telugu (te)</div>
              <div>• Marathi (mr)</div>
              <div>• Gujarati (gu)</div>
              <div>• Kannada (kn)</div>
              <div>• Malayalam (ml)</div>
              <div>• Punjabi (pa)</div>
              <div>• Odia (or)</div>
              <div>• Assamese (as)</div>
              <div>• Urdu (ur)</div>
              <div>• Sanskrit (sa)</div>
            </div>
          </div>
        )}

        {activeTab === 'latency' && (
          <div className="p-4 rounded-2xl bg-[#050310]/90 border border-purple-500/20 space-y-3 font-sans text-xs text-slate-300 font-mono">
            <h3 className="font-bold text-white font-mono text-sm">Sub-second Latency Telemetry</h3>
            <div className="space-y-1 text-xs">
              <div>• Sarvam STT Ingestion: ~1240ms</div>
              <div>• SentenceTransformer Embedding: ~20ms</div>
              <div>• FAISS Index Search: ~37.4ms</div>
              <div>• Groq Llama 3.1 8B Generation: ~350ms</div>
              <div>• Grounding Verification: ~15ms</div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
