// ============================================
// 首页 Banner — 墨韵主视觉
// ============================================

interface Props {
  stats?: { total_merch: number; total_ip: number; recent_updates: number };
}

export default function HeroBanner({ stats }: Props) {
  return (
    <section className="relative overflow-hidden border-b border-black/[0.03]">
      {/* 背景水墨光晕 */}

      {/* 装饰线 */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/15 to-transparent" />

      <div className="relative max-w-4xl mx-auto px-5 py-20 sm:py-28 text-center">
        {/* 上方墨韵装饰 */}
        <div className="flex items-center justify-center gap-0 mb-8">
          <span className="w-10 h-px bg-white/30" />
          <span className="mx-3 w-1.5 h-1.5 rounded-full bg-white/40" />
          <span className="w-14 h-px bg-white/20" />
          <span className="mx-3 w-1.5 h-1.5 rounded-full bg-white/40" />
          <span className="w-10 h-px bg-white/30" />
        </div>

        <h1 className="font-[var(--font-display)] text-4xl sm:text-5xl lg:text-6xl font-black text-white tracking-[0.1em] mb-6">
          桐桐的吃谷日记
        </h1>
        <p className="text-white/80 text-base sm:text-lg tracking-[0.08em] max-w-lg mx-auto mb-12 leading-loose font-[var(--font-body)]">
          追踪你最爱的 IP 周边发行信息
        </p>

        {/* 统计 — 三道竖线分隔 */}
        {stats && (
          <div className="flex flex-wrap justify-center items-center gap-8 sm:gap-14">
            <StatBox value={stats.total_ip} label="收录作品" />
            <div className="w-px h-10 bg-white/15 hidden sm:block" />
            <StatBox value={stats.total_merch} label="周边记录" />
            <div className="w-px h-10 bg-white/15 hidden sm:block" />
            <StatBox value={stats.recent_updates} label="近7天更新" accent />
          </div>
        )}

        {/* 底部装饰 */}
        <div className="absolute bottom-6 left-1/2 -translate-x-1/2 w-24 h-px bg-gradient-to-r from-transparent via-white/20 to-transparent" />
      </div>
    </section>
  );
}

function StatBox({ value, label, accent }: { value: number; label: string; accent?: boolean }) {
  return (
    <div className="flex flex-col items-center">
      <span className={`font-[var(--font-display)] text-2xl sm:text-3xl font-bold tracking-[0.04em] ${accent ? 'text-[var(--c-gold-light)]' : 'text-white'}`}>
        {value}
      </span>
      <span className="text-[0.68rem] text-white/60 tracking-[0.1em] mt-2 font-[var(--font-body)]">{label}</span>
    </div>
  );
}
