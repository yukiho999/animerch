// ============================================
// 统计区块 — 墨韵
// ============================================
import type { StatsData } from '../types';

export default function StatsSection({ stats }: { stats: StatsData }) {
  return (
    <section className="max-w-6xl mx-auto">
      <h2 className="section-title mb-8">数据概览</h2>

      <div className="grid sm:grid-cols-2 gap-8">
        {/* IP 排行 */}
        <div className="card-white p-5">
          <h3 className="text-xs font-bold text-white/50 tracking-[0.12em] uppercase mb-5">热门作品</h3>
          <div className="space-y-4">
            {stats.ip_distribution.filter(i => i.ip_name !== '其他未分类').slice(0, 8).map(item => {
              const maxCount = stats.ip_distribution[0]?.count || 1;
              const pct = Math.round((item.count / maxCount) * 100);
              return (
                <div key={item.ip_id} className="flex items-center gap-3">
                  <span className="text-xs text-white/80 w-24 truncate font-[var(--font-display)]">{item.ip_name}</span>
                  <div className="flex-1 h-1.5 rounded-full bg-white/[0.08] overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-[var(--c-gold-light)] to-[var(--c-gold)] transition-all duration-700 ease-out" style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-[0.65rem] text-white/50 w-6 text-right">{item.count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* 品类分布 */}
        <div className="card-white p-5">
          <h3 className="text-xs font-bold text-white/50 tracking-[0.12em] uppercase mb-5">品类分布</h3>
          <div className="space-y-3">
            {stats.category_distribution.map(item => {
              const total = stats.total_merch || 1;
              const pct = Math.round((item.count / total) * 100);
              return (
                <div key={item.category} className="flex items-center gap-2">
                  <span className="text-xs text-white/80 w-20">{item.category}</span>
                  <span className="text-[0.65rem] text-white/40">{item.count}</span>
                  <div className="flex-1 h-1 rounded-full bg-white/[0.08] overflow-hidden">
                    <div className="h-full rounded-full bg-white/15" style={{ width: `${Math.max(pct, 4)}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
