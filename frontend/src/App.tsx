// ============================================
// 应用路由入口
// ============================================
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import IPListPage from './pages/IPListPage';
import IPDetailPage from './pages/IPDetailPage';
import MerchDetailPage from './pages/MerchDetailPage';

export default function App() {
  return (
    <Routes>
      {/* 首页 — 独立布局（无导航栏，全屏） */}
      <Route path="/" element={<HomePage />} />

      {/* 子页面 — Layout 布局（带导航栏） */}
      <Route element={<Layout />}>
        <Route path="/ip" element={<IPListPage />} />
        <Route path="/ip/:id" element={<IPDetailPage />} />
        <Route path="/merch/:id" element={<MerchDetailPage />} />
      </Route>
    </Routes>
  );
}
