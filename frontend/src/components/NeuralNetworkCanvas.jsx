import React, { useEffect, useRef } from 'react';

export default function NeuralNetworkCanvas({ appState = 'IDLE' }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    let animationFrameId;
    let width = (canvas.width = canvas.parentElement.clientWidth || 600);
    let height = (canvas.height = 140);

    const handleResize = () => {
      if (canvas.parentElement) {
        width = canvas.width = canvas.parentElement.clientWidth;
        height = canvas.height = 140;
      }
    };
    window.addEventListener('resize', handleResize);

    // 7 Pipeline Stage Nodes
    const stageNames = [
      'Query',
      'Embedding',
      'FAISS',
      'Evidence',
      'LLM',
      'Verification',
      'Answer'
    ];

    let tick = 0;

    const render = () => {
      tick += prefersReducedMotion ? 0.005 : 0.02;
      ctx.clearRect(0, 0, width, height);

      const paddingX = 40;
      const availableWidth = width - paddingX * 2;
      const stepX = availableWidth / (stageNames.length - 1);
      const centerY = height / 2;

      // Determine active stage highlight index based on appState
      let activeIndex = -1;
      if (appState === 'TYPING' || appState === 'QUERY') activeIndex = 0;
      else if (appState === 'RETRIEVING') activeIndex = 2;
      else if (appState === 'GENERATING') activeIndex = 4;
      else if (appState === 'VERIFYING') activeIndex = 5;
      else if (appState === 'ANSWER_COMPLETE') activeIndex = 6;

      const nodeCoords = stageNames.map((name, i) => ({
        x: paddingX + i * stepX,
        y: centerY + (prefersReducedMotion ? 0 : Math.sin(tick + i) * 3),
        name,
        isActive: i <= activeIndex
      }));

      // Draw connecting lines & data flow pulses
      for (let i = 0; i < nodeCoords.length - 1; i++) {
        const n1 = nodeCoords[i];
        const n2 = nodeCoords[i + 1];

        const isPathActive = i < activeIndex;
        ctx.strokeStyle = isPathActive ? 'rgba(0, 240, 255, 0.7)' : 'rgba(168, 85, 247, 0.25)';
        ctx.lineWidth = isPathActive ? 2 : 1;

        ctx.beginPath();
        ctx.moveTo(n1.x, n1.y);
        ctx.lineTo(n2.x, n2.y);
        ctx.stroke();

        // Animated traveling data pulse
        if (isPathActive || appState === 'RETRIEVING' || appState === 'GENERATING') {
          const pulseOffset = ((tick * 1.5 + i * 0.4) % 1.0);
          const px = n1.x + (n2.x - n1.x) * pulseOffset;
          const py = n1.y + (n2.y - n1.y) * pulseOffset;

          ctx.fillStyle = '#00F0FF';
          ctx.shadowColor = 'rgba(0, 240, 255, 0.9)';
          ctx.shadowBlur = 8;
          ctx.beginPath();
          ctx.arc(px, py, 3, 0, Math.PI * 2);
          ctx.fill();
          ctx.shadowBlur = 0;
        }
      }

      // Draw Nodes & Labels
      nodeCoords.forEach((node, i) => {
        const isCurrentActive = i === activeIndex;
        const radius = isCurrentActive ? 7 : 5;

        // Node Glow
        if (node.isActive) {
          ctx.fillStyle = isCurrentActive ? '#EC4899' : '#00F0FF';
          ctx.shadowColor = isCurrentActive ? 'rgba(236, 72, 153, 0.9)' : 'rgba(0, 240, 255, 0.8)';
          ctx.shadowBlur = 12;
        } else {
          ctx.fillStyle = '#A855F7';
          ctx.shadowColor = 'rgba(168, 85, 247, 0.3)';
          ctx.shadowBlur = 4;
        }

        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Label
        ctx.fillStyle = node.isActive ? '#FFFFFF' : '#94A3B8';
        ctx.font = '10px "JetBrains Mono", monospace';
        ctx.textAlign = 'center';
        ctx.fillText(node.name, node.x, node.y + 22);
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, [appState]);

  return (
    <div className="w-full h-[140px] relative rounded-xl bg-[#090617]/80 border border-purple-500/20 p-2 overflow-hidden">
      <div className="absolute top-2 left-3 text-[10px] font-mono text-purple-300 font-bold uppercase tracking-wider">
        LIVE NEURAL PIPELINE FLOW
      </div>
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}
