// ============================================
// 点击涟漪效果 — Canvas 叠加层
// ============================================
import { useEffect, useRef } from 'react';

interface Ripple {
  x: number;
  y: number;
  r: number;
  maxR: number;
  opacity: number;
  velocity: number;
}

export default function ClickRipple() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let ripples: Ripple[] = [];

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    window.addEventListener('resize', resize);
    resize();

    const handleClick = (e: MouseEvent) => {
      ripples.push({
        x: e.clientX,
        y: e.clientY,
        r: 0,
        maxR: 70,
        opacity: 0.6,
        velocity: 2.5,
      });
    };
    window.addEventListener('click', handleClick);

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.shadowBlur = 15;
      ctx.shadowColor = 'rgba(255, 255, 255, 0.3)';

      for (let i = 0; i < ripples.length; i++) {
        const rp = ripples[i];
        rp.r += rp.velocity;
        rp.velocity *= 0.96;
        rp.opacity -= 0.012;

        if (rp.opacity <= 0) {
          ripples.splice(i, 1);
          i--;
          continue;
        }

        ctx.beginPath();
        ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(255, 255, 255, ${rp.opacity})`;
        ctx.lineWidth = 1.5;
        ctx.stroke();

        ctx.beginPath();
        ctx.arc(rp.x, rp.y, rp.r * 0.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(255, 255, 255, ${rp.opacity * 0.2})`;
        ctx.fill();
      }
      ctx.shadowBlur = 0;

      requestAnimationFrame(animate);
    };
    animate();

    return () => {
      window.removeEventListener('resize', resize);
      window.removeEventListener('click', handleClick);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[9999]"
    />
  );
}
