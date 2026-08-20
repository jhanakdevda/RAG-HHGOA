import React from 'react';
import { Globe } from 'lucide-react';

export default function SupportedLanguagesGrid() {
  const languages = [
    'हिंदी', 'বাংলা', 'தமிழ்', 'తెలుగు', 'मराठी', 'ગુજરાતી', 'ಕನ್ನಡ', 'മലയാളം',
    'ਪੰਜਾਬੀ', 'ଓଡ଼ିଆ', 'অসমীয়া', 'नेपाली', 'اردو', 'English'
  ];

  return (
    <div className="w-full glass-panel p-6 rounded-3xl border border-purple-500/30 bg-[#080518]/90 shadow-lg space-y-4 font-sans">
      
      <div className="flex items-center gap-2 font-mono text-xs font-bold text-white uppercase tracking-wider border-b border-purple-500/20 pb-3">
        <Globe className="w-4 h-4 text-cyan-400" />
        <span>Supported Languages</span>
      </div>

      <div className="flex flex-wrap gap-2.5 font-sans text-xs">
        {languages.map((lang, idx) => (
          <div
            key={idx}
            className="px-4 py-2 rounded-2xl bg-[#050310]/90 border border-purple-500/20 text-slate-200 hover:text-white hover:border-purple-400 transition-all shadow-sm font-semibold"
          >
            {lang}
          </div>
        ))}
      </div>

    </div>
  );
}
