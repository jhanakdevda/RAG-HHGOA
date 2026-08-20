import React from 'react';
import AntiGravityLatticeCanvas from './AntiGravityLatticeCanvas';
import TrustRadarCanvas from './TrustRadarCanvas';
import CometVortexCanvas from './CometVortexCanvas';
import AnswerCard from './AnswerCard';
import SourcesAccordion from './SourcesAccordion';
import TechnicalDetails from './TechnicalDetails';
import MainQueryBox from './MainQueryBox';
import { Sparkles, MessageSquare, ShieldCheck, Zap } from 'lucide-react';

export default function LiveWorkspace({
  query,
  setQuery,
  onSubmit,
  isLoading,
  selectedLanguage,
  response,
  sttLatency
}) {
  const currentAnswer = response && response.answer ? response.answer : 'आप भारत के बारे में बताएं... भारत एक विशाल और विविध देश है जिसमें समृद्ध संस्कृति, इतिहास और भूगोल है।';
  const currentSources = response && response.sources ? response.sources : [
    { chunk_id: 'src_1', domain: 'MS MARCO-XI', similarity_score: 0.812, text_snippet: 'भारत एक दक्षिण एशियाई देश है जिसमें 28 राज्य और 8 केंद्र शासित प्रदेश हैं।' },
    { chunk_id: 'src_2', domain: 'MS MARCO-XI', similarity_score: 0.745, text_snippet: 'India is the world\'s most populous democracy with ancient civilational heritage.' },
    { chunk_id: 'src_3', domain: 'Groq Llama 3.1 8B', similarity_score: 0.702, text_snippet: 'Sub-second LLM answer generation grounded strictly in retrieved context passages.' }
  ];

  const groundingScore = response && response.grounding_score ? response.grounding_score : 0.85;
  const groundingStatus = response && response.grounding_status ? response.grounding_status : 'GROUNDED';

  return (
    <main className="flex-1 space-y-6 font-sans min-w-0">
      
      {/* 1. Live Info Workspace (3D Lattice + Grounded Answer Shard) matching Image 13 */}
      <div className="glass-panel p-5 sm:p-6 border border-purple-500/30 bg-[#0a0618]/90 relative shadow-[0_0_40px_rgba(168,85,247,0.15)]">
        <div className="flex items-center justify-between border-b border-purple-500/20 pb-3 mb-4 font-mono text-xs">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-white tracking-widest uppercase">
              Live Info Workspace
            </span>
          </div>
          <span className="text-purple-300">Anti-Gravity Neural Mesh</span>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 items-center">
          
          {/* Left: Dynamic 3D Fractal Lattice Sphere */}
          <div className="relative rounded-2xl p-4 bg-[#060412]/80 border border-cyan-500/20 shadow-inner flex flex-col items-center justify-center">
            <span className="absolute top-3 left-3 text-[10px] font-mono text-cyan-400 font-bold uppercase">
              3D Neural Lattice Sphere
            </span>
            <AntiGravityLatticeCanvas />
          </div>

          {/* Right: Floating "Grounded Answer & Attribution" Data Shard */}
          <div className="p-4 rounded-2xl bg-[#0c0820]/90 border border-purple-500/30 shadow-lg space-y-3 font-sans relative">
            
            <div className="flex items-center justify-between border-b border-purple-500/20 pb-2 font-mono text-xs">
              <span className="font-bold text-white uppercase tracking-wider">
                Grounded Answer &amp; Attribution
              </span>
              <span className="px-2 py-0.5 rounded bg-emerald-950/60 text-emerald-400 font-bold text-[10px]">
                {groundingStatus}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              {/* Summary text shard */}
              <div className="sm:col-span-2 space-y-1 font-sans text-xs text-slate-200 leading-relaxed max-h-44 overflow-y-auto pr-1">
                <div className="text-[10px] font-mono text-cyan-400 font-bold">SUMMARY</div>
                <p>{currentAnswer}</p>
              </div>

              {/* Source Attribution column */}
              <div className="space-y-1.5 font-mono text-[11px]">
                <div className="text-[10px] font-mono text-purple-300 font-bold">SOURCE ATTRIBUTION</div>
                {currentSources.slice(0, 3).map((src, i) => (
                  <div key={i} className="p-1.5 rounded-lg bg-white/5 border border-white/10 text-[10px] space-y-0.5">
                    <div className="text-cyan-400 font-bold truncate">Source {i + 1}: {src.domain || 'MS MARCO-XI'}</div>
                    <div className="text-slate-400 truncate">{src.text_snippet || src.text}</div>
                  </div>
                ))}
              </div>
            </div>

          </div>

        </div>
      </div>

      {/* 2. Middle Row: Live Transcription & Grounding Trust Radar */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Live Transcription Panel */}
        <div className="glass-panel p-5 border border-purple-500/25 bg-[#0a0618]/90 font-sans space-y-3">
          <div className="flex items-center justify-between border-b border-purple-500/20 pb-2 font-mono text-xs">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-cyan-400" />
              <span className="font-bold text-white uppercase tracking-wider">Live Transcription</span>
            </div>
            <span className="text-xs text-slate-400 font-mono">Indic STT</span>
          </div>

          <div className="p-4 rounded-xl bg-[#060412]/80 border border-purple-500/20 font-sans text-sm text-slate-100 min-h-[120px] flex items-center justify-center text-center">
            {query || "आप भारत के बारे में बताएं ... (Speak or type your question)"}
          </div>
        </div>

        {/* Grounding & Hallucination Check (Trust Radar Spider Chart) */}
        <div className="glass-panel p-5 border border-purple-500/25 bg-[#0a0618]/90 font-sans space-y-3">
          <div className="flex items-center justify-between border-b border-purple-500/20 pb-2 font-mono text-xs">
            <div className="flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span className="font-bold text-white uppercase tracking-wider">Grounding &amp; Hallucination Check</span>
            </div>
            <span className="text-xs text-emerald-400 font-mono">View: 3D Holographic</span>
          </div>

          <TrustRadarCanvas score={groundingScore} status={groundingStatus} />
        </div>

      </div>

      {/* 3. Bottom Row: Recent & Sample Questions (Knowledge Comet Trail) & Quick Test Console */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Knowledge Comet Trail */}
        <div className="glass-panel p-5 border border-purple-500/25 bg-[#0a0618]/90 font-sans space-y-3">
          <div className="flex items-center justify-between border-b border-purple-500/20 pb-2 font-mono text-xs">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span className="font-bold text-white uppercase tracking-wider">Knowledge Comet Trail</span>
            </div>
            <span className="text-xs text-purple-300 font-mono">Spiral Vortex</span>
          </div>

          <CometVortexCanvas onSelectQuestion={(q) => setQuery(q)} />
        </div>

        {/* Quick Test Prompts Console */}
        <MainQueryBox
          query={query}
          setQuery={setQuery}
          onSubmit={onSubmit}
          isLoading={isLoading}
          selectedLanguage={selectedLanguage}
        />

      </div>

      {/* Actual Live Response Cards (if response exists) */}
      {response && response.answer && (
        <div className="space-y-6">
          <AnswerCard response={response} query={query} />
          <SourcesAccordion sources={response.sources} />
          <TechnicalDetails response={response} sttLatency={sttLatency} />
        </div>
      )}

    </main>
  );
}
