import React from 'react';
import { Globe, CheckCircle2 } from 'lucide-react';

export const SUPPORTED_LANGUAGES = [
  { code: 'auto', label: 'Auto Detect', flag: '🌐' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'hi', label: 'Hindi', flag: '🇮🇳' },
  { code: 'mr', label: 'Marathi', flag: '🇮🇳' },
  { code: 'bn', label: 'Bengali', flag: '🇮🇳' },
  { code: 'te', label: 'Telugu', flag: '🇮🇳' },
  { code: 'ta', label: 'Tamil', flag: '🇮🇳' },
  { code: 'gu', label: 'Gujarati', flag: '🇮🇳' },
  { code: 'kn', label: 'Kannada', flag: '🇮🇳' },
  { code: 'ml', label: 'Malayalam', flag: '🇮🇳' },
  { code: 'pa', label: 'Punjabi', flag: '🇮🇳' },
  { code: 'or', label: 'Odia', flag: '🇮🇳' },
  { code: 'as', label: 'Assamese', flag: '🇮🇳' },
  { code: 'ur', label: 'Urdu', flag: '🇮🇳' },
  { code: 'sa', label: 'Sanskrit', flag: '🇮🇳' },
];

export function getLanguageName(code) {
  if (!code) return 'Auto Detect';
  const found = SUPPORTED_LANGUAGES.find(l => l.code === code.toLowerCase() || l.label.toLowerCase() === code.toLowerCase());
  return found ? `${found.label} ${found.flag}` : code;
}

export default function LanguageSelector({ selectedLanguage, onChangeLanguage, detectedLanguage }) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 mb-2 px-1">
      {/* Selector Label & Dropdown */}
      <div className="flex items-center gap-2">
        <Globe className="w-4 h-4 text-cyan-400 shrink-0" />
        <label htmlFor="language-select" className="text-xs font-semibold text-slate-300 uppercase tracking-wider font-mono">
          Language
        </label>
        
        <div className="relative">
          <select
            id="language-select"
            value={selectedLanguage}
            onChange={(e) => onChangeLanguage(e.target.value)}
            className="appearance-none bg-[#0a1226]/90 border border-white/15 hover:border-cyan-500/40 text-xs font-medium text-slate-100 rounded-xl px-3 py-1.5 pr-8 focus:outline-none focus:ring-1 focus:ring-cyan-400 transition-colors cursor-pointer"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code} className="bg-[#0b1329] text-slate-100">
                {lang.flag} {lang.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-slate-400 text-xs">
            ▼
          </div>
        </div>
      </div>

      {/* Detected Language Notification Badge */}
      {detectedLanguage && (
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/15 border border-emerald-500/30 text-emerald-300 text-xs font-medium font-mono animate-fadeIn">
          <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
          <span>Detected language: <strong>{getLanguageName(detectedLanguage)}</strong></span>
        </div>
      )}
    </div>
  );
}
