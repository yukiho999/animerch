// ============================================
// 页脚 — 极简墨韵
// ============================================
export default function Footer() {
  return (
    <footer className="border-t border-white/10 bg-transparent mt-auto">
      <div className="max-w-6xl mx-auto px-5 py-8 flex flex-col sm:flex-row items-center justify-between gap-2 text-xs text-white/40 tracking-[0.06em] font-[var(--font-body)]">
        <span>© 2026 桐桐的吃谷日记 — 追踪你爱的IP周边</span>
        <span>数据来源：微博等公开社交平台</span>
      </div>
    </footer>
  );
}
