// ============================================
// 骨架屏
// ============================================
export function CardSkeleton({ count = 8 }: { count?: number }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
      {Array.from({ length: count }).map((_, i) => (
        <div key={i} className="bg-white/[0.05] backdrop-blur border border-white/[0.06] rounded-md overflow-hidden animate-pulse">
          <div className="h-44 bg-white/[0.04]" />
          <div className="p-3 space-y-2">
            <div className="h-3 w-16 bg-white/[0.06] rounded" />
            <div className="h-4 w-full bg-white/[0.06] rounded" />
            <div className="h-3 w-1/2 bg-white/[0.06] rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function DetailSkeleton() {
  return (
    <div className="max-w-3xl mx-auto px-5 py-10 animate-pulse">
      <div className="h-6 w-40 bg-white/[0.06] rounded mb-6" />
      <div className="h-64 w-full bg-white/[0.04] rounded-md mb-8" />
      <div className="h-5 w-2/3 bg-white/[0.06] rounded mb-3" />
      <div className="h-4 w-1/2 bg-white/[0.06] rounded" />
    </div>
  );
}
