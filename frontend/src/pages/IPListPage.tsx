// ============================================
// IP 列表页 — 仿 boke ref 风格（3 列 + 动画标签切换 + 数字分页）
// ============================================
import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import IPCard from '../components/IPCard';
import MerchCard from '../components/MerchCard';
import { CardSkeleton } from '../components/Skeleton';
import { fetchIPs, fetchMerchList } from '../api/client';
import type { IPItem, MerchItem, IPListResult } from '../types';

const CAT_TABS = [
  { label: '全部', value: '' },
  { label: '动漫', value: '动漫' },
  { label: '小说', value: '小说' },
  { label: '游戏', value: '游戏' },
];

const PS = 12; // page size

export default function IPListPage() {
  const [searchParams] = useSearchParams();
  const searchQuery = searchParams.get('search') || '';

  const [ips, setIps] = useState<IPItem[]>([]);
  const [merchs, setMerchs] = useState<MerchItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeCat, setActiveCat] = useState('');
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const [jumpInput, setJumpInput] = useState('');

  const totalPages = Math.max(1, Math.ceil(total / PS));

  useEffect(() => {
    setLoading(true);
    if (searchQuery) {
      fetchMerchList({ search: searchQuery, size: 50 }).then((data) => {
        setMerchs(data.items);
        setLoading(false);
      });
    } else {
      fetchIPs({ category: activeCat || undefined, page, size: PS }).then((data: IPListResult) => {
        setIps(data.items.filter((ip) => ip.name !== '其他未分类'));
        setTotal(data.total);
        setMerchs([]);
        setLoading(false);
      });
    }
  }, [activeCat, page, searchQuery]);

  // reset page on category change
  useEffect(() => {
    setPage(1);
  }, [activeCat]);

  const handleJump = () => {
    const n = parseInt(jumpInput, 10);
    if (n >= 1 && n <= totalPages) {
      setPage(n);
      setJumpInput('');
    }
  };

  const handleJumpKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleJump();
  };

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-12">
      {/* 标题区 */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-6 md:mb-10"
      >
        <div className="flex items-center gap-2 md:gap-3 mb-1 md:mb-2">
          <svg className="w-5 h-5 md:w-7 md:h-7 text-sky-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
              d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h1 className="text-xl md:text-3xl font-bold text-white">
            {searchQuery ? `搜索：「${searchQuery}」` : '作品一览'}
          </h1>
        </div>
        {!searchQuery && (
          <p className="text-sm md:text-base text-white/40 ml-7 md:ml-10">
            追踪你最爱的 IP 周边发行信息
          </p>
        )}
      </motion.div>

      {/* 分类标签 — glass pill 切换 */}
      {!searchQuery && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.15 }}
          className="mb-5 md:mb-8 flex flex-wrap gap-1.5 md:gap-2"
        >
          {CAT_TABS.map((c) => {
            const active = activeCat === c.value;
            return (
              <button
                key={c.label}
                type="button"
                onClick={() => setActiveCat(c.value)}
                className={`relative px-3 py-1.5 md:px-5 md:py-2 rounded-2xl text-xs md:text-sm font-medium transition-all duration-300 ${
                  active
                    ? 'text-white shadow-lg shadow-sky-500/20'
                    : 'text-white/50 bg-white/[0.05] backdrop-blur-xl border border-white/[0.08] hover:bg-white/[0.1]'
                }`}
              >
                {active && (
                  <motion.div
                    layoutId="activeCategoryBg"
                    className="absolute inset-0 rounded-2xl bg-gradient-to-r from-sky-500 to-cyan-400"
                    transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{c.label}</span>
              </button>
            );
          })}
        </motion.div>
      )}

      {/* 搜索结果 — 周边直接展示 */}
      {searchQuery && (
        <AnimatePresence mode="wait">
          {loading ? (
            <CardSkeleton count={8} />
          ) : merchs.length > 0 ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-6"
            >
              {merchs.map((m, i) => (
                <MerchCard key={m.id} merch={m} index={i} />
              ))}
            </motion.div>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-white/40">
              <svg className="w-12 h-12 mb-4 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <p>未找到相关周边</p>
            </div>
          )}
        </AnimatePresence>
      )}

      {/* IP 列表 */}
      {!searchQuery && (
        <AnimatePresence mode="wait">
          {loading ? (
            <div className="flex items-center justify-center py-32">
              <div className="w-8 h-8 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin" />
            </div>
          ) : ips.length > 0 ? (
            <>
              <motion.div
                key={`${activeCat || 'all'}-${page}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.3 }}
                className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 md:gap-6"
              >
                {ips.map((ip, i) => (
                  <IPCard key={ip.id} ip={ip} index={i} />
                ))}
              </motion.div>

              {/* 数字分页 — 标签页风格 */}
              {totalPages > 1 && (
                <div className="flex items-center justify-center gap-1.5 mt-10 flex-wrap">
                  {/* 上一页 */}
                  <button
                    onClick={() => setPage(page - 1)}
                    disabled={page <= 1}
                    className="px-2.5 py-1.5 rounded text-xs text-white/30 disabled:opacity-30 disabled:cursor-default hover:text-white/60 transition-colors"
                  >
                    ←
                  </button>

                  {/* 页码 1 2 3 ... n */}
                  {getPageNumbers(page, totalPages).map((p, i) =>
                    p === '...' ? (
                      <span key={`d-${i}`} className="text-white/20 text-xs px-1">…</span>
                    ) : (
                      <button
                        key={p}
                        onClick={() => setPage(p as number)}
                        className={`min-w-[2rem] h-8 px-2 rounded text-sm font-medium transition-all duration-200 ${
                          p === page
                            ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20'
                            : 'text-white/50 hover:text-white/80 hover:bg-white/[0.08]'
                        }`}
                      >
                        {p}
                      </button>
                    )
                  )}

                  {/* 下一页 */}
                  <button
                    onClick={() => setPage(page + 1)}
                    disabled={page >= totalPages}
                    className="px-2.5 py-1.5 rounded text-xs text-white/30 disabled:opacity-30 disabled:cursor-default hover:text-white/60 transition-colors"
                  >
                    →
                  </button>

                  {/* 跳转输入 */}
                  <span className="text-xs text-white/30 ml-3">跳至</span>
                  <input
                    type="number"
                    min={1}
                    max={totalPages}
                    value={jumpInput}
                    onChange={(e) => setJumpInput(e.target.value)}
                    onKeyDown={handleJumpKey}
                    placeholder={`${totalPages}`}
                    className="w-12 h-8 px-2 rounded bg-white/[0.06] border border-white/[0.12] text-white text-xs text-center placeholder:text-white/20 focus:outline-none focus:border-sky-500/50 transition-colors [appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"
                  />
                  <button
                    onClick={handleJump}
                    className="px-2.5 py-1 rounded text-xs text-sky-400 hover:text-sky-300 hover:bg-white/[0.06] transition-colors"
                  >
                    GO
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="flex flex-col items-center justify-center py-32 text-white/40">
              <svg className="w-12 h-12 mb-4 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1}
                  d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <p>暂无作品数据</p>
            </div>
          )}
        </AnimatePresence>
      )}
    </div>
  );
}

function getPageNumbers(c: number, t: number): (number | string)[] {
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1);
  const r: (number | string)[] = [1];
  if (c > 3) r.push('...');
  for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) r.push(i);
  if (c < t - 2) r.push('...');
  r.push(t);
  return r;
}
