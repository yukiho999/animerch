// ============================================
// 子页面背景 — 图片轮播 + 粒子（比首页更模糊）
// ============================================
import { useState, useEffect } from 'react';
import ParticleBackground from './ParticleBackground';

// 背景图路径：开发环境 /bg.jpg，生产环境 /animerch/bg.jpg（GitHub Pages）
const BASE = (import.meta as any).env?.BASE_URL || '/animerch/';
const BG_IMAGES = ['bg.jpg', 'bg2.jpg', 'bg3.jpg', 'bg4.jpg'].map(f => `${BASE}${f}`);
const SWITCH_INTERVAL = 8000;

export default function SubPageBackground() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    if (BG_IMAGES.length <= 1) return;
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % BG_IMAGES.length);
    }, SWITCH_INTERVAL);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden" style={{ zIndex: -1 }}>
      {/* 图片层 */}
      {BG_IMAGES.map((img, i) => (
        <div
          key={img}
          className="absolute inset-0 transition-opacity"
          style={{
            backgroundImage: `url(${img})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            opacity: i === index ? 1 : 0,
            transitionDuration: '2000ms',
            transitionTimingFunction: 'ease-in-out',
            filter: 'blur(10px) brightness(0.7)',
            transform: 'scale(1.1)',
          }}
        />
      ))}

      {/* 白色柔光遮罩 — 提亮 */}
      <div className="absolute inset-0 bg-white/15" />

      {/* 彩色渐变叠加 — 比首页更微弱 */}
      <div
        className="absolute inset-0 opacity-20"
        style={{
          background: 'linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a1a2e)',
          backgroundSize: '400% 400%',
          animation: 'gradientMove 15s ease infinite',
        }}
      />

      {/* 模糊光晕 */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-900/10 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-teal-900/8 blur-[120px] rounded-full" />

      {/* 粒子 — 首页同款 */}
      <ParticleBackground />
    </div>
  );
}
