import React, { useState, useRef, useEffect } from 'react';
import { Mic, Send, X, Loader2, Square, AlertCircle } from 'lucide-react';
import { transcribeAudio } from '../services/api';

export default function MainQueryBox({
  query,
  setQuery,
  onSubmit,
  isLoading,
  selectedLanguage
}) {
  // Voice states: 'IDLE' | 'RECORDING' | 'TRANSCRIBING' | 'ERROR'
  const [voiceState, setVoiceState] = useState('IDLE');
  const [voiceErrorMessage, setVoiceErrorMessage] = useState('');

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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
            setVoiceState('IDLE');
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
          setVoiceErrorMessage('STT Service error');
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
    e.preventDefault();
    if (!query.trim() || isLoading) return;
    onSubmit({ query: query.trim(), isVoice: false });
  };

  return (
    <div className="w-full mb-4">
      <form onSubmit={handleSubmit} className="relative">
        <div className={`clean-card p-2 sm:p-3 transition-all ${
          voiceState === 'RECORDING' ? 'border-rose-500/50 shadow-[0_0_20px_rgba(244,63,94,0.15)]' : 'hover:border-white/20'
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
              className="w-full bg-transparent text-sm sm:text-base text-slate-100 placeholder-slate-400 focus:outline-none resize-none px-2 py-1 leading-relaxed font-sans"
            />

            {query && !isLoading && voiceState === 'IDLE' && (
              <button
                type="button"
                onClick={() => setQuery('')}
                className="p-1 text-slate-400 hover:text-slate-200 transition-colors mr-2 rounded hover:bg-white/5"
                title="Clear input"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Controls Bar at bottom of Query Box */}
          <div className="flex items-center justify-between pt-2 border-t border-white/5 px-1 gap-2">
            
            {/* Inline Status Feedback */}
            <div className="flex items-center gap-2 text-xs font-mono">
              {voiceState === 'RECORDING' && (
                <div className="flex items-center gap-2 text-rose-400 font-semibold">
                  <span className="rec-indicator" />
                  <span>Listening...</span>
                  <div className="flex items-center gap-0.5 h-3 ml-1">
                    <span className="small-wave-bar" />
                    <span className="small-wave-bar" />
                    <span className="small-wave-bar" />
                    <span className="small-wave-bar" />
                  </div>
                </div>
              )}

              {voiceState === 'TRANSCRIBING' && (
                <div className="flex items-center gap-1.5 text-cyan-400">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Transcribing...</span>
                </div>
              )}

              {voiceState === 'ERROR' && (
                <div className="flex items-center gap-1.5 text-rose-400 text-xs">
                  <AlertCircle className="w-3.5 h-3.5 shrink-0" />
                  <span>{voiceErrorMessage}</span>
                  <button
                    type="button"
                    onClick={() => setVoiceState('IDLE')}
                    className="underline text-[11px] ml-1 text-rose-300"
                  >
                    Reset
                  </button>
                </div>
              )}

              {isLoading && voiceState === 'IDLE' && (
                <div className="flex items-center gap-1.5 text-cyan-400">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  <span>Searching knowledge...</span>
                </div>
              )}
            </div>

            {/* Right Action Buttons */}
            <div className="flex items-center gap-2 ml-auto">
              
              {/* Microphone Toggle Button */}
              {voiceState === 'RECORDING' ? (
                <button
                  type="button"
                  onClick={stopRecording}
                  className="px-3 py-1.5 rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-mono text-xs font-semibold flex items-center gap-1.5 transition-colors"
                  aria-label="Stop voice input"
                >
                  <Square className="w-3 h-3 fill-current" />
                  <span>Done</span>
                </button>
              ) : (
                <button
                  type="button"
                  onClick={startRecording}
                  disabled={isLoading || voiceState === 'TRANSCRIBING'}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono flex items-center gap-1.5 transition-all ${
                    voiceState === 'TRANSCRIBING'
                      ? 'bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 cursor-not-allowed'
                      : 'bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white'
                  }`}
                  aria-label="Start voice input"
                  title="Ask with voice"
                >
                  <Mic className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Voice</span>
                </button>
              )}

              {/* Ask/Send Submit Button */}
              <button
                type="submit"
                disabled={!query.trim() || isLoading || voiceState === 'RECORDING'}
                className={`px-4 py-1.5 rounded-lg font-semibold text-xs flex items-center gap-1.5 transition-all font-mono ${
                  !query.trim() || isLoading || voiceState === 'RECORDING'
                    ? 'bg-white/5 border border-white/5 text-slate-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white shadow-[0_0_12px_rgba(0,240,255,0.25)]'
                }`}
                aria-label="Submit question"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>Ask</span>
                    <Send className="w-3 h-3" />
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
