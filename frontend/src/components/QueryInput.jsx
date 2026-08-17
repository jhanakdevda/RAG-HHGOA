import React, { useState, useRef } from 'react';
import { Mic, MicOff, Send, Globe, ChevronDown, AlertCircle } from 'lucide-react';
import { transcribeAudio } from '../services/api';

export const SUPPORTED_LANGUAGES = [
  { code: 'auto', name: 'Auto / Detect' },
  { code: 'en', name: 'English' },
  { code: 'hi', name: 'Hindi (हिन्दी)' },
  { code: 'mr', name: 'Marathi (मराठी)' },
  { code: 'bn', name: 'Bengali (বাংলা)' },
  { code: 'ta', name: 'Tamil (தமிழ்)' },
  { code: 'te', name: 'Telugu (తెలుగు)' },
  { code: 'gu', name: 'Gujarati (ગુજરાતી)' },
  { code: 'kn', name: 'Kannada (कन्नड़)' },
  { code: 'ml', name: 'Malayalam (മലയാളം)' },
  { code: 'pa', name: 'Punjabi (ਪੰਜਾਬੀ)' },
  { code: 'or', name: 'Odia (ଓଡ଼ిଆ)' },
  { code: 'ur', name: 'Urdu (اردو)' },
  { code: 'as', name: 'Assamese (অসমীয়া)' },
  { code: 'ne', name: 'Nepali (नेपाली)' }
];

export function detectLanguage(text) {
  if (!text || typeof text !== 'string') return 'en';
  
  if (/[\u0980-\u09FF]/.test(text)) return 'bn';
  if (/[\u0B80-\u0BFF]/.test(text)) return 'ta';
  if (/[\u0C00-\u0C7F]/.test(text)) return 'te';
  if (/[\u0A80-\u0AFF]/.test(text)) return 'gu';
  if (/[\u0C80-\u0CFF]/.test(text)) return 'kn';
  if (/[\u0D00-\u0D7F]/.test(text)) return 'ml';
  if (/[\u0A00-\u0A7F]/.test(text)) return 'pa';
  if (/[\u0B00-\u0B7F]/.test(text)) return 'or';
  if (/[\u0600-\u06FF]/.test(text)) return 'ur';
  
  if (/[\u0900-\u097F]/.test(text)) {
    const marathiKeywords = /\b(आहे|आहेत|कोणती|कोणता|काय|वेगाने|उडतो|कसा|केव्हा|कोठे|म्हणजे|नमस्कार|गोव्याची|महाराष्ट्राची|भारताची)\b/i;
    if (marathiKeywords.test(text)) {
      return 'mr';
    }
    return 'hi';
  }
  
  return 'en';
}

