// ============================================
// 周边卡片 — 图主文辅 + 3D 倾斜 + 光晕跟随（仿 ref 风格）
// ============================================
import { useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';

interface Props {
  merch: {
    id: number;
    ip_name: string;
    name: string;
    category: string | null;
    official_price: number | null;
    release_date: string | null;
    release_method: string | null;
    is_discontinued: boolean;
    image_url: string | null;
    crafts: string[];
  };
  index?: number;
}

const FALLBACK_IMAGE = '/favicon.svg';

function imgUrl(raw: string | null): string {
  if (!raw) return FALLBACK_IMAGE;
  const u = raw.split(/[，,]+/)[0].trim();
  if (!u) return FALLBACK_IMAGE;
  // 微博图片走后端代理绕过 Referer 防盗链
  return `/api/proxy/image?url=${encodeURIComponent(u)}`;
}

export default function MerchCard({ merch, index = 0 }: Props) {
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
      <Link to={`/merch/${merch.id}`} className="no-underline block">
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
                src={imgUrl(merch.image_url)}
                alt={merch.name}
                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                loading="lazy"
                referrerPolicy="no-referrer"
                onError={(e) => {
                  (e.target as HTMLImageElement).src = FALLBACK_IMAGE;
                }}
              />

              {/* 渐变遮罩 — 底部深，顶部透 */}
              <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/20 to-transparent" />

              {/* 顶部标签 */}
              <div className="absolute top-3 left-3 flex flex-wrap gap-1.5">
                {merch.ip_name && (
                  <span className="px-2.5 py-0.5 rounded-full bg-white/15 backdrop-blur-sm text-white/90 text-[10px] md:text-xs font-medium">
                    {merch.ip_name}
                  </span>
                )}
                {merch.release_method && merch.release_method !== '未知' && (
                  <span className="px-2.5 py-0.5 rounded-full bg-sky-500/80 backdrop-blur-sm text-white text-[10px] md:text-xs font-medium">
                    {merch.release_method}
                  </span>
                )}
                {merch.is_discontinued && (
                  <span className="px-2.5 py-0.5 rounded-full bg-red-500/80 backdrop-blur-sm text-white text-[10px] md:text-xs font-medium">
                    绝版
                  </span>
                )}
              </div>

              {/* 底部信息覆盖层 */}
              <div className="absolute bottom-0 left-0 right-0 p-3 md:p-4">
                <h3 className="text-sm md:text-base font-bold text-white mb-1 line-clamp-2 leading-snug">
                  {merch.name}
                </h3>

                <div className="flex items-center justify-between text-white/70 text-xs">
                  <div className="flex items-center gap-2">
                    {merch.category && (
                      <span className="px-2 py-0.5 rounded-full bg-white/10 backdrop-blur-sm">
                        {merch.category}
                      </span>
                    )}
                    {merch.release_date && <span>{merch.release_date}</span>}
                  </div>
                  {merch.official_price != null ? (
                    <span className="text-sm font-bold text-white">¥{Math.round(merch.official_price)}</span>
                  ) : (
                    <span className="text-white/50 text-xs">待定</span>
                  )}
                </div>

                {/* 工艺标签 */}
                {merch.crafts.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-2">
                    {merch.crafts.slice(0, 4).map((c) => (
                      <span
                        key={c}
                        className="px-2 py-0.5 rounded-full bg-white/10 backdrop-blur-sm text-white/60 text-[10px]"
                      >
                        {c}
                      </span>
                    ))}
                    {merch.crafts.length > 4 && (
                      <span className="text-white/40 text-[10px]">+{merch.crafts.length - 4}</span>
                    )}
                  </div>
                )}
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
