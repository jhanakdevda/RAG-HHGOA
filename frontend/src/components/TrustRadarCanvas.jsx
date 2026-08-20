import React, { useEffect, useState } from 'react';

export default function TrustRadarCanvas({ score = 0.85, status = 'GROUNDED' }) {
  const [rotation, setRotation] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setRotation(prev => (prev + 0.5) % 360);
    }, 40);
    return () => clearInterval(interval);
  }, []);

  const axes = [
    'Evidence Check',
    'Hallucination Check',
    'Context Match',
    'Claim Alignment',
    'Factual Fidelity'
  ];

  const center = 100;
  const radius = 65;
  const numAxes = axes.length;

  const getCoordinates = (index, valueMultiplier, rotDeg = 0) => {
    const angleRad = (rotDeg * Math.PI) / 180;
    const baseAngle = (Math.PI * 2 / numAxes) * index - Math.PI / 2 + angleRad;
    const x = center + radius * valueMultiplier * Math.cos(baseAngle);
    const y = center + radius * valueMultiplier * Math.sin(baseAngle);
    return { x, y };
  };

  const values = [
    Math.max(0.65, score),
    Math.max(0.72, score * 0.95),
    Math.max(0.68, score * 1.05),
    Math.max(0.78, score * 0.9),
    Math.max(0.75, score * 1.0)
  ];

  const radarPoints = values
    .map((v, i) => {
      const { x, y } = getCoordinates(i, v, rotation);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  return (
    <div className="w-full font-sans">
      <div className="flex items-center justify-between font-mono text-xs mb-2">
        <span className="font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
          Spinning Holographic Trust Radar
        </span>
        <span className="text-cyan-400 font-bold bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
          {(score * 100).toFixed(0)}% Faithfulness
        </span>
      </div>

      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Animated Holographic Spider Chart */}
        <div className="w-[200px] h-[200px] shrink-0 relative flex items-center justify-center">
          
          {/* Subtle Outer Halo Ring */}
          <div className="absolute inset-2 rounded-full border border-cyan-500/20 animate-pulse pointer-events-none" />

          <svg viewBox="0 0 200 200" className="w-full h-full drop-shadow-[0_0_15px_rgba(0,240,255,0.3)]">
            {/* Concentric Grid Pentagons */}
            {[0.25, 0.5, 0.75, 1.0].map((level, idx) => {
              const points = Array.from({ length: numAxes })
                .map((_, i) => {
                  const { x, y } = getCoordinates(i, level, rotation);
                  return `${x.toFixed(1)},${y.toFixed(1)}`;
                })
                .join(' ');
              return (
                <polygon
                  key={idx}
                  points={points}
                  fill="none"
                  stroke={idx === 3 ? "rgba(0, 240, 255, 0.35)" : "rgba(168, 85, 247, 0.15)"}
                  strokeWidth={idx === 3 ? "1.5" : "1"}
                  strokeDasharray={idx % 2 === 1 ? "3 3" : "none"}
                />
              );
            })}

            {/* Rotating Axis Rays */}
            {Array.from({ length: numAxes }).map((_, i) => {
              const { x, y } = getCoordinates(i, 1.0, rotation);
              return (
                <line
                  key={i}
                  x1={center}
                  y1={center}
                  x2={x}
                  y2={y}
                  stroke="rgba(0, 240, 255, 0.25)"
                  strokeWidth="1"
                />
              );
            })}

            {/* Holographic Radar Polygon */}
            <polygon
              points={radarPoints}
              fill="rgba(0, 240, 255, 0.22)"
              stroke="#00F0FF"
              strokeWidth="2"
              className="drop-shadow-[0_0_12px_rgba(0,240,255,0.7)]"
            />

            {/* Orbiting Glowing Nodes on Vertices */}
            {values.map((v, i) => {
              const { x, y } = getCoordinates(i, v, rotation);
              return (
                <g key={i}>
                  <circle
                    cx={x}
                    cy={y}
                    r="4"
                    fill="#00F0FF"
                    className="animate-pulse"
                  />
                  <circle
                    cx={x}
                    cy={y}
                    r="8"
                    fill="none"
                    stroke="rgba(0, 240, 255, 0.5)"
                    strokeWidth="1"
                  />
                </g>
              );
            })}
          </svg>
        </div>

        {/* Axis Metric Labels List */}
        <div className="flex-1 space-y-1.5 font-mono text-[11px] w-full">
          {axes.map((label, idx) => (
            <div key={idx} className="flex items-center justify-between text-slate-300 p-1.5 rounded-lg bg-white/5 border border-white/5 hover:border-purple-500/30 transition-all">
              <span className="truncate pr-2 font-medium">{label}</span>
              <span className="text-cyan-300 font-bold font-mono">{(values[idx] * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
