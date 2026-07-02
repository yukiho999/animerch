// ============================================
// 首页入口 — 居中标题 + 点击跳转（延迟，让水波纹可见）
// ============================================
import { useState, type KeyboardEvent } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomeEntry() {
  const navigate = useNavigate();
  const [leaving, setLeaving] = useState(false);
  const [searchValue, setSearchValue] = useState('');

  const handleClick = () => {
    if (leaving) return;
    setLeaving(true);
    setTimeout(() => navigate('/ip'), 400);
  };

  const handleSearch = (e: KeyboardEvent) => {
    if (e.key === 'Enter' && searchValue.trim()) {
      if (leaving) return;
      setLeaving(true);
      setTimeout(() => navigate(`/ip?search=${encodeURIComponent(searchValue.trim())}`), 400);
    }
  };

  const handleSearchStop = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      className="relative z-10 flex flex-col items-center justify-center h-screen w-full cursor-pointer select-none"
      onClick={handleClick}
    >
      <div className="flex flex-col items-center w-full px-4">
        {/* 搜索框 */}
        <div className="relative w-full max-w-2xl mb-8" onClick={handleSearchStop}>
          <input
            type="text"
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            onKeyDown={handleSearch}
            placeholder="搜索周边…"
            className="w-full h-12 pl-10 pr-4 rounded-full text-base
                       bg-white/[0.07] backdrop-blur border border-white/[0.08]
                       text-white placeholder-white/25
                       focus:outline-none focus:border-white/25 focus:bg-white/[0.12]
                       transition-all duration-300 text-center"
          />
          <svg className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30"
               fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* 主标题 */}
        <h1
          className="text-6xl sm:text-7xl lg:text-8xl text-white mb-6 text-center leading-tight"
          style={{
            fontFamily: 'Handwrite, cursive',
            textShadow: '0 0 40px rgba(255,255,255,0.15), 0 0 80px rgba(255,255,255,0.08)',
            letterSpacing: '0.15em',
            fontWeight: 400,
          }}
        >
          桐桐的吃谷日记
        </h1>

        {/* 英文标题 */}
        <p
          className="text-white/45 text-xl sm:text-2xl tracking-[0.12em] mb-3"
          style={{ fontFamily: "'Reenie Beanie', cursive", transform: 'rotate(-1deg)' }}
        >
          TongTong's Merch Diary
        </p>

        {/* 简介 */}
        <p className="text-white/30 text-sm tracking-[0.1em] max-w-md text-center leading-relaxed">
          追踪你最爱的 IP 周边发行信息
        </p>
      </div>

      {/* 底部提示 */}
      <div className="absolute bottom-12 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
        <span className="text-white/15 text-xs tracking-[0.15em] animate-pulse">
          点击任意位置进入
        </span>
        <div className="w-px h-6 bg-gradient-to-b from-white/15 to-transparent" />
      </div>
    </div>
  );
}
