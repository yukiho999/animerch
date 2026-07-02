// ============================================
// 工艺标签 — 日式极简
// ============================================
export default function CraftTag({ name, onClick }: { name: string; onClick?: () => void }) {
  return (
    <span
      className="craft-pill cursor-pointer"
      onClick={onClick}
    >
      {name}
    </span>
  );
}
