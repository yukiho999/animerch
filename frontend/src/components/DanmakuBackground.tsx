// ============================================
// 弹幕背景 — 文字从右向左飘过（仿 B 站弹幕）
// ============================================
import { useEffect, useRef, useMemo } from 'react';

const DANMAKU_TEXTS = [
  '今日份试手气~',
  '难道我是自推绝缘体吗',
  '这个柄图太权威了',
  '祝我一发出自推',
  'IP错误',
  '关山万里路，拔剑起长歌！',
  '身在无间，心在桃源',
  '手中无武器，我心永忠诚',
  '回忆的书页可以推开噩梦',
  '我命由我，不问凶吉',
  '祝各位老师吃谷愉快',
];

interface DanmakuItem {
  id: number;
  text: string;
  y: number;          // 垂直位置 (百分比)
  speed: number;      // 像素/秒
  fontSize: number;   // px
  opacity: number;
  x: number;          // 当前水平位置 (像素)
}

export default function DanmakuBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const itemsRef = useRef<DanmakuItem[]>([]);
  const idCounter = useRef(0);

  // 初始化弹幕池
  const initItems = (canvasWidth: number, canvasHeight: number): DanmakuItem[] => {
    const items: DanmakuItem[] = [];
    // 生成 20~30 条弹幕铺满屏幕
    const count = 22;
    for (let i = 0; i < count; i++) {
      const text = DANMAKU_TEXTS[i % DANMAKU_TEXTS.length];
      items.push(createDanmaku(canvasWidth, canvasHeight, text, true));
    }
    return items;
  };

  const createDanmaku = (
    canvasWidth: number,
    canvasHeight: number,
    text: string,
    randomX: boolean,
  ): DanmakuItem => {
    const fontSize = 14 + Math.random() * 18; // 14~32px
    const speed = 30 + Math.random() * 60;     // 30~90 px/s
    const y = 5 + Math.random() * (canvasHeight - fontSize - 10);
    const x = randomX
      ? Math.random() * canvasWidth * 1.5 + canvasWidth * 0.3  // 散布在屏幕各处
      : canvasWidth + Math.random() * 200;                       // 从右侧外开始
    const opacity = 0.08 + Math.random() * 0.1; // 8%~18% 透明度
    return {
      id: idCounter.current++,
      text,
      y,
      speed,
      fontSize,
      opacity,
      x,
    };
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animId: number;
    let lastTime = performance.now();

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      itemsRef.current = initItems(canvas.width, canvas.height);
    };
    resize();
    window.addEventListener('resize', resize);

    const animate = (now: number) => {
      const dt = Math.min((now - lastTime) / 1000, 0.1); // 防止跳帧过大
      lastTime = now;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const w = canvas.width;
      const h = canvas.height;

      for (const item of itemsRef.current) {
        // 移动
        item.x -= item.speed * dt;

        // 完全滑出左侧 → 从右侧重新进入
        if (item.x < -measureTextWidth(ctx, item.text, item.fontSize) - 50) {
          item.x = w + 50 + Math.random() * 300;
          item.y = 5 + Math.random() * (h - item.fontSize - 10);
          item.speed = 30 + Math.random() * 60;
          item.opacity = 0.08 + Math.random() * 0.1;
        }

        // 绘制
        ctx.save();
        ctx.globalAlpha = item.opacity;
        ctx.fillStyle = '#ffffff';
        ctx.font = `${item.fontSize}px "SimSun", "STSong", "宋体", serif`;
        ctx.textBaseline = 'top';
        // 给文字加微弱发光，更有弹幕感
        ctx.shadowColor = 'rgba(255, 255, 255, 0.3)';
        ctx.shadowBlur = 4;
        ctx.fillText(item.text, item.x, item.y);
        ctx.restore();
      }

      animId = requestAnimationFrame(animate);
    };
    animId = requestAnimationFrame(animate);

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animId);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none z-[1]"
      style={{ background: 'transparent' }}
    />
  );
}

/** 估算文字宽度（canvas measureText 不够精确但够用） */
function measureTextWidth(
  ctx: CanvasRenderingContext2D,
  text: string,
  fontSize: number,
): number {
  ctx.save();
  ctx.font = `${fontSize}px "SimSun", "STSong", "宋体", serif`;
  const m = ctx.measureText(text);
  ctx.restore();
  return m.width;
}
