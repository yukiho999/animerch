// ============================================
// 萤火虫粒子背景 — Canvas 动画
// ============================================
import { useEffect, useRef } from 'react';

interface Particle {
  x: number;
  y: number;
  size: number;
  vx: number;
  vy: number;
  opacity: number;
  opacityDir: number;
  breathingSpeed: number;
  breathingPhase: number;
}

export default function ParticleBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let particles: Particle[] = [];
    let animId: number;

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
    };
    resize();
    window.addEventListener('resize', resize);

    // 初始化粒子
    const count = 60;
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        size: 1.5 + Math.random() * 3,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        opacity: 0.2 + Math.random() * 0.6,
        opacityDir: Math.random() > 0.5 ? 1 : -1,
        breathingSpeed: 0.005 + Math.random() * 0.015,
        breathingPhase: Math.random() * Math.PI * 2,
      });
    }

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      for (const p of particles) {
        // 缓慢移动
        p.x += p.vx;
        p.y += p.vy;

        // 边界反弹
        if (p.x < 0) p.vx = Math.abs(p.vx);
        if (p.x > canvas.width) p.vx = -Math.abs(p.vx);
        if (p.y < 0) p.vy = Math.abs(p.vy);
        if (p.y > canvas.height) p.vy = -Math.abs(p.vy);

        // 呼吸闪烁
        p.breathingPhase += p.breathingSpeed;
        const currentOpacity = p.opacity * (0.4 + 0.6 * Math.sin(p.breathingPhase));

        // 绘制光晕
        ctx.save();
        ctx.globalAlpha = currentOpacity;

        // 外层大光晕
        const gradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size * 8);
        gradient.addColorStop(0, 'rgba(200, 255, 220, 0.9)');
        gradient.addColorStop(0.3, 'rgba(160, 255, 200, 0.4)');
        gradient.addColorStop(0.7, 'rgba(100, 200, 150, 0.05)');
        gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size * 8, 0, Math.PI * 2);
        ctx.fill();

        // 内核亮点
        ctx.fillStyle = 'rgba(220, 255, 240, 0.95)';
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
      }

      animId = requestAnimationFrame(animate);
    };
    animate();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-0"
      style={{ background: 'transparent' }}
    />
  );
}