export default function QueryInput({ onSubmit, isLoading }) {
  const [query, setQuery] = useState('');
  const [selectedLang, setSelectedLang] = useState('auto');
  const [detectedLang, setDetectedLang] = useState(null);

  const [recordingState, setRecordingState] = useState('IDLE'); // IDLE, RECORDING, STOPPING, TRANSCRIBING
  const [sttError, setSttError] = useState(null);
  const [sttLatency, setSttLatency] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const getEffectiveLang = (textInput = query) => {
    if (selectedLang !== 'auto') return selectedLang;
    return detectLanguage(textInput);
  };

  const getSelectedLangLabel = () => {
    if (selectedLang !== 'auto') {
      const match = SUPPORTED_LANGUAGES.find((l) => l.code === selectedLang);
      return match ? match.name : 'English';
    }
    if (detectedLang) {
      const match = SUPPORTED_LANGUAGES.find((l) => l.code === detectedLang);
      return `Auto (${match ? match.name : 'English'})`;
    }
    return 'Auto / Detect';
  };

  const handleSubmit = (e, overrideQuery = null) => {
    if (e) e.preventDefault();
    const activeQuery = overrideQuery !== null ? overrideQuery : query;
    if (!activeQuery.trim() || isLoading || recordingState !== 'IDLE') return;

    const langCode = getEffectiveLang(activeQuery);
    setDetectedLang(langCode);
    setSttLatency(null);

    onSubmit({
      query: activeQuery.trim(),
      top_k: 3,
      preferred_answer_language: langCode,
      language_filter: langCode === 'en' ? null : langCode,
      stt_latency_ms: null
    });
  };

  const startRecording = async () => {
    setSttError(null);
    setSttLatency(null);
    audioChunksRef.current = [];

    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        console.error('[VOICE] Microphone permission not granted or mediaDevices unavailable');
        throw new Error('Microphone permission is required for voice input.');
      }

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mimeTypes = [
        'audio/webm;codecs=opus',
        'audio/webm',
        'audio/mp4',
        'audio/ogg;codecs=opus',
        'audio/wav'
      ];
      let mimeType = '';
      for (const m of mimeTypes) {
        if (MediaRecorder.isTypeSupported(m)) {
          mimeType = m;
          break;
        }
      }

      console.log('[VOICE] Recording started');
      console.log('[VOICE] Selected MIME type:', mimeType || 'browser default');

      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data && event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        console.log('[VOICE] Recording stopped');
        setRecordingState('STOPPING');

        const audioBlob = new Blob(audioChunksRef.current, { type: mimeType || 'audio/webm' });
        stream.getTracks().forEach((t) => t.stop());

        console.log('[VOICE] Recorded Blob size:', audioBlob.size, 'bytes');

        if (!audioBlob || audioBlob.size < 100) {
          console.warn('[VOICE] Invalid blob size:', audioBlob ? audioBlob.size : 0);
          setSttError('Recording failed. Please try again.');
          setRecordingState('IDLE');
          return;
        }

        setRecordingState('TRANSCRIBING');
        console.log('[VOICE] Sending audio to /transcribe endpoint...');

        try {
          const sttLang = selectedLang === 'auto' ? 'en' : selectedLang;
          const res = await transcribeAudio({ audioBlob, language: sttLang });
          console.log('[VOICE] STT API response:', res);

          if (res.success && res.transcript && res.transcript.trim()) {
            const cleanText = res.transcript.trim();
            console.log('[VOICE] Transcript received:', cleanText);

            setQuery(cleanText);
            
            const autoDetected = detectLanguage(cleanText);
            setDetectedLang(autoDetected);
            console.log('[VOICE] Detected language:', autoDetected);

            const effectiveLang = selectedLang !== 'auto' ? selectedLang : autoDetected;

            if (res.stt_latency_ms) {
              setSttLatency(res.stt_latency_ms);
            }

            setRecordingState('IDLE');
            console.log('[VOICE] Submitting NEW transcript to /ask:', cleanText);

            // Execute submission directly using the new transcript string
            onSubmit({
              query: cleanText,
              top_k: 3,
              preferred_answer_language: effectiveLang,
              language_filter: effectiveLang === 'en' ? null : effectiveLang,
              stt_latency_ms: res.stt_latency_ms || null
            });
          } else {
            console.warn('[VOICE] STT failed or returned empty transcript:', res.error_message);
            setSttError(res.error_message || "Could not understand the voice input. Please try again.");
            setRecordingState('IDLE');
          }
        } catch (err) {
          console.error('[VOICE] Error transcribing audio:', err);
          setRecordingState('IDLE');
          setSttError("Could not understand the voice input. Please try again.");
        }
      };

      mediaRecorder.start();
      setRecordingState('RECORDING');
    } catch (err) {
      console.error('[VOICE] MediaRecorder error:', err);
      setRecordingState('IDLE');
      setSttError('Microphone permission is required for voice input.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordingState === 'RECORDING') {
      mediaRecorderRef.current.stop();
    }
  };

  const toggleRecording = () => {
    if (recordingState === 'RECORDING') {
      stopRecording();
    } else if (recordingState === 'IDLE') {
      startRecording();
    }
  };

  return (
    <div className="w-full mb-10">
      {/* Decorative Section Line Header */}
      <div className="flex items-center justify-center gap-3 mb-6">
        <div className="h-px bg-slate-800 flex-1"></div>
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
        <span className="font-mono text-xs font-bold tracking-widest text-slate-300 uppercase whitespace-nowrap">
          ASK THE KNOWLEDGE BASE
        </span>
        <span className="w-1.5 h-1.5 rounded-full bg-cyan-400"></span>
        <div className="h-px bg-slate-800 flex-1"></div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Main Input Row: Text Input + Ask Button */}
        <div className="p-2 sm:p-2.5 rounded-2xl bg-[#0c162e] border border-slate-700/60 shadow-inner flex items-center justify-between gap-3">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              if (selectedLang === 'auto') {
                setDetectedLang(detectLanguage(e.target.value));
              }
            }}
            placeholder={
              recordingState === 'RECORDING'
                ? 'Listening...'
                : recordingState === 'STOPPING'
                ? 'Processing...'
                : recordingState === 'TRANSCRIBING'
                ? 'Transcribing...'
                : 'Ask a question...'
            }
            disabled={isLoading || recordingState !== 'IDLE'}
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 px-4 py-2.5 outline-none font-sans text-base sm:text-lg font-medium"
          />

          {/* Ask Button Only (Single Mic is below in Voice Panel) */}
          <button
            type="submit"
            disabled={!query.trim() || isLoading || recordingState !== 'IDLE'}
            className="px-6 py-3 rounded-xl bg-[#152042] hover:bg-[#1e2e5c] border border-indigo-500/40 text-slate-100 font-mono font-bold flex items-center justify-center gap-2 disabled:opacity-30 disabled:cursor-not-allowed transition-all text-sm shrink-0 shadow-md"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-slate-100 border-t-transparent rounded-full animate-spin"></div>
            ) : (
              <>
                <span>Ask</span>
                <Send className="w-3.5 h-3.5" />
              </>
            )}
          </button>
        </div>

        {/* Single Compact Language Dropdown Row */}
        <div className="flex items-center justify-end w-full">
          {/* Single Compact Language Dropdown */}
          <div className="relative inline-block text-left">
            <div className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full bg-[#0c162e] border border-cyan-500/40 text-cyan-300 font-mono text-xs font-semibold shadow-sm">
              <Globe className="w-3.5 h-3.5 text-cyan-400" />
              <select
                value={selectedLang}
                onChange={(e) => {
                  setSelectedLang(e.target.value);
                  setDetectedLang(null);
                }}
                className="bg-transparent text-cyan-300 outline-none cursor-pointer pr-1"
              >
                {SUPPORTED_LANGUAGES.map((l) => (
                  <option key={l.code} value={l.code} className="bg-[#0c162e] text-slate-200">
                    {l.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Hero Voice Visualizer Panel */}
        <div className="p-6 rounded-2xl bg-[#0c162e]/80 border border-slate-800/80 flex flex-col items-center justify-center relative">
          <div className="flex items-center justify-center gap-6 sm:gap-10 w-full mb-3">
            {/* Left Waveform Bars */}
            <div className="flex items-center gap-1 sm:gap-1.5">
              <span className={`wave-bar-cyan ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-purple ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-cyan ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-purple ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-cyan ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
            </div>

            {/* Glowing Hero Microphone Button */}
            <button
              type="button"
              onClick={toggleRecording}
              disabled={isLoading || recordingState === 'STOPPING' || recordingState === 'TRANSCRIBING'}
              className={`mic-hero-center ${recordingState === 'RECORDING' ? 'mic-recording-active' : ''}`}
              title="Tap mic to speak (Sarvam STT)"
            >
              {recordingState === 'RECORDING' ? (
                <MicOff className="w-8 h-8 text-white animate-pulse" />
              ) : recordingState === 'STOPPING' || recordingState === 'TRANSCRIBING' ? (
                <div className="w-7 h-7 border-2 border-amber-400 border-t-transparent rounded-full animate-spin"></div>
              ) : (
                <Mic className="w-8 h-8" />
              )}
            </button>

            {/* Right Waveform Bars */}
            <div className="flex items-center gap-1 sm:gap-1.5">
              <span className={`wave-bar-purple ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-cyan ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-purple ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-cyan ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
              <span className={`wave-bar-purple ${recordingState === 'RECORDING' ? 'animate-bounce' : ''}`}></span>
            </div>
          </div>

          <span className="font-mono text-xs text-slate-400 font-medium">
            {recordingState === 'RECORDING' ? (
              <span className="text-rose-400 animate-pulse font-bold">● LISTENING...</span>
            ) : recordingState === 'STOPPING' ? (
              <span className="text-amber-400 font-bold">◌ PROCESSING...</span>
            ) : recordingState === 'TRANSCRIBING' ? (
              <span className="text-amber-400 font-bold">◌ TRANSCRIBING...</span>
            ) : (
              <span>Tap mic to speak</span>
            )}
          </span>
        </div>

        {/* Error State Banner */}
        {sttError && (
          <div className="flex items-center justify-center gap-2 p-3 rounded-xl bg-rose-950/40 border border-rose-500/30 text-xs text-rose-300 font-mono">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{sttError}</span>
          </div>
        )}
      </form>
    </div>
  );
}
