import React from 'react';
import { Globe } from 'lucide-react';

export const SUPPORTED_LANGUAGES = [
  { code: 'auto', label: 'Auto Detect', flag: '🌐' },
  { code: 'en', label: 'English', flag: '🇬🇧' },
  { code: 'hi', label: 'हिन्दी (Hindi)', flag: '🇮🇳' },
  { code: 'bn', label: 'বাংলা (Bengali)', flag: '🇮🇳' },
  { code: 'ta', label: 'தமிழ் (Tamil)', flag: '🇮🇳' },
  { code: 'te', label: 'తెలుగు (Telugu)', flag: '🇮🇳' },
  { code: 'mr', label: 'मराठी (Marathi)', flag: '🇮🇳' },
  { code: 'gu', label: 'ગુજરાતી (Gujarati)', flag: '🇮🇳' },
  { code: 'kn', label: 'ಕನ್ನಡ (Kannada)', flag: '🇮🇳' },
  { code: 'ml', label: 'മലയാളം (Malayalam)', flag: '🇮🇳' },
  { code: 'pa', label: 'ਪੰਜਾਬੀ (Punjabi)', flag: '🇮🇳' },
  { code: 'or', label: 'ଓଡ଼ିଆ (Odia)', flag: '🇮🇳' },
  { code: 'as', label: 'অসমীয়া (Assamese)', flag: '🇮🇳' },
  { code: 'ur', label: 'اردو (Urdu)', flag: '🇮🇳' },
  { code: 'sa', label: 'संस्कृतम् (Sanskrit)', flag: '🇮🇳' },
];

export function getLanguageName(code) {
  if (!code) return 'Auto Detect';
  const cleanCode = code.toLowerCase();
  const found = SUPPORTED_LANGUAGES.find(
    l => l.code === cleanCode || l.label.toLowerCase().includes(cleanCode)
  );
  if (found) {
    return `${found.label} ${found.flag}`;
  }
  // Fallbacks for display
  if (cleanCode.startsWith('hi')) return 'हिन्दी (Hindi) 🇮🇳';
  if (cleanCode.startsWith('bn')) return 'বাংলা (Bengali) 🇮🇳';
  if (cleanCode.startsWith('ta')) return 'தமிழ் (Tamil) 🇮🇳';
  if (cleanCode.startsWith('te')) return 'తెలుగు (Telugu) 🇮🇳';
  if (cleanCode.startsWith('mr')) return 'मराठी (Marathi) 🇮🇳';
  if (cleanCode.startsWith('gu')) return 'ગુજરાતી (Gujarati) 🇮🇳';
  if (cleanCode.startsWith('kn')) return 'ಕನ್ನಡ (Kannada) 🇮🇳';
  if (cleanCode.startsWith('ml')) return 'മലയാളം (Malayalam) 🇮🇳';
  if (cleanCode.startsWith('pa')) return 'ਪੰਜਾਬੀ (Punjabi) 🇮🇳';
  if (cleanCode.startsWith('or')) return 'ଓଡ଼ିଆ (Odia) 🇮🇳';
  if (cleanCode.startsWith('as')) return 'অসমীয়া (Assamese) 🇮🇳';
  if (cleanCode.startsWith('ur')) return 'اردو (Urdu) 🇮🇳';
  if (cleanCode.startsWith('sa')) return 'संस्कृतम् (Sanskrit) 🇮🇳';
  if (cleanCode.startsWith('en')) return 'English 🇬🇧';
  return 'English 🇬🇧';
}

export default function LanguageSelector({ selectedLanguage, onLanguageChange, detectedLanguage }) {
  return (
    <div className="flex items-center justify-between gap-2 mb-2 px-1 text-xs font-sans">
      
      {/* Selector Label & Dropdown */}
      <div className="flex items-center gap-1.5 text-slate-300">
        <Globe className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
        <span className="font-medium">Language:</span>
        
        <div className="relative inline-block">
          <select
            value={selectedLanguage}
            onChange={(e) => onLanguageChange && onLanguageChange(e.target.value)}
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
