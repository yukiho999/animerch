// ============================================
// IP 详情页 — 墨韵
// ============================================
import { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import MerchCard from '../components/MerchCard';
import FilterBar from '../components/FilterBar';
import Pagination from '../components/Pagination';
import { CardSkeleton } from '../components/Skeleton';
import { fetchIP, fetchMerchList, fetchCrafts } from '../api/client';
import type { IPItem, MerchItem, CraftItem } from '../types';

export default function IPDetailPage() {
  const { id } = useParams<{ id: string }>();
  const ipId = Number(id);
  const [ip, setIP] = useState<IPItem | null>(null);
  const [merchs, setMerchs] = useState<MerchItem[]>([]);
  const [crafts, setCrafts] = useState<CraftItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [category, setCategory] = useState('');
  const [craft, setCraft] = useState('');
  const [disc, setDisc] = useState('');
  const [page, setPage] = useState(1);
  const PS = 20;

  useEffect(() => { fetchIP(ipId).then(setIP).catch(() => setIP(null)); fetchCrafts().then(setCrafts).catch(() => {}); }, [id]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const params: any = { ip_id: ipId, page, size: PS };
      if (category) params.category = category;
      if (craft) params.craft = craft;
      if (disc !== '') params.is_discontinued = Number(disc);
      const d = await fetchMerchList(params);
      setMerchs(d.items); setTotal(d.total);
    } catch {} finally { setLoading(false); }
  }, [ipId, category, craft, disc, page]);
  useEffect(() => { load(); }, [load]);

  const cCat = (v: string) => { setCategory(v); setPage(1); };
  const cCraft = (v: string) => { setCraft(v); setPage(1); };
  const cDisc = (v: string) => { setDisc(v); setPage(1); };

  return (
    <div className="max-w-6xl mx-auto px-5 py-8">
      {/* 返回键 — 单独一行 */}
      <Link to="/ip" className="inline-flex items-center gap-1 text-xs text-white/50 hover:text-white no-underline tracking-[0.06em] transition-colors duration-300 mb-6">
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 19l-7-7 7-7" />
        </svg>
        返回作品一览
      </Link>

      {ip && (
        <div className="mb-6">
          <h1 className="font-[var(--font-display)] text-2xl font-bold text-white tracking-[0.06em] mb-1">
            <span className="text-4xl mr-3 align-middle">{ipEmoji(ip.name)}</span>
            {ip.name}
          </h1>
          <p className="text-xs text-white/50 mt-2">{ip.category} · {ip.merch_count} 件周边</p>
          {ip.description && <p className="text-xs text-white/60 mt-2 leading-relaxed max-w-xl">{ip.description}</p>}
        </div>
      )}

      <div className="mb-6">
        <FilterBar crafts={crafts} selectedCategory={category} selectedCraft={craft} selectedDiscontinued={disc}
          onCategoryChange={cCat} onCraftChange={cCraft} onDiscontinuedChange={cDisc} />
      </div>

      {loading ? <CardSkeleton count={8} /> : merchs.length > 0 ? (
        <>
          <p className="text-[0.65rem] text-white/40 mb-4">共 {total} 件</p>
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-5">
            {merchs.map(m => <div key={m.id} className="anim-fade-up"><MerchCard merch={m} /></div>)}
          </div>
          <Pagination page={page} size={PS} total={total} onPageChange={setPage} />
        </>
      ) : (
        <div className="text-center py-16 text-white/40 text-sm">该作品暂无周边数据</div>
      )}
    </div>
  );
}

function ipEmoji(n: string): string {
  const m: Record<string, string> = { '魔道祖师':'🐇','天官赐福':'🏮','人鱼陷落':'🧜','长歌行':'⚔️','星梦偶像计划':'⭐','非人哉':'🦊','第五人格':'🎭','十日终焉':'⏳','网球王子':'🎾','偶像梦幻祭':'🌟' };
  return m[n] || '📖';
}
