import React, { useState } from 'react';
import { ShieldCheck, Volume2, Copy, Check } from 'lucide-react';

export default function AnswerCard({ response, query }) {
  const [copied, setCopied] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  if (!response) return null;

  const answerText = response.answer || 'Grounded answer generation complete.';
  const rawQuery = query || response.query || 'What is a corporation?';
  const cleanQuery = rawQuery.replace(/^["']|["']$/g, '').trim();
  const isGrounded = response.grounding_status === 'GROUNDED' || !response.grounding_status;

  const handleCopy = () => {
    navigator.clipboard.writeText(answerText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleSpeak = () => {
    if ('speechSynthesis' in window) {
      if (isPlaying) {
        window.speechSynthesis.cancel();
        setIsPlaying(false);
        return;
      }
      const utterance = new SpeechSynthesisUtterance(answerText);
      utterance.onend = () => setIsPlaying(false);
      utterance.onerror = () => setIsPlaying(false);
      setIsPlaying(true);
      window.speechSynthesis.speak(utterance);
    }
  };

  return (
    <div className="w-full glass-panel p-6 sm:p-10 rounded-3xl border border-pink-500/30 bg-[#090615]/50 backdrop-blur-2xl shadow-[0_0_40px_rgba(255,46,147,0.15)] space-y-6 font-sans animate-fadeIn">
      
      {/* Card Header */}
      <div className="flex items-center justify-between border-b border-pink-500/20 pb-4">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-xl bg-emerald-950/80 border border-emerald-500/40 flex items-center justify-center">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <span className="font-bold text-white text-base sm:text-lg tracking-tight font-sans">
            Grounded AI Intelligence
          </span>
        </div>

        <span className="px-3.5 py-1 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 font-mono text-[10px] font-bold tracking-wider uppercase">
          GUARDRAIL: {isGrounded ? 'PASS' : 'FLAGGED'}
        </span>
      </div>

      {/* Transcribed Query Block */}
      <div className="p-4 sm:p-5 rounded-2xl bg-[#04020a]/60 border border-pink-500/20 space-y-1 font-sans">
        <div className="text-[10px] font-mono font-bold text-orange-400 uppercase tracking-widest">
          TRANSCRIBED QUERY
        </div>
        <p className="text-xs sm:text-sm text-slate-200 font-sans">
          "{cleanQuery}"
        </p>
      </div>

      {/* Answer Body Text */}
      <div className="py-2">
        <p className="text-sm sm:text-lg text-slate-100 font-sans leading-relaxed">
          {answerText}
        </p>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap items-center gap-3 pt-2 font-mono text-xs">
        <button
          onClick={handleSpeak}
          className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-200 hover:text-white font-sans text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
        >
          <Volume2 className={`w-4 h-4 ${isPlaying ? 'text-orange-400 animate-pulse' : 'text-pink-300'}`} />
          <span>{isPlaying ? 'Speaking...' : 'Listen Answer'}</span>
        </button>

        <button
          onClick={handleCopy}
          className="px-4 py-2.5 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-200 hover:text-white font-sans text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
        >
          {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4 text-pink-300" />}
          <span>{copied ? 'Copied!' : 'Copy Response'}</span>
        </button>
      </div>

    </div>
  );
}
