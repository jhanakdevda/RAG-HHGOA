import React from 'react';
import { Zap } from 'lucide-react';

export default function QuickPrompts({ onSelectPrompt }) {
  const prompts = [
    { text: 'What is a corporation?', lang: 'en' },
    { text: 'What is artificial intelligence?', lang: 'en' },
    { text: 'पर्यावरण संरक्षण क्यों महत्वपूर्ण है?', lang: 'hi' },
    { text: 'मराठीमध्ये प्रश्न विचारा', lang: 'mr' },
    { text: 'ગુજરાતીમાં પ્રશ્ન પૂછો', lang: 'gu' }
  ];

  return (
    <div className="pt-2 border-t border-purple-500/20 font-sans">
      <div className="flex items-center gap-1.5 text-[11px] font-mono text-purple-300 font-bold mb-2.5 uppercase tracking-wider">
        <Zap className="w-3.5 h-3.5 text-amber-400" />
        <span>QUICK TEST PROMPTS</span>
      </div>

      <div className="flex flex-wrap gap-2 font-mono text-xs">
        {prompts.map((p, idx) => (
          <button
            key={idx}
            type="button"
            onClick={() => onSelectPrompt(p.text)}
            className="px-3 py-1.5 rounded-xl bg-purple-950/40 hover:bg-purple-900/60 border border-purple-500/30 text-slate-200 hover:text-white font-sans text-xs transition-all shadow-sm"
          >
            {p.text}
          </button>
        ))}
      </div>
    </div>
  );
}
