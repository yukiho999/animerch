// ============================================
// 图片轮播组件 — 多图轮播
// ============================================
import { useState } from 'react';

interface Props {
  images: string[];          // 图片URL列表
  className?: string;        // 外层class
  maxHeight?: number;        // 最大高度
  minHeight?: number;        // 最小高度
}

export default function ImageCarousel({
  images,
  className = '',
  maxHeight = 360,
  minHeight = 160,
}: Props) {
  const [idx, setIdx] = useState(0);

  if (!images || images.length === 0) {
    return (
      <div className={`flex items-center justify-center bg-stone-50 text-4xl opacity-20 ${className}`}
           style={{ minHeight, maxHeight }}>
        🖼
      </div>
    );
  }

  const prev = () => setIdx((idx - 1 + images.length) % images.length);
  const next = () => setIdx((idx + 1) % images.length);

  return (
    <div className={`relative bg-stone-50 overflow-hidden group ${className}`}
         style={{ minHeight, maxHeight }}>
      {/* 当前图 */}
      <img
        src={images[idx]}
        alt={`${idx + 1}/${images.length}`}
        className="w-full h-full object-contain"
        style={{ maxHeight }}
      />

      {/* 左右箭头 — 多图时显示 */}
      {images.length > 1 && (
        <>
          <button
            onClick={prev}
            className="absolute left-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full
                       bg-black/30 text-white text-sm flex items-center justify-center
                       opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/50"
          >
            ‹
          </button>
          <button
            onClick={next}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 rounded-full
                       bg-black/30 text-white text-sm flex items-center justify-center
                       opacity-0 group-hover:opacity-100 transition-opacity hover:bg-black/50"
          >
            ›
          </button>

          {/* 圆点指示器 */}
          <div className="absolute bottom-2 left-1/2 -translate-x-1/2 flex gap-1.5">
            {images.map((_, i) => (
              <span
                key={i}
                onClick={() => setIdx(i)}
                className={`w-1.5 h-1.5 rounded-full cursor-pointer transition-colors ${
                  i === idx ? 'bg-white' : 'bg-white/40'
                }`}
              />
            ))}
          </div>
        </>
      )}
    </div>
  );
}
