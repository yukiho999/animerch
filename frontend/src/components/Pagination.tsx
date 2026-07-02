// ============================================
// 分页
// ============================================
export default function Pagination({
  page, size, total, onPageChange,
}: {
  page: number; size: number; total: number;
  onPageChange: (p: number) => void;
}) {
  const totalPages = Math.ceil(total / size);
  if (totalPages <= 1) return null;

  const pages = getPages(page, totalPages);

  const btnBase = "px-2.5 py-1 rounded text-xs tracking-[0.04em] transition-colors border border-transparent";
  const btnActive = "bg-white/20 text-white border-white/20";
  const btnInactive = "text-white/40 hover:border-white/15 hover:text-white/70";

  return (
    <div className="flex items-center justify-center gap-1.5 mt-10">
      <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
        className={`${btnBase} text-white/30 disabled:opacity-30 disabled:cursor-default hover:text-white/60`}>
        ←
      </button>
      {pages.map((p, i) =>
        p === '...' ? (
          <span key={`d-${i}`} className="text-white/20 text-xs px-1">…</span>
        ) : (
          <button key={p} onClick={() => onPageChange(p as number)}
            className={`${btnBase} ${p === page ? btnActive : btnInactive}`}>
            {p}
          </button>
        )
      )}
      <button onClick={() => onPageChange(page + 1)} disabled={page >= totalPages}
        className={`${btnBase} text-white/30 disabled:opacity-30 disabled:cursor-default hover:text-white/60`}>
        →
      </button>
    </div>
  );
}

function getPages(c: number, t: number): (number | string)[] {
  if (t <= 7) return Array.from({ length: t }, (_, i) => i + 1);
  const r: (number | string)[] = [1];
  if (c > 3) r.push('...');
  for (let i = Math.max(2, c - 1); i <= Math.min(t - 1, c + 1); i++) r.push(i);
  if (c < t - 2) r.push('...');
  r.push(t);
  return r;
}
