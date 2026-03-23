import Link from 'next/link';
import { LayoutDashboard, ScrollText, ArrowRight, Zap, Globe, Shield } from 'lucide-react';

export default function HomePage() {
  return (
    <div className="relative min-h-[calc(100vh-64px)] flex flex-col items-center justify-center overflow-hidden bg-zinc-950">
      {/* Background Glows */}
      <div className="absolute top-1/4 -left-20 w-96 h-96 bg-brand-primary/20 rounded-full blur-[128px] opacity-20" />
      <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-blue-600/20 rounded-full blur-[128px] opacity-20" />

      <div className="max-w-5xl mx-auto px-6 py-20 relative z-10 text-center space-y-12">
        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white/5 border border-white/10 text-brand-primary text-xs font-black tracking-widest uppercase animate-fade-in">
          <Zap className="w-4 h-4 fill-brand-primary" />
          AI Powered Strategy Center
        </div>

        {/* Hero Text */}
        <div className="space-y-6">
          <h1 className="text-6xl md:text-8xl font-black tracking-tighter text-white">
            掌握策略動向 <br />
            <span className="bg-gradient-to-r from-brand-primary to-orange-500 bg-clip-text text-transparent">
              洞悉市場先機
            </span>
          </h1>
          <p className="text-xl text-zinc-400 max-w-2xl mx-auto font-medium leading-relaxed">
            TradeView Strategy 提供專業級的策略抓取、高品質繁體中文轉譯以及即時系統管理，助您深入理解全球頂尖交易員的邏輯。
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-6 pt-8">
          <Link
            href="/scripts"
            className="group relative flex items-center gap-3 px-10 py-5 bg-brand-primary text-white rounded-[2rem] font-black text-lg transition-all hover:scale-105 active:scale-95 shadow-2xl shadow-brand-primary/20"
          >
            探索策略中心
            <ScrollText className="w-6 h-6 transition-transform group-hover:rotate-12" />
          </Link>
          {process.env.NEXT_PUBLIC_HIDE_ADMIN !== 'true' && (
            <Link
              href="/monitor"
              className="flex items-center gap-3 px-10 py-5 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-[2rem] font-bold text-lg transition-all backdrop-blur-xl"
            >
              <LayoutDashboard className="w-6 h-6 text-zinc-400" />
              查看管理中心
            </Link>
          )}
        </div>

        {/* Feature Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-24 border-t border-white/5">
          <div className="text-left space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center text-brand-primary">
              <Globe className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-white">在地化轉譯</h3>
            <p className="text-zinc-500 font-medium">整合 AI 指令系統，將複雜的英文策略自動轉化為精確的繁體中文解釋。</p>
          </div>
          
          <div className="text-left space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center text-blue-500">
              <Shield className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-white">獨立數據儲存</h3>
            <p className="text-zinc-500 font-medium">使用專屬高效能資料庫，確保您的策略數據與監控日誌安全且具備高可用性。</p>
          </div>

          <div className="text-left space-y-4">
            <div className="w-12 h-12 rounded-2xl bg-zinc-900 border border-white/5 flex items-center justify-center text-emerald-500">
              <ArrowRight className="w-6 h-6" />
            </div>
            <h3 className="text-xl font-black text-white">一鍵導引</h3>
            <p className="text-zinc-500 font-medium">直觀的用戶介面，讓您在海量 TradingView 腳本中快速找到具備價值的策略內容。</p>
          </div>
        </div>
      </div>
    </div>
  );
}
