// ============================================
// 导航栏 — 墨韵极简
// ============================================
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import SearchBar from './SearchBar';

export default function Navbar() {
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 bg-white/[0.15] backdrop-blur-xl border-b border-white/10"
         style={{ boxShadow: '0 1px 0 rgba(255,255,255,0.06)' }}>
      <div className="max-w-6xl mx-auto px-5 h-14 flex items-center justify-between">
        {/* Logo — 墨韵风 */}
        <Link to="/" className="flex items-center gap-2 no-underline group" onClick={() => setOpen(false)}>
          <span className="font-[var(--font-display)] text-xl font-bold tracking-[0.08em] text-white group-hover:text-[var(--c-gold-light)] transition-colors duration-300">
            桐桐的吃谷日记
          </span>
        </Link>

        {/* 搜索 — 桌面 */}
        <div className="hidden md:block w-64">
          <SearchBar onSearch={(q) => navigate(`/?search=${encodeURIComponent(q)}`)} />
        </div>

        {/* 导航 — 桌面 */}
        <div className="hidden md:flex items-center gap-8">
          {[
            { to: '/', label: '首页' },
          ].map(l => (
            <Link
              key={l.to}
              to={l.to}
              className="text-sm tracking-[0.06em] text-white/70 hover:text-white no-underline transition-colors duration-300 font-[var(--font-display)]"
            >
              {l.label}
            </Link>
          ))}
        </div>

        {/* 汉堡 — 移动 */}
        <button className="md:hidden text-white text-xl p-1" onClick={() => setOpen(!open)}>
          {open ? '✕' : '☰'}
        </button>
      </div>

      {/* 移动菜单 */}
      {open && (
        <div className="md:hidden bg-black/30 backdrop-blur-xl border-t border-white/10 px-5 py-4 space-y-3">
          <SearchBar onSearch={(q) => { navigate(`/?search=${encodeURIComponent(q)}`); setOpen(false); }} />
          {[
            { to: '/', label: '首页' },
          ].map(l => (
            <Link key={l.to} to={l.to} onClick={() => setOpen(false)}
              className="block text-sm tracking-[0.06em] text-white/70 hover:text-white no-underline py-1.5 font-[var(--font-display)]">
              {l.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}
