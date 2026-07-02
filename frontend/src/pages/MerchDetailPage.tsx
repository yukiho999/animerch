// ============================================
// 周边详情页 — 墨韵 + 多图轮播
// ============================================
import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { DetailSkeleton } from '../components/Skeleton';
import { fetchMerch } from '../api/client';
import type { MerchDetail } from '../types';

const API_BASE_IMG = import.meta.env.VITE_API_BASE || '/api';

function proxyUrl(u: string): string {
  return `${API_BASE_IMG}/proxy/image?url=${encodeURIComponent(u)}`;
}

function parseImages(url: string | null): string[] {
  if (!url) return [];
  if (url.includes('，') || url.includes(',')) return url.split(/[，,]+/).map(s => proxyUrl(s.trim())).filter(Boolean);
  return [proxyUrl(url)];
}

export default function MerchDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [m, setM] = useState<MerchDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [imgIdx, setImgIdx] = useState(0);

  useEffect(() => { fetchMerch(Number(id)).then(setM).finally(() => setLoading(false)); }, [id]);

  if (loading) return <DetailSkeleton />;
  if (!m) return <div className="text-center py-20 text-white/40 text-sm font-[var(--font-display)]">周边不存在</div>;

  const images = parseImages(m.image_url);
  const goPrev = () => setImgIdx((imgIdx - 1 + images.length) % images.length);
  const goNext = () => setImgIdx((imgIdx + 1) % images.length);

  return (
    <div className="max-w-3xl mx-auto px-5 py-8">
      {/* 导航区 — 作品一览在上，IP名称在下，左上角对齐 */}
      <div className="flex flex-col items-start gap-1 mb-6">
        <Link to="/ip" className="inline-flex items-center gap-1 text-xs text-white/50 hover:text-white no-underline tracking-[0.06em] transition-colors duration-300">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 19l-7-7 7-7" />
          </svg>
          作品一览
        </Link>

        <Link to={`/ip/${m.ip_id}`} className="text-xs text-white/50 hover:text-white no-underline tracking-[0.06em] transition-colors duration-300">
          ← {m.ip_name}
        </Link>
      </div>

      {/* 图片轮播 */}
      <div className="mt-4 mb-8 border border-white/[0.08] rounded-lg overflow-hidden bg-white/[0.05] backdrop-blur relative">
        {images.length > 0 ? (
          <>
            <img src={images[imgIdx]} alt={`${m.name} - ${imgIdx + 1}/${images.length}`}
                 className="w-full object-contain" style={{ maxHeight: '60vh' }} />

            {images.length > 1 && (
              <>
                <button onClick={goPrev} className="absolute left-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/25 text-white text-xl flex items-center justify-center hover:bg-black/40 transition-colors duration-300">‹</button>
                <button onClick={goNext} className="absolute right-3 top-1/2 -translate-y-1/2 w-10 h-10 rounded-full bg-black/25 text-white text-xl flex items-center justify-center hover:bg-black/40 transition-colors duration-300">›</button>

                {/* 缩略图 */}
                <div className="absolute bottom-3 left-1/2 -translate-x-1/2 flex gap-2 bg-black/25 backdrop-blur-sm rounded-full px-3 py-2">
                  {images.map((src, i) => (
                    <img key={i} src={src} onClick={() => setImgIdx(i)}
                      className={`w-9 h-9 rounded object-cover cursor-pointer border-2 transition-all duration-300 ${i === imgIdx ? 'border-white opacity-100' : 'border-transparent opacity-50 hover:opacity-75'}`} />
                  ))}
                </div>

                <div className="absolute top-3 right-3 bg-black/30 backdrop-blur-sm text-white text-xs px-2.5 py-1 rounded-full tracking-[0.06em]">
                  {imgIdx + 1} / {images.length}
                </div>
              </>
            )}
          </>
        ) : (
          <div className="flex items-center justify-center min-h-[200px] text-5xl opacity-15">🖼</div>
        )}
      </div>

      {/* 信息卡 */}
      <div className="card-white p-6 sm:p-8 mb-6">
        <div className="flex flex-wrap items-start justify-between gap-4 mb-6">
          <div>
            <h1 className="font-[var(--font-display)] text-xl font-bold text-white tracking-[0.05em] leading-snug mb-2">{m.name}</h1>
            <div className="flex items-center gap-2 text-xs">
              <Link to={`/ip/${m.ip_id}`} className="text-[var(--c-gold-light)] hover:underline no-underline font-medium">{m.ip_name}</Link>
              {m.is_discontinued && <span className="px-1.5 py-0.5 rounded-sm text-[0.6rem] bg-red-50 text-red-500 border border-red-100">绝版</span>}
            </div>
          </div>
          {m.official_price ? (
            <div className="text-right">
              <div className="font-[var(--font-display)] text-2xl font-bold text-white">¥{Math.round(m.official_price)}</div>
              <div className="text-[0.6rem] text-white/40 mt-0.5 tracking-[0.06em]">官方发售价</div>
            </div>
          ) : null}
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-5 py-4 border-t border-white/[0.06]">
          <Info label="种类" value={LABELS.cat[m.category || ''] || m.category || '未知'} />
          <Info label="发售方式" value={LABELS.method[m.release_method || ''] || m.release_method || '未知'} />
          <Info label="发售日期" value={m.release_date || '待定'} />
          <Info label="来源" value={m.source_platform || '未知'} />
        </div>
      </div>

      {/* 工艺 */}
      {m.crafts.length > 0 && (
        <div className="card-white p-5 mb-6">
          <h3 className="text-xs font-bold text-white/50 tracking-[0.12em] uppercase mb-4">工艺</h3>
          <div className="flex flex-wrap gap-2">
            {m.crafts.map(c => <span key={c} className="craft-pill">{c}</span>)}
          </div>
        </div>
      )}

      {m.source_url && (
        <div className="text-center mt-8">
          <a href={m.source_url} target="_blank" rel="noopener noreferrer"
             className="text-xs text-white/40 hover:text-white underline-offset-2 underline tracking-[0.06em] transition-colors duration-300">
            查看原始帖子 →
          </a>
        </div>
      )}
    </div>
  );
}

function Info({ label, value }: { label: string; value: string }) {
  return <div><div className="text-[0.65rem] text-white/40 mb-1 tracking-[0.08em] font-medium">{label}</div><div className="text-sm text-white/80">{value}</div></div>;
}

const LABELS: Record<string, Record<string, string>> = {
  cat: { '吧唧': '吧唧','色纸': '色纸','亚克力立牌': '亚克力立牌','粘土人': '粘土人','挂件': '挂件','文件夹': '文件夹','海报': '海报','立牌': '立牌','其他': '其他' },
  method: { '通贩': '通贩','场贩': '场贩','受注': '受注','限定': '限定','抽选': '抽选','未知': '未知' },
};
