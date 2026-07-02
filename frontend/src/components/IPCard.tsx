// ============================================
// IP 卡片 — 图主文辅 + 3D 倾斜 + 光晕跟随（仿 ref 风格）
// ============================================
import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import type { IPItem } from '../types';

// fallback 图路径：开发环境 /favicon.svg，生产环境 /animerch/favicon.svg（GitHub Pages）
const B = (import.meta as any).env?.BASE_URL || '/animerch/';
const FALLBACK_IMAGE = `${B}favicon.svg`;

// 图片代理基地址
const imgBase = (import.meta as any).env?.VITE_API_BASE || '/api';

function imgUrl(raw: string | null): string {
  if (!raw) return FALLBACK_IMAGE;
  const u = raw.split(/[，,]+/)[0].trim();
  if (!u) return FALLBACK_IMAGE;
  return `${imgBase}/proxy/image?url=${encodeURIComponent(u)}`;
}

export default function IPCard({ ip, index = 0 }: { ip: IPItem; index?: number }) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [tilt, setTilt] = useState({ rotateX: 0, rotateY: 0 });
  const [glow, setGlow] = useState({ x: 50, y: 50, opacity: 0 });

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    const cx = e.clientX - rect.left;
    const cy = e.clientY - rect.top;
    const midX = rect.width / 2;
    const midY = rect.height / 2;
    setTilt({
      rotateX: -((cy - midY) / midY) * 6,
      rotateY: ((cx - midX) / midX) * 6,
    });
    setGlow({
      x: (cx / rect.width) * 100,
      y: (cy / rect.height) * 100,
      opacity: 0.15,
    });
  };

  const handleMouseLeave = () => {
    setTilt({ rotateX: 0, rotateY: 0 });
    setGlow({ x: 50, y: 50, opacity: 0 });
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.08 * index, ease: 'easeOut' }}
    >
      <Link to={`/ip/${ip.id}`} className="no-underline block">
        <div
          ref={cardRef}
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
          className="group relative rounded-3xl overflow-hidden cursor-pointer"
          style={{ perspective: '1000px', transformStyle: 'preserve-3d' }}
        >
          {/* 3D 倾斜层 */}
          <div
            className="relative transition-transform duration-200 ease-out"
            style={{
              transform: `rotateX(${tilt.rotateX}deg) rotateY(${tilt.rotateY}deg)`,
              transformStyle: 'preserve-3d',
            }}
          >
            {/* 图片区 16/10 */}
            <div className="relative aspect-[16/10] w-full overflow-hidden">
              <img
                src={imgUrl(ip.cover_url)}
                alt={ip.name}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                loading="lazy"
                referrerPolicy="no-referrer"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = FALLBACK_IMAGE;
                }}
              />

              {/* 渐变遮罩 */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/20 to-transparent" />

              {/* 顶部标签 */}
              <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
                {ip.category && (
                  <span className="px-2.5 py-0.5 rounded-full bg-white/15 backdrop-blur-sm text-white/90 text-[10px] md:text-xs font-medium">
                    {ip.category}
                  </span>
                )}
              </div>

              {/* 底部信息覆盖层 */}
              <div className="absolute bottom-0 left-0 right-0 p-3 md:p-4">
                <h3 className="text-sm md:text-base font-bold text-white mb-1 leading-snug">
                  {ip.name}
                </h3>
                {ip.description && (
                  <p className="text-white/60 text-xs line-clamp-1 mb-2">
                    {ip.description}
                  </p>
                )}
                <div className="flex items-center justify-between text-white/70 text-xs">
                  <span className="px-2 py-0.5 rounded-full bg-white/10 backdrop-blur-sm">
                    {ip.merch_count} 件周边
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 光晕跟随 */}
          <div
            className="absolute inset-0 pointer-events-none rounded-3xl transition-opacity duration-200"
            style={{
              background: `radial-gradient(circle at ${glow.x}% ${glow.y}%, rgba(255,255,255,${glow.opacity}), transparent 60%)`,
            }}
          />
        </div>
      </Link>
    </motion.div>
  );
}
