import React from 'react';

export default function Hero() {
  return (
    <section className="pt-16 pb-12 sm:pt-24 sm:pb-16 text-center max-w-3xl mx-auto px-4 font-sans">
      <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight mb-4 leading-tight">
        <span className="bg-gradient-to-r from-purple-400 via-blue-400 to-emerald-400 bg-clip-text text-transparent">
          Ask. Listen. Discover.
        </span>
      </h1>

      <p className="text-slate-300 text-sm sm:text-base font-normal leading-relaxed max-w-2xl mx-auto">
        Voice-enabled Retrieval-Augmented Generation across Indian languages and English. Ask questions, listen to grounded answers, and inspect verified source attributions.
      </p>
    </section>
  );
}
