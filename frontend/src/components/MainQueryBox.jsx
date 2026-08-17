import React, { useState, useRef, useEffect } from 'react';
import { Mic, MicOff, Send, X, AlertCircle, Loader2, Square } from 'lucide-react';
import { transcribeAudio } from '../services/api';

export default function MainQueryBox({
  query,
  setQuery,
  onSubmit,
  isLoading,
  selectedLanguage,
  onStartVoice,
  onEndVoice
}) {
  // Voice states: 'IDLE' | 'RECORDING' | 'TRANSCRIBING' | 'ERROR'
  const [voiceState, setVoiceState] = useState('IDLE');
  const [voiceErrorMessage, setVoiceErrorMessage] = useState('');
  const [recordingSeconds, setRecordingSeconds] = useState(0);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerIntervalRef = useRef(null);

  // Clean up timer on unmount
  useEffect(() => {
    return () => {
      if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    };
  }, []);

  const startRecording = async () => {
    setVoiceErrorMessage('');
    setVoiceState('RECORDING');
    setRecordingSeconds(0);
    audioChunksRef.current = [];

    if (onStartVoice) onStartVoice();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/ogg' });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        // Stop audio tracks
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
            setVoiceState('IDLE');
            // Auto submit with STT latency telemetry
            onSubmit({
              query: res.transcript,
              isVoice: true,
              stt_latency_ms: res.stt_latency_ms || 1240,
              detected_stt_language: res.language_code
            });
          } else {
            setVoiceState('ERROR');
            setVoiceErrorMessage(res.error_message || 'Could not understand audio');
          }
        } catch (err) {
          setVoiceState('ERROR');
          setVoiceErrorMessage('STT Service unreachable');
        }
      };

      mediaRecorder.start(200);

      // Start elapsed timer
      timerIntervalRef.current = setInterval(() => {
        setRecordingSeconds(prev => prev + 1);
      }, 1000);

    } catch (err) {
      console.error('Microphone access error:', err);
      setVoiceState('ERROR');
      setVoiceErrorMessage('Microphone access denied or unavailable');
    }
  };

  const stopRecording = () => {
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      mediaRecorderRef.current.stop();
    }
  };

  const cancelRecording = () => {
    if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.onstop = null;
      if (mediaRecorderRef.current.state !== 'inactive') {
        mediaRecorderRef.current.stop();
      }
    }
    setVoiceState('IDLE');
    setRecordingSeconds(0);
    if (onEndVoice) onEndVoice();
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit({ query: query.trim(), isVoice: false });
  };

  const formatTimer = (secs) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="w-full mb-6">
      <form onSubmit={handleSubmit} className="relative">
        <div className={`glass-card p-2 sm:p-3 transition-all ${
          voiceState === 'RECORDING' ? 'border-rose-500/50 shadow-[0_0_25px_rgba(239,68,68,0.2)]' : 'hover:border-cyan-500/30'
        }`}>
          
          {/* Main Input Textarea */}
          <div className="relative flex items-center">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit(e);
                }
              }}
              placeholder="Ask anything about the knowledge base..."
              disabled={isLoading || voiceState === 'RECORDING' || voiceState === 'TRANSCRIBING'}
              rows={2}
              className="w-full bg-transparent text-sm sm:text-base text-slate-100 placeholder-slate-400 focus:outline-none resize-none px-3 py-2 leading-relaxed"
            />
            
            {/* Clear query button */}
            {query && !isLoading && voiceState === 'IDLE' && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="p-1.5 text-slate-400 hover:text-slate-200 transition-colors mr-2 rounded-lg hover:bg-white/5"
                title="Clear input"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Controls Bar at bottom of Query Box */}
          <div className="flex flex-wrap items-center justify-between pt-2 border-t border-white/5 px-2 gap-2">
            
            {/* Left Voice Status Feedback */}
            <div className="flex items-center gap-2 font-mono text-xs">
              {voiceState === 'IDLE' && (
                <span className="text-slate-400 hidden sm:inline">Ask with voice or type text</span>
              )}

              {voiceState === 'RECORDING' && (
                <div className="flex items-center gap-2.5 text-rose-400 font-semibold">
                  <span className="flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
                    Listening...
                  </span>
                  <span className="text-white/40">|</span>
                  <div className="flex items-center gap-1 h-4">
                    <span className="wave-bar" />
                    <span className="wave-bar" />
                    <span className="wave-bar" />
                    <span className="wave-bar" />
                    <span className="wave-bar" />
                    <span className="wave-bar" />
                  </div>
                  <span className="text-slate-300 font-bold ml-1">{formatTimer(recordingSeconds)}</span>
                </div>
              )}

              {voiceState === 'TRANSCRIBING' && (
                <div className="flex items-center gap-2 text-cyan-400 font-medium">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Transcribing speech via Sarvam...</span>
                </div>
              )}

              {voiceState === 'ERROR' && (
                <div className="flex items-center gap-1.5 text-rose-400">
                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                  <span>{voiceErrorMessage || 'Could not understand audio'}</span>
                  <button
                    type="button"
                    onClick={() => setVoiceState('IDLE')}
                    className="underline text-xs text-rose-300 hover:text-rose-100 ml-2"
                  >
                    Reset
                  </button>
                </div>
              )}
            </div>

            {/* Right Action Buttons */}
            <div className="flex items-center gap-2.5 ml-auto">
              
              {/* Microphone Toggle Button */}
              {voiceState === 'RECORDING' ? (
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={stopRecording}
                    className="px-3.5 py-1.5 rounded-xl bg-rose-600 hover:bg-rose-500 text-white font-mono text-xs font-semibold flex items-center gap-1.5 shadow-[0_0_15px_rgba(239,68,68,0.4)] transition-all"
                    aria-label="Stop voice input"
                  >
                    <Square className="w-3.5 h-3.5 fill-current" />
                    <span>Done</span>
                  </button>

                  <button
                    type="button"
                    onClick={cancelRecording}
                    className="px-2.5 py-1.5 rounded-xl bg-white/10 hover:bg-white/20 text-slate-300 text-xs font-mono transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              ) : (
                <button
                  type="button"
                  onClick={startRecording}
                  disabled={isLoading || voiceState === 'TRANSCRIBING'}
                  className={`w-10 h-10 rounded-xl flex items-center justify-center transition-all ${
                    voiceState === 'TRANSCRIBING'
                      ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-400 cursor-not-allowed'
                      : 'bg-gradient-to-br from-cyan-500/20 via-purple-500/20 to-blue-500/20 hover:from-cyan-500/30 hover:to-purple-500/30 border border-cyan-500/40 text-cyan-300 hover:text-white shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                  }`}
                  aria-label="Start voice input"
                  title="Ask with voice"
                >
                  <Mic className="w-5 h-5" />
                </button>
              )}

              {/* Ask/Send Submit Button */}
              <button
                type="submit"
                disabled={!query.trim() || isLoading || voiceState === 'RECORDING'}
                className={`px-5 py-2 rounded-xl font-semibold text-xs sm:text-sm flex items-center gap-2 transition-all font-mono ${
                  !query.trim() || isLoading || voiceState === 'RECORDING'
                    ? 'bg-white/5 border border-white/10 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_20px_rgba(0,240,255,0.3)] hover:scale-[1.02]'
                }`}
                aria-label="Submit question"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>Ask</span>
                    <Send className="w-3.5 h-3.5" />
                  </>
                )}
              </button>

            </div>

          </div>

        </div>
      </form>
    </div>
  );
}
