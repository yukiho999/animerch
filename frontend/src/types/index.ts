// ============================================
// TypeScript 类型定义
// ============================================

export interface IPItem {
  id: number;
  name: string;
  aliases: string[];
  category: string | null;
  cover_url: string | null;
  description: string | null;
  merch_count: number;
  created_at: string;
  updated_at: string;
}

export interface IPListResult {
  items: IPItem[];
  total: number;
  page: number;
  size: number;
}

export interface MerchItem {
  id: number;
  ip_id: number;
  ip_name: string;
  name: string;
  category: CategoryType | null;
  official_price: number | null;
  release_date: string | null;
  release_method: ReleaseMethod | null;
  is_discontinued: boolean;
  attributes: Record<string, unknown> | null;
  image_url: string | null;
  source_platform: string | null;
  source_url: string | null;
  crafts: string[];
  created_at: string;
}

export interface MerchDetail extends MerchItem {
  updated_at: string;
}

export interface MerchListResult {
  items: MerchItem[];
  total: number;
  page: number;
  size: number;
}

export interface CraftItem {
  id: number;
  name: string;
}

export interface StatsData {
  total_merch: number;
  total_ip: number;
  total_crafts: number;
  ip_distribution: { ip_name: string; ip_id: number; count: number }[];
  category_distribution: { category: string; count: number }[];
  recent_updates: number;
}

export type CategoryType =
  | '吧唧'
  | '色纸'
  | '亚克力立牌'
  | '粘土人'
  | '挂件'
  | '文件夹'
  | '海报'
  | '立牌'
  | '其他';

export type ReleaseMethod =
  | '通贩'
  | '场贩'
  | '受注'
  | '限定'
  | '抽选'
  | '未知';

export const CATEGORY_LABELS: Record<string, string> = {
  '吧唧': '🔴 吧唧',
  '色纸': '🟨 色纸',
  '亚克力立牌': '🟦 亚克力立牌',
  '粘土人': '🧸 粘土人',
  '挂件': '🔑 挂件',
  '文件夹': '📁 文件夹',
  '海报': '🖼️ 海报',
  '立牌': '🟪 立牌',
  '其他': '📦 其他',
};

export const METHOD_LABELS: Record<string, string> = {
  '通贩': '🌐 通贩',
  '场贩': '🏟️ 场贩',
  '受注': '📋 受注',
  '限定': '⭐ 限定',
  '抽选': '🎲 抽选',
  '未知': '❓ 未知',
};
