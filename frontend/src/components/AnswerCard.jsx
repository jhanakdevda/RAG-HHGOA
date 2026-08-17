import React, { useState, useEffect } from 'react';
import { User, Sparkles, Copy, Check, Volume2, VolumeX, Pause, Play, CheckCircle2 } from 'lucide-react';
import { getLanguageName } from './LanguageSelector';

export default function AnswerCard({ response, query }) {
  const [copied, setCopied] = useState(false);
  const [speechState, setSpeechState] = useState('IDLE'); // 'IDLE' | 'PLAYING' | 'PAUSED'

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

    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(response.answer);
    
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

  const isGrounded = response.grounding_status === 'GROUNDED' || response.grounding_status === 'PARTIALLY_GROUNDED';

  return (
    <div className="w-full space-y-3 mb-4 animate-fadeIn font-sans">
      
      {/* 1. User Question */}
      <div className="clean-card p-3.5 border-l-2 border-l-purple-500 bg-[#090d1c]/80">
        <div className="text-[11px] font-mono text-purple-400 font-bold mb-1 flex items-center gap-1.5">
          <User className="w-3 h-3" /> YOU
        </div>
        <p className="text-slate-200 text-sm font-medium">
          {response.query || query}
        </p>
      </div>

      {/* 2. AI Answer */}
      <div className="clean-card p-4 border border-cyan-500/20 bg-[#0a1226]/90 relative">
        <div className="flex items-center justify-between pb-2 mb-3 border-b border-white/5 font-mono text-xs">
          <span className="flex items-center gap-1.5 font-bold text-cyan-400">
            <Sparkles className="w-3.5 h-3.5" /> AI ANSWER
          </span>

          <span className="text-[11px] text-slate-400">
            Language: <strong className="text-slate-200 font-normal">{getLanguageName(response.answer_language)}</strong>
          </span>
        </div>

        {/* Answer Text */}
        <div className="text-slate-100 text-sm sm:text-base leading-relaxed whitespace-pre-wrap font-normal mb-4">
          {response.answer}
        </div>

        {/* Bottom Actions Bar */}
        <div className="pt-2 border-t border-white/5 flex items-center justify-between font-mono text-xs gap-2">
          
          {/* Grounding Badge */}
          {isGrounded ? (
            <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 font-semibold border border-emerald-500/20">
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>✓ GROUNDED</span>
            </div>
          ) : (
            <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded bg-slate-500/10 text-slate-400">
              UNVERIFIED
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex items-center gap-2">
            <button
              onClick={handleCopy}
              className="px-2.5 py-1 rounded bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white text-xs font-mono flex items-center gap-1 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-400">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy</span>
                </>
              )}
            </button>

            <button
              onClick={handleTTS}
              className={`px-2.5 py-1 rounded border text-xs font-mono flex items-center gap-1 transition-colors ${
                speechState === 'PLAYING'
                  ? 'bg-cyan-500/20 border-cyan-400 text-cyan-300'
                  : 'bg-white/5 hover:bg-white/10 border-white/10 text-slate-300 hover:text-white'
              }`}
            >
              {speechState === 'PLAYING' ? (
                <>
                  <Pause className="w-3 h-3 text-cyan-400" />
                  <span>Pause</span>
                </>
              ) : (
                <>
                  <Volume2 className="w-3 h-3 text-cyan-400" />
                  <span>Listen</span>
                </>
              )}
            </button>
          </div>

        </div>

      </div>

    </div>
  );
}
