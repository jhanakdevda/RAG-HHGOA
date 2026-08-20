import React, { useEffect, useRef } from 'react';

export default function CometVortexCanvas({ onSelectQuestion }) {
  const canvasRef = useRef(null);

  const sampleQuestions = [
    "What is a corporation?",
    "पर्यावरण संरक्षण क्यों महत्वपूर्ण है?",
    "What is machine learning?",
    "कॉर्पोरेशन म्हणजे काय?",
    "કોર્પોરેશન એટલે શું?"
  ];

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId;
    let width = (canvas.width = canvas.parentElement.clientWidth || 320);
    let height = (canvas.height = 200);

    const handleResize = () => {
      if (canvas.parentElement) {
        width = canvas.width = canvas.parentElement.clientWidth;
        height = canvas.height = 200;
      }
    };
    window.addEventListener('resize', handleResize);

    // Particle comet trails
    const particles = [];
    for (let i = 0; i < 60; i++) {
      particles.push({
        angle: Math.random() * Math.PI * 2,
        radius: Math.random() * 85 + 10,
        speed: Math.random() * 0.015 + 0.005,
        size: Math.random() * 1.5 + 0.8,
        color: Math.random() > 0.5 ? '#A855F7' : '#00F0FF'
      });
    }

    let angleOffset = 0;

    const render = () => {
      angleOffset += 0.008;
      ctx.clearRect(0, 0, width, height);

      const cx = width / 2;
      const cy = height / 2;

      // Draw Central Glowing Core Node
      ctx.fillStyle = '#00F0FF';
      ctx.shadowColor = 'rgba(0, 240, 255, 0.9)';
      ctx.shadowBlur = 20;
      ctx.beginPath();
      ctx.arc(cx, cy, 4, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;

      // Draw Spiral Vortex Comet Particles
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.angle += p.speed;

        const x = cx + Math.cos(p.angle) * p.radius;
        const y = cy + Math.sin(p.angle) * (p.radius * 0.5); // Elliptical spiral

        const alpha = Math.min(1.0, (p.radius / 90) * 0.8);
        ctx.fillStyle = p.color;
        ctx.globalAlpha = alpha;

        ctx.beginPath();
        ctx.arc(x, y, p.size, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.globalAlpha = 1.0;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="w-full relative font-sans">
      
      {/* Vortex Canvas Background */}
      <div className="w-full h-[180px] relative rounded-xl overflow-hidden bg-[#0a0718]/80 border border-purple-500/20">
        <canvas ref={canvasRef} className="w-full h-full" />

        {/* Overlay Question Chips integrated on spiral trails */}
        <div className="absolute inset-0 p-3 flex flex-wrap items-center justify-around gap-2 font-mono text-xs">
          {sampleQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => onSelectQuestion(q)}
              className="px-3 py-1 rounded-full bg-[#120c29]/90 hover:bg-purple-900/60 border border-purple-500/30 text-slate-200 hover:text-white font-sans text-xs transition-all shadow-[0_0_12px_rgba(168,85,247,0.25)] hover:scale-105"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
