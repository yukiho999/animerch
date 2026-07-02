// ============================================
// 图片轮播背景 — 两张背景图交替淡入淡出
// ============================================
import { useState, useEffect } from 'react';

const BG_IMAGES = ['/bg.jpg', '/bg2.jpg', '/bg3.jpg', '/bg4.jpg'];
const SWITCH_INTERVAL = 8000; // 8 秒切换

export default function GradientBg() {
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
            filter: 'blur(2px)',
            transform: 'scale(1.05)',
          }}
        />
      ))}

      {/* 暗色渐变遮罩 — 让粒子更明显，文字可读 */}
      <div className="absolute inset-0 bg-black/45" />

      {/* 彩色渐变叠加 */}
      <div
        className="absolute inset-0 opacity-30"
        style={{
          background: 'linear-gradient(-45deg, #1a1a2e, #16213e, #0f3460, #1a1a2e)',
          backgroundSize: '400% 400%',
          animation: 'gradientMove 15s ease infinite',
        }}
      />

      {/* 模糊光晕 — 增加层次感 */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-emerald-900/15 blur-[120px] rounded-full" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-teal-900/10 blur-[120px] rounded-full" />
    </div>
  );
}
