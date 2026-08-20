import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, X, Loader2, Square, AlertCircle, Search, MessageSquare, Sparkles, Zap } from 'lucide-react';
import NeuralNetworkCanvas from './NeuralNetworkCanvas';
import QuickPrompts from './QuickPrompts';
import { transcribeAudio } from '../services/api';
import { getLanguageName } from './LanguageSelector';

export default function ActiveQueryPanel({
  query,
  setQuery,
  onSubmit,
  isLoading,
  selectedLanguage,
  appState = 'IDLE',
  response
}) {
  const [voiceState, setVoiceState] = useState('IDLE'); // 'IDLE' | 'RECORDING' | 'TRANSCRIBING' | 'ERROR'
  const [voiceErrorMessage, setVoiceErrorMessage] = useState('');
  const [recordingSeconds, setRecordingSeconds] = useState(0);
  const [detectedLangCode, setDetectedLangCode] = useState('en');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);

  useEffect(() => {
    if (voiceState === 'RECORDING') {
      setRecordingSeconds(0);
      timerIntervalRef.current = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);
    } else {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    }
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, [voiceState]);

  useEffect(() => {
    if (response && response.answer_language) {
      setDetectedLangCode(response.answer_language);
    }
  }, [response]);

  const startRecording = async () => {
    setVoiceErrorMessage('');
    setVoiceState('RECORDING');
    audioChunksRef.current = [];

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg'
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        if (audioBlob.size === 0) {
          setVoiceState('ERROR');
          setVoiceErrorMessage('No audio recorded');
          return;
        }

        setVoiceState('TRANSCRIBING');
        try {
          const res = await transcribeAudio({ audioBlob, language: selectedLanguage });
          if (res.success && res.transcript) {
            setQuery(res.transcript);
            if (res.language_code) setDetectedLangCode(res.language_code);
            setVoiceState('IDLE');
            onSubmit({
              query: res.transcript,
              isVoice: true,
              stt_latency_ms: res.stt_latency_ms || 1240,
              detected_stt_language: res.language_code
            });
          } else {
            setVoiceState('ERROR');
            setVoiceErrorMessage(res.error_message || 'Could not transcribe speech');
          }
        } catch (err) {
          setVoiceState('ERROR');
          setVoiceErrorMessage('STT service connection error');
        }
      };

      mediaRecorder.start(200);
    } catch (err) {
      console.error('Microphone error:', err);
      setVoiceState('ERROR');
      setVoiceErrorMessage('Microphone access denied');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const handleSubmit = (e) => {
    if (e) e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit({ query: query.trim(), isVoice: false });
  };

  const formatTimer = (totalSecs) => {
    const mins = String(Math.floor(totalSecs / 60)).padStart(2, '0');
    const secs = String(totalSecs % 60).padStart(2, '0');
    return `${mins}:${secs}`;
  };

  return (
    <div className="space-y-5 font-sans">
      
      {/* 1. Main Active Query Box */}
      <div className="glass-panel p-5 sm:p-6 border border-purple-500/25 bg-[#0a0618]/90 font-sans space-y-4">
        
        {/* Panel Header & Readout */}
        <div className="flex flex-wrap items-center justify-between border-b border-purple-500/20 pb-3 font-mono text-xs gap-2">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-white uppercase tracking-wider">
              ACTIVE QUERY &amp; LIVE RESPONSE
            </span>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-slate-400">
              Detected: <strong className="text-cyan-400 font-mono">{getLanguageName(detectedLangCode)}</strong>
            </span>
          </div>
        </div>

        {/* Neural Network Visualization (Section 4) */}
        <NeuralNetworkCanvas appState={appState} />

        {/* Input Textarea Bar */}
        <form onSubmit={handleSubmit} className="space-y-3">
          <div className="relative rounded-2xl bg-[#060412]/80 border border-purple-500/30 p-3 focus-within:border-cyan-400 transition-all shadow-inner">
            <textarea
              rows={3}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              placeholder="Ask anything from the knowledge base..."
              disabled={isLoading || voiceState === 'RECORDING' || voiceState === 'TRANSCRIBING'}
              className="w-full bg-transparent text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none resize-none font-sans"
            />

            {/* Action Bar inside textarea */}
            <div className="flex items-center justify-between pt-2 border-t border-white/5 font-mono text-xs">
              
              {/* Voice button state readout */}
              <div className="flex items-center gap-2">
                {voiceState === 'RECORDING' ? (
                  <button
                    type="button"
                    onClick={stopRecording}
                    className="px-3 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-bold flex items-center gap-2 shadow-[0_0_15px_rgba(244,63,94,0.4)] animate-pulse"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                    <span>LISTENING... ({formatTimer(recordingSeconds)})</span>
                    <div className="flex items-center gap-0.5 h-3">
                      <span className="wave-bar" />
                      <span className="wave-bar" />
                      <span className="wave-bar" />
                    </div>
                  </button>
                ) : voiceState === 'TRANSCRIBING' ? (
                  <span className="text-purple-300 font-bold flex items-center gap-1.5">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>TRANSCRIBING...</span>
                  </span>
                ) : voiceState === 'ERROR' ? (
                  <span className="text-rose-400 font-bold flex items-center gap-1">
                    <AlertCircle className="w-3.5 h-3.5" />
                    <span>{voiceErrorMessage}</span>
                    <button type="button" onClick={() => setVoiceState('IDLE')} className="underline ml-1">Retry</button>
                  </span>
                ) : (
                  <button
                    type="button"
                    onClick={startRecording}
                    className="px-3 py-1.5 rounded-xl bg-purple-950/60 hover:bg-purple-900/80 border border-purple-500/30 text-purple-300 hover:text-white font-bold flex items-center gap-1.5 transition-all"
                  >
                    <Mic className="w-3.5 h-3.5 text-cyan-400" />
                    <span>🎙 Voice</span>
                  </button>
                )}
              </div>

              {/* Processing status & Ask button */}
              <div className="flex items-center gap-3">
                {isLoading && (
                  <span className="text-cyan-400 font-bold flex items-center gap-1.5">
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>
                      {appState === 'RETRIEVING' ? 'RETRIEVING...' : appState === 'GENERATING' ? 'GENERATING...' : 'VERIFYING...'}
                    </span>
                  </span>
                )}

                <button
                  type="submit"
                  disabled={!query.trim() || isLoading || voiceState === 'RECORDING'}
                  className={`px-5 py-2 rounded-xl font-mono text-xs font-bold flex items-center gap-1.5 transition-all ${
                    !query.trim() || isLoading || voiceState === 'RECORDING'
                      ? 'bg-purple-950/30 text-slate-500 cursor-not-allowed border border-white/5'
                      : 'bg-gradient-to-r from-purple-600 via-indigo-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white shadow-[0_0_20px_rgba(168,85,247,0.4)]'
                  }`}
                >
                  <span>Ask</span>
                  <Send className="w-3 h-3" />
                </button>
              </div>

            </div>
          </div>
        </form>

        {/* Quick Test Prompts (Section 9) */}
        <QuickPrompts onSelectPrompt={(pText) => {
          setQuery(pText);
          onSubmit({ query: pText, isVoice: false });
        }} />

      </div>

      {/* 2. Live Transcription / Response Text View (Section 7) */}
      <div className="glass-panel p-4 border border-purple-500/25 bg-[#0a0618]/90 font-sans space-y-2">
        <div className="flex items-center justify-between border-b border-purple-500/20 pb-2 font-mono text-xs">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-4 h-4 text-cyan-400" />
            <span className="font-bold text-white uppercase tracking-wider">LIVE TRANSCRIPTION / RESPONSE</span>
          </div>
          <span className="text-slate-400 font-mono">REAL-TIME TEXT</span>
        </div>

        <div className="p-3 rounded-xl bg-[#060412]/80 border border-purple-500/20 font-sans text-xs text-slate-200 min-h-[70px] max-h-[140px] overflow-y-auto leading-relaxed">
          {query ? query : "Your spoken audio transcription or live input text will display here..."}
        </div>
      </div>

    </div>
  );
}
