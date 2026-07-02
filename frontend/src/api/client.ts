// ============================================
// API 调用封装 (axios)
// ============================================
import axios from 'axios';
import type { IPItem, IPListResult, MerchListResult, MerchDetail, CraftItem, StatsData } from '../types';

// 生产环境通过 VITE_API_BASE 环境变量指定后端地址
const baseURL = import.meta.env.VITE_API_BASE || '/api';

const api = axios.create({
  baseURL,
  timeout: 10000,
});

// ── IP ──
export async function fetchIPs(params?: { category?: string; search?: string; page?: number; size?: number }) {
  const { data } = await api.get<IPListResult>('/ip/ip', { params });
  return data;
}

export async function fetchIP(id: number) {
  const { data } = await api.get<IPItem>(`/ip/ip/${id}`);
  return data;
}

// ── 周边 ──
export async function fetchMerchList(params: {
  ip_id?: number;
  category?: string;
  craft?: string;
  is_discontinued?: number;
  search?: string;
  page?: number;
  size?: number;
}) {
  const { data } = await api.get<MerchListResult>('/merch/merch', { params });
  return data;
}

export async function fetchMerch(id: number) {
  const { data } = await api.get<MerchDetail>(`/merch/merch/${id}`);
  return data;
}

// ── 工艺 ──
export async function fetchCrafts() {
  const { data } = await api.get<CraftItem[]>('/merch/crafts');
  return data;
}

// ── 统计 ──
export async function fetchStats() {
  const { data } = await api.get<StatsData>('/merch/stats');
  return data;
}
