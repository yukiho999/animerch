// ============================================
// 全局布局 — 极简墨韵 + 子页面背景
// ============================================
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import SubPageBackground from './SubPageBackground';

export default function Layout() {
  return (
    <div className="flex flex-col min-h-screen">
      <SubPageBackground />
      <Navbar />
      <main className="flex-1 relative z-10">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
