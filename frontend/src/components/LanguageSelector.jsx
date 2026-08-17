import React from 'react';
import { Globe } from 'lucide-react';

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
    <div className="flex items-center justify-between gap-2 mb-2 px-1 text-xs">
      
      {/* Selector Label & Dropdown */}
      <div className="flex items-center gap-1.5 text-slate-300">
        <Globe className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
        <span className="font-medium">Language:</span>
        
        <div className="relative inline-block">
          <select
            value={selectedLanguage}
            onChange={(e) => onChangeLanguage(e.target.value)}
            className="appearance-none bg-[#0a1226]/80 border border-white/10 hover:border-white/20 text-xs text-slate-200 rounded-md px-2.5 py-1 pr-6 focus:outline-none focus:ring-1 focus:ring-cyan-400 cursor-pointer font-sans"
          >
            {SUPPORTED_LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code} className="bg-[#0b1329] text-slate-100">
                {lang.flag} {lang.label}
              </option>
            ))}
          </select>
          <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-1.5 text-slate-400 text-[10px]">
            ▼
          </div>
        </div>
      </div>

      {/* Detected Language Notification */}
      {detectedLanguage && (
        <div className="text-[11px] text-emerald-400 font-mono flex items-center gap-1">
          <span>Detected language: <strong>{getLanguageName(detectedLanguage)}</strong></span>
        </div>
      )}

    </div>
  );
}
