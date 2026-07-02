// ============================================
// 首页 — 全屏入口（粒子 + 弹幕 + 涟漪 + 渐变背景）
// ============================================
import ParticleBackground from '../components/ParticleBackground';
import DanmakuBackground from '../components/DanmakuBackground';
import ClickRipple from '../components/ClickRipple';
import HomeEntry from '../components/HomeEntry';
import GradientBg from '../components/GradientBg';

export default function HomePage() {
  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      <GradientBg />
      <ParticleBackground />
      <DanmakuBackground />
      <HomeEntry />
      <ClickRipple />
    </div>
  );
}
