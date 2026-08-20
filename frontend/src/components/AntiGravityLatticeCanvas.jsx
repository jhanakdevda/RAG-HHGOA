import React, { useEffect, useRef } from 'react';

export default function AntiGravityLatticeCanvas() {
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId;
    let width = (canvas.width = canvas.parentElement.clientWidth || 320);
    let height = (canvas.height = 240);

    const handleResize = () => {
      if (canvas.parentElement) {
        width = canvas.width = canvas.parentElement.clientWidth;
        height = canvas.height = 240;
      }
    };
    window.addEventListener('resize', handleResize);

    // Build 3D Fractal Lattice Mesh
    const nodes = [];
    const gridSize = 3;
    const spacing = 45;

    for (let x = -1; x <= 1; x++) {
      for (let y = -1; y <= 1; y++) {
        for (let z = -1; z <= 1; z++) {
          nodes.push({
            origX: x * spacing,
            origY: y * spacing,
            origZ: z * spacing,
            x: x * spacing,
            y: y * spacing,
            z: z * spacing
          });
        }
      }
    }

    let angleX = 0;
    let angleY = 0;

    const render = () => {
      angleX += 0.008;
      angleY += 0.012;
      ctx.clearRect(0, 0, width, height);

      const focalLength = 280;
      const projected = [];

      // Rotate and Project Nodes
      const cosX = Math.cos(angleX);
      const sinX = Math.sin(angleX);
      const cosY = Math.cos(angleY);
      const sinY = Math.sin(angleY);

      for (let i = 0; i < nodes.length; i++) {
        const n = nodes[i];
        
        // Y rotation
        let rx = n.origX * cosY - n.origZ * sinY;
        let rz = n.origZ * cosY + n.origX * sinY;
        
        // X rotation
        let ry = n.origY * cosX - rz * sinX;
        rz = rz * cosX + n.origY * sinX;

        // Anti-gravity floating oscillation
        ry += Math.sin(angleY * 2 + i) * 6;

        const scale = focalLength / (focalLength + rz + 200);
        const px = rx * scale + width / 2;
        const py = ry * scale + height / 2;

        projected.push({ x: px, y: py, z: rz, scale, origIdx: i });
      }

      // Draw Connections (Lattice Filaments)
      ctx.lineWidth = 1;
      for (let i = 0; i < projected.length; i++) {
        const p1 = projected[i];
        for (let j = i + 1; j < projected.length; j++) {
          const p2 = projected[j];
          const distSq = (p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2;

          if (distSq < 4800) {
            const alpha = (1 - Math.sqrt(distSq) / 70) * 0.45;
            const gradient = ctx.createLinearGradient(p1.x, p1.y, p2.x, p2.y);
            gradient.addColorStop(0, `rgba(0, 240, 255, ${alpha})`);
            gradient.addColorStop(1, `rgba(168, 85, 247, ${alpha})`);

            ctx.strokeStyle = gradient;
            ctx.beginPath();
            ctx.moveTo(p1.x, p1.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      }

      // Draw Glowing Nodes
      for (let i = 0; i < projected.length; i++) {
        const p = projected[i];
        const r = Math.max(1.5, 3 * p.scale);
        
        ctx.fillStyle = i % 2 === 0 ? '#00F0FF' : '#A855F7';
        ctx.shadowColor = i % 2 === 0 ? 'rgba(0, 240, 255, 0.8)' : 'rgba(168, 85, 247, 0.8)';
        ctx.shadowBlur = 10;
        
        ctx.beginPath();
        ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
        ctx.fill();
      }

      ctx.shadowBlur = 0;
      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener('resize', handleResize);
      cancelAnimationFrame(animationFrameId);
    };
  }, []);

  return (
    <div className="w-full h-[240px] relative flex items-center justify-center">
      <canvas ref={canvasRef} className="w-full h-full" />
    </div>
  );
}
