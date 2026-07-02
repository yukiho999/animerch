// ============================================
// 搜索栏 — 墨韵极简
// ============================================
import { useState, type KeyboardEvent } from 'react';

interface Props {
  onSearch: (query: string) => void;
  initialValue?: string;
}

export default function SearchBar({ onSearch, initialValue = '' }: Props) {
  const [value, setValue] = useState(initialValue);

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter') onSearch(value.trim());
  };

  return (
    <div className="relative">
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="搜索作品…"
        className="w-full h-9 pl-9 pr-3 rounded-full text-sm font-[var(--font-body)]
                   bg-white/[0.08] backdrop-blur border border-white/[0.08]
                   text-white placeholder-white/30
                   focus:outline-none focus:border-white/30 focus:bg-white/[0.12]
                   transition-all duration-300"
      />
      <svg className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-white/40"
           fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>
  );
}
