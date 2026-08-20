import React, { useState } from 'react';
import { Settings, X, Mic, Zap, Search, Cpu, ShieldCheck, Lock, Globe, Clock, ChevronDown, ChevronUp } from 'lucide-react';

export default function HowItWorks({ isOpen, onToggle }) {
  const [activeTab, setActiveTab] = useState('pipeline');

  if (!isOpen) return null;

  const tabs = [
    { id: 'pipeline', label: 'Pipeline', icon: Zap },
    { id: 'guardrails', label: 'Guardrails', icon: ShieldCheck },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'languages', label: '4 Languages', icon: Globe },
    { id: 'latency', label: 'Latency', icon: Clock }
  ];

  const pipelineCards = [
    {
      step: '01',
      title: 'Voice Ingestion & STT Layer',
      techPill: 'Sarvam AI + Web Audio API',
      icon: Mic,
      desc: 'Real-time microphone capture via browser MediaRecorder (Opus WebM) with live frequency waveform visualization. Streams directly to Sarvam AI STT for high-accuracy multilingual transcription across Indic languages.'
    },
    {
      step: '02',
      title: 'Multilingual Chunking & Preprocessing',
      techPill: 'Sentence-Boundary Preservation',
      icon: Zap,
      desc: 'Evaluated across sentence-boundary paradigms on MS MARCO-XI. Computes inter-sentence cosine similarity and splits at natural semantic topic shifts, preserving Devanagari purna viram (।) and Unicode punctuation.'
    },
    {
      step: '03',
      title: 'Vector Embedding Engine',
      techPill: 'paraphrase-multilingual-MiniLM-L12-v2',
      icon: Zap,
      desc: '384-dimensional dense vectors with cross-lingual semantic alignment. Generates high-fidelity embeddings across English, Hindi, Marathi, and Gujarati in ~13ms.'
    },
    {
      step: '04',
      title: 'Fast 21.5k Vector Database',
      techPill: 'FAISS IndexFlatIP (25ms)',
      icon: Search,
      desc: 'Indexed 21,573 dense vector chunks with normalized inner-product cosine similarity. Sub-25ms top-k retrieval across the entire authentic evidence dataset.'
    },
    {
      step: '05',
      title: 'Groq Llama 3.1 8B LLM Engine',
      techPill: 'Groq LPU (Sub-Second)',
      icon: Cpu,
      desc: 'Ultra-fast LLM answer synthesis with context-bounded prompt templates, returning grounded answers with exact source attribution.'
    },
    {
      step: '06',
      title: 'Grounding Verification Engine',
      techPill: 'Semantic Similarity Fallback',
      icon: ShieldCheck,
      desc: 'Automated claim verification engine evaluating sentence-level coverage ratio and cross-lingual vector similarity to prevent hallucinations and unverified claims.'
    }
  ];

  const guardrailCards = [
    {
      step: '01',
      title: 'Safety Filter Screening',
      techPill: 'Unsafe Query Gate',
      desc: 'Screens incoming user queries against safety policies prior to vector retrieval or LLM execution.'
    },
    {
      step: '02',
      title: 'Prompt Injection Defense',
      techPill: 'XML Boundary Tagging',
      desc: 'Encloses retrieved context inside strictly escaped untrusted XML boundary tags to prevent adversarial prompt injection.'
    },
    {
      step: '03',
      title: 'Grounding Verification',
      techPill: 'Hallucination Barrier',
      desc: 'Cross-lingual embedding similarity verification to ensure generated answers strictly align with retrieved evidence.'
    }
  ];

  const securityCards = [
    {
      step: '01',
      title: 'CORS & Rate Limiter',
      techPill: 'Circuit Breaker Cooldown',
      desc: 'Configurable production CORS middleware and 30-second circuit-breaker cooldown protection against API abuse.'
    },
    {
      step: '02',
      title: 'Non-Persisted Voice Data',
      techPill: 'In-Memory Stream',
      desc: 'User audio recordings are processed in-memory for STT transcription and immediately discarded.'
    }
  ];

  const languageCards = [
    { step: '01', title: 'English (en)', techPill: 'Default Language', desc: 'Primary language for global queries and fallback generation.' },
    { step: '02', title: 'हिन्दी (hi)', techPill: 'Sarvam hi-IN', desc: 'Full support for Hindi queries, STT, and Devanagari text retrieval.' },
    { step: '03', title: 'मराठी (mr)', techPill: 'Sarvam mr-IN', desc: 'Full support for Marathi queries, STT, and Devanagari text retrieval.' },
    { step: '04', title: 'ગુજરાતી (gu)', techPill: 'Sarvam gu-IN', desc: 'Full support for Gujarati queries, STT, and Gujarati script retrieval.' }
  ];

  const latencyCards = [
    { step: '01', title: 'Query Embedding Latency', techPill: '13.2 ms', desc: 'Paraphrase-multilingual-MiniLM sentence transformation.' },
    { step: '02', title: 'FAISS Dense Search Latency', techPill: '3.6 ms', desc: 'Dense vector L2 inner product search across 21.5k vectors.' },
    { step: '03', title: 'Groq LLM Generation Latency', techPill: '~900 ms', desc: 'Groq Llama 3.1 8B sub-second inference engine.' },
    { step: '04', title: 'Grounding Verification Latency', techPill: '< 2.0 ms', desc: 'Fast-path lexical & semantic embedding alignment evaluation.' }
  ];

  const renderActiveTabContent = () => {
    let currentCards = pipelineCards;
    if (activeTab === 'guardrails') currentCards = guardrailCards;
    if (activeTab === 'security') currentCards = securityCards;
    if (activeTab === 'languages') currentCards = languageCards;
    if (activeTab === 'latency') currentCards = latencyCards;

    return (
      <div className="space-y-3 font-sans">
        {currentCards.map((card, idx) => {
          const Icon = card.icon || Zap;
          return (
            <div
              key={idx}
              className="p-4 rounded-xl bg-[#0c081d]/90 border border-purple-500/25 hover:border-purple-500/40 transition-all shadow-md font-sans"
            >
              <div className="flex flex-wrap items-center justify-between gap-2 mb-2 font-mono text-xs">
                <div className="flex items-center gap-2.5">
                  <span className="px-2.5 py-0.5 rounded-lg bg-purple-950/60 border border-purple-500/30 text-purple-300 font-bold text-xs">
                    {card.step}
                  </span>
                  <div className="flex items-center gap-1.5 font-bold text-white text-sm font-sans">
                    <Icon className="w-4 h-4 text-purple-400" />
                    <span>{card.title}</span>
                  </div>
                </div>

                <span className="px-2.5 py-0.5 rounded-full bg-white/5 border border-white/10 text-slate-300 font-mono text-[11px]">
                  {card.techPill}
                </span>
              </div>

              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed font-sans mt-2">
                {card.desc}
              </p>
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <section id="how-it-works" className="w-full mt-10 mb-12 animate-fadeIn font-sans">
      
      {/* Signature Outer Modal/Card matching Image 2 */}
      <div className="glass-panel p-6 sm:p-8 border border-purple-500/30 bg-[#0a0618]/95 shadow-[0_0_50px_rgba(168,85,247,0.15)] relative">
        
        {/* Header matching Image 2 */}
        <div className="flex items-start justify-between pb-4 mb-5 border-b border-purple-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-900/40 border border-purple-500/40 flex items-center justify-center text-purple-300 shadow-[0_0_15px_rgba(168,85,247,0.3)]">
              <Settings className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg sm:text-xl font-extrabold text-white tracking-tight font-sans">
                System Architecture &amp; Technical Specs
              </h2>
              <p className="text-xs text-slate-400 font-sans mt-0.5">
                End-to-end pipeline, 4-tier guardrails, edge security &amp; telemetry
              </p>
            </div>
          </div>

          <button
            onClick={onToggle}
            className="p-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
            title="Close architecture"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tabbed Navigation Bar matching Image 2 */}
        <div className="flex flex-wrap items-center gap-2 mb-6 font-mono text-xs">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 rounded-xl font-mono text-xs font-semibold flex items-center gap-2 transition-all ${
                  isActive
                    ? 'bg-purple-600 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)] border border-purple-400'
                    : 'bg-purple-950/30 hover:bg-purple-900/40 text-slate-300 border border-purple-500/20'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : 'text-purple-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Active Tab Content */}
        {renderActiveTabContent()}

      </div>

    </section>
  );
}
