import React, { useState, useEffect } from 'react';
import { User, Sparkles, Copy, Check, Volume2, VolumeX, Pause, Play, ShieldCheck, CheckCircle2 } from 'lucide-react';
import { getLanguageName } from './LanguageSelector';

export default function AnswerCard({ response, query }) {
  const [copied, setCopied] = useState(false);
  const [speechState, setSpeechState] = useState('IDLE'); // 'IDLE' | 'PLAYING' | 'PAUSED'

  // Reset speech state when response changes
  useEffect(() => {
    setSpeechState('IDLE');
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }, [response]);

  if (!response || !response.answer) return null;

  const handleCopy = () => {
    if (response.answer) {
      navigator.clipboard.writeText(response.answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleTTS = () => {
    if (!('speechSynthesis' in window)) return;

    if (speechState === 'PLAYING') {
      window.speechSynthesis.pause();
      setSpeechState('PAUSED');
      return;
    }

    if (speechState === 'PAUSED') {
      window.speechSynthesis.resume();
      setSpeechState('PLAYING');
      return;
    }

    // Start fresh utterance
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(response.answer);
    
    // Attempt language code matching
    const langCode = response.answer_language || 'en';
    utterance.lang = langCode.startsWith('hi') ? 'hi-IN' :
                     langCode.startsWith('ta') ? 'ta-IN' :
                     langCode.startsWith('te') ? 'te-IN' :
                     langCode.startsWith('bn') ? 'bn-IN' :
                     langCode.startsWith('mr') ? 'mr-IN' : 'en-US';

    utterance.onend = () => setSpeechState('IDLE');
    utterance.onerror = () => setSpeechState('IDLE');

    window.speechSynthesis.speak(utterance);
    setSpeechState('PLAYING');
  };

  const stopTTS = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setSpeechState('IDLE');
  };

  const isGrounded = response.grounding_status === 'GROUNDED' || response.grounding_status === 'PARTIALLY_GROUNDED';
  const langDisplay = getLanguageName(response.answer_language || response.detected_language);

  return (
    <div className="w-full space-y-4 mb-6 animate-fadeIn">
      
      {/* 1. User Question Card */}
      <div className="glass-card p-4 border-l-4 border-l-purple-500 bg-[#090e21]/70">
        <div className="flex items-center justify-between mb-1.5 font-mono text-xs">
          <span className="flex items-center gap-1.5 text-purple-400 font-bold tracking-wider">
            <User className="w-3.5 h-3.5" />
            YOU
          </span>
          <span className="text-slate-500 text-[11px]">Just now</span>
        </div>
        <p className="text-slate-100 text-sm sm:text-base font-medium leading-relaxed">
          {response.query || query}
        </p>
      </div>

      {/* 2. AI Answer Card */}
      <div className="glass-card p-5 border border-cyan-500/30 bg-[#0a1329]/90 shadow-[0_10px_40px_-15px_rgba(0,240,255,0.15)] relative">
        
        {/* Header Bar */}
        <div className="flex items-center justify-between pb-3 mb-4 border-b border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center">
              <Sparkles className="w-4 h-4 text-cyan-400" />
            </div>
            <span className="font-mono font-bold text-xs sm:text-sm text-cyan-400 tracking-wider">
              AI ANSWER
            </span>
          </div>

          {/* Action Controls */}
          <div className="flex items-center gap-2">
            
            {/* Copy Button */}
            <button
              onClick={handleCopy}
              className="px-2.5 py-1.5 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1.5 transition-colors"
              title="Copy answer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400 font-semibold">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>

            {/* TTS Listen Button */}
            <div className="flex items-center gap-1">
              <button
                onClick={handleTTS}
                className={`px-2.5 py-1.5 rounded-lg border text-xs font-mono flex items-center gap-1.5 transition-all ${
                  speechState === 'PLAYING'
                    ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300 shadow-[0_0_12px_rgba(0,240,255,0.3)]'
                    : 'bg-white/5 hover:bg-white/10 border-white/10 text-slate-300 hover:text-white'
                }`}
                title="Listen to answer"
              >
                {speechState === 'PLAYING' ? (
                  <>
                    <Pause className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Pause</span>
                  </>
                ) : speechState === 'PAUSED' ? (
                  <>
                    <Play className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Resume</span>
                  </>
                ) : (
                  <>
                    <Volume2 className="w-3.5 h-3.5 text-cyan-400" />
                    <span>Listen</span>
                  </>
                )}
              </button>

              {speechState !== 'IDLE' && (
                <button
                  onClick={stopTTS}
                  className="p-1.5 rounded-lg bg-rose-500/20 border border-rose-500/40 text-rose-300 hover:text-rose-100"
                  title="Stop playback"
                >
                  <VolumeX className="w-3.5 h-3.5" />
                </button>
              )}
            </div>

          </div>
        </div>

        {/* Answer Content */}
        <div className="text-slate-100 text-sm sm:text-base leading-relaxed whitespace-pre-wrap font-normal mb-5">
          {response.answer}
        </div>

        {/* Bottom Grounding Badge */}
        <div className="pt-3 border-t border-white/5 flex flex-wrap items-center justify-between gap-2 font-mono text-xs">
          {isGrounded ? (
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 font-semibold">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>✓ GROUNDED</span>
            </div>
          ) : (
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-slate-500/15 border border-slate-500/30 text-slate-400">
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>UNVERIFIED</span>
            </div>
          )}

          <span className="text-slate-400 text-[11px]">
            Answer generated in <span className="text-slate-200 font-semibold">{langDisplay}</span>
          </span>
        </div>

      </div>

    </div>
  );
}
