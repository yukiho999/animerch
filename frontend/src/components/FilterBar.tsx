// ============================================
// 筛选栏 — 日式极简下拉
// ============================================
interface Props {
  categories?: { label: string; value: string }[];
  crafts?: { id: number; name: string }[];
  selectedCategory: string;
  selectedCraft: string;
  selectedDiscontinued: string;
  onCategoryChange: (v: string) => void;
  onCraftChange: (v: string) => void;
  onDiscontinuedChange: (v: string) => void;
}

const baseSelectCls =
  "appearance-none px-3 py-2 pr-7 rounded-md text-xs tracking-[0.04em] " +
  "bg-white/[0.08] backdrop-blur border border-white/[0.08] text-white/70 " +
  "focus:outline-none focus:border-white/30 cursor-pointer transition-colors";

export default function FilterBar(props: Props) {
  const { selectedCategory, selectedCraft, selectedDiscontinued,
          onCategoryChange, onCraftChange, onDiscontinuedChange } = props;
  const crafts = props.crafts || [];
  const categories = props.categories || defaultCategories;

  const hasFilter = selectedCategory || selectedCraft || selectedDiscontinued;

  return (
    <div className="flex flex-wrap gap-3 items-center">
      {/* 品类 */}
      <div className="relative">
        <select value={selectedCategory} onChange={e => onCategoryChange(e.target.value)} className={baseSelectCls}>
          <option value="">全部种类</option>
          {categories.map(c => <option key={c.value} value={c.value}>{c.label}</option>)}
        </select>
      </div>

      {/* 工艺 */}
      <div className="relative">
        <select value={selectedCraft} onChange={e => onCraftChange(e.target.value)} className={baseSelectCls}>
          <option value="">全部工艺</option>
          {crafts.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
        </select>
      </div>

      {/* 绝版 */}
      <div className="relative">
        <select value={selectedDiscontinued} onChange={e => onDiscontinuedChange(e.target.value)} className={baseSelectCls}>
          <option value="">全部状态</option>
          <option value="0">在售</option>
          <option value="1">绝版</option>
        </select>
      </div>

      {/* 清除 */}
      {hasFilter && (
        <button
          onClick={() => { onCategoryChange(''); onCraftChange(''); onDiscontinuedChange(''); }}
          className="text-[0.7rem] tracking-[0.04em] text-white/40 hover:text-white transition-colors underline underline-offset-2"
        >
          清除筛选
        </button>
      )}
    </div>
  );
}

const defaultCategories = [
  { label: '吧唧', value: '吧唧' },
  { label: '色纸', value: '色纸' },
  { label: '亚克力立牌', value: '亚克力立牌' },
  { label: '粘土人', value: '粘土人' },
  { label: '挂件', value: '挂件' },
  { label: '文件夹', value: '文件夹' },
  { label: '海报', value: '海报' },
  { label: '立牌', value: '立牌' },
  { label: '其他', value: '其他' },
];
