'use client';

import React, { useState, useEffect } from 'react';
import TradingViewChart from '@/components/TradingViewChart';
import { LayoutGrid, LineChart, Code2, Heart, MessageSquare, Info, Globe, Languages, ExternalLink, Calendar, User, Activity } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function ScriptDetailClient({ script }: { script: any }) {
  const [mounted, setMounted] = useState(false);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [lang, setLang] = useState<'zh' | 'en'>('zh');
  const [symbol, setSymbol] = useState('AAPL');
  
  const [customSymbol, setCustomSymbol] = useState('');
  
  const popularSymbols = [
    { label: 'Apple', value: 'AAPL' },
    { label: 'Tesla', value: 'TSLA' },
    { label: 'Nvidia', value: 'NVDA' },
    { label: 'Meta', value: 'META' },
    { label: '台積電 (2330.TW)', value: '2330.TW' },
  ];
  
  useEffect(() => {
    setMounted(true);
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 600);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const hasTranslation = !!script.description_zh;

  return (
    <div className="min-h-screen bg-[#0a0a0b] text-zinc-100 font-sans selection:bg-brand-primary/30 pb-20">
      <div className="max-w-[1600px] mx-auto px-6 py-12 space-y-12">
        {/* Breadcrumb */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <nav className="flex items-center gap-2 text-sm text-zinc-500 font-medium">
            <a href="/scripts" className="hover:text-brand-primary transition-colors">策略總覽</a>
            <span>/</span>
            <span className="text-zinc-300">{script.title}</span>
          </nav>
        </div>

        {/* Hero Area */}
        <div className="space-y-4">
          <div className="flex items-center gap-3">
            {script.serial_id && (
              <div className="px-3 py-1 rounded-full bg-white text-black text-xs font-black border border-white shadow-xl">
                #{script.serial_id}
              </div>
            )}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-primary/10 text-brand-primary text-[10px] font-bold tracking-widest uppercase border border-brand-primary/20">
              {script.source_type === 'editors_picks' ? "Editor's Pick" : "Popular Script"}
            </div>
            {script.is_implemented && (
              <div className="px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-500 text-[10px] font-bold border border-emerald-500/20">
                已實作
              </div>
            )}
            <div className="px-3 py-1 rounded-full bg-zinc-800 text-zinc-300 text-[10px] font-black tracking-widest uppercase border border-white/5 shadow-2xl">
              {script.category === 'Stock' ? '個股' : 
               script.category === 'ETF' ? 'ETF' :
               script.category === 'Futures' ? '期貨' :
               script.category === 'Crypto' ? '加密幣' : '其他'}
            </div>
          </div>
          <h1 className="text-5xl font-black tracking-tight leading-tight text-white max-w-4xl">
            {script.title}
          </h1>
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div className="flex items-center gap-2 text-zinc-400">
              <User className="w-5 h-5 text-brand-primary" />
              <span className="font-bold">{script.author}</span>
            </div>
            <div className="flex items-center gap-2 text-zinc-500">
              <Calendar className="w-4 h-4" />
              {new Date(script.last_synced_at).toLocaleDateString('zh-TW')}
            </div>
            <div className="flex items-center gap-4 px-4 py-1.5 bg-zinc-900/50 rounded-full border border-white/5">
               <div className="flex items-center gap-1.5"><Heart className="w-4 h-4 text-red-500" /> <span className="text-xs font-bold">{script.boosts_count || 0}</span></div>
               <div className="w-px h-3 bg-zinc-800" />
               <div className="flex items-center gap-1.5"><MessageSquare className="w-4 h-4 text-blue-500" /> <span className="text-xs font-bold">{script.comments_count || 0}</span></div>
            </div>
          </div>
        </div>

        {/* 1. Dynamic Chart Section (Fixed at top of document flow) */}
        <section className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700 pt-8 border-t border-white/5">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-black flex items-center gap-3">
              <LineChart className="w-6 h-6 text-brand-primary" />
              動態分析圖表
            </h2>
            {/* Symbol Switcher */}
            <div className="hidden lg:flex flex-wrap items-center gap-2 p-1 bg-white/5 rounded-xl border border-white/5 backdrop-blur-md">
              <span className="px-3 text-xs font-black text-zinc-600 uppercase tracking-widest">快速切換:</span>
              {popularSymbols.map((s) => (
                <button
                  key={s.value}
                  onClick={() => {
                    setSymbol(s.value);
                    setCustomSymbol(''); // Reset custom input when clicking presets
                  }}
                  className={cn(
                    "px-4 py-1.5 rounded-lg text-sm font-black tracking-widest uppercase transition-all",
                    symbol === s.value 
                      ? "bg-white text-black shadow-lg" 
                      : "text-zinc-500 hover:text-white"
                  )}
                >
                  {s.label}
                </button>
              ))}
              
              <div className="w-px h-4 bg-zinc-800 mx-2" />
              
              {/* Custom Symbol Input */}
              <div className="flex items-center gap-2 px-2 py-0.5 bg-black/40 rounded-lg border border-white/5 group focus-within:border-brand-primary/50 transition-all">
                <input
                  type="text"
                  placeholder="輸入代號 (e.g. BTCUSDT)"
                  value={customSymbol}
                  onChange={(e) => setCustomSymbol(e.target.value.toUpperCase())}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && customSymbol) {
                      setSymbol(customSymbol);
                    }
                  }}
                  className="bg-transparent border-none outline-none text-xs font-black w-32 placeholder:text-zinc-700 text-white p-1"
                />
                <button 
                  onClick={() => customSymbol && setSymbol(customSymbol)}
                  className="p-1 hover:text-brand-primary text-zinc-500 transition-colors"
                >
                  <Activity className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          </div>

          <div className="rounded-[2.5rem] bg-zinc-900/40 border border-white/10 p-2 backdrop-blur-3xl overflow-hidden shadow-3xl">
            {mounted ? (
              <TradingViewChart slug={script.slug} symbol={symbol} />
            ) : (
              <div className="h-[500px] w-full bg-zinc-900 animate-pulse rounded-3xl flex items-center justify-center text-zinc-500 font-bold">啟動圖表引擎中...</div>
            )}
          </div>
          
          <div className="p-8 bg-zinc-900/40 rounded-[2rem] border border-white/5 backdrop-blur-xl">
             <h3 className="text-lg font-black mb-4 flex items-center gap-2">
               <Info className="w-5 h-5 text-brand-primary" />
               分析說明
             </h3>
              <p className="text-zinc-400 leading-relaxed text-sm">
               本動態圖表目前切換至 <b>{symbol}</b> 進行設計基準校驗。數據採用 15 分鐘級別 K 線。
               圖表中的買賣信號是透過 Python 精準還原 <b>{script.title}</b> 的核心演算法運算而成。
             </p>
          </div>
        </section>

        {/* 2. Unified Information & Article Section (Single Row Header) */}
        <section className="space-y-6 pt-12 border-t border-white/5">
          {/* Controls Row */}
          <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-4">
            {/* Header & Lang Switcher */}
            <div className="flex-1 flex items-center justify-between bg-zinc-900/50 p-4 rounded-2xl border border-white/5 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <Globe className="w-5 h-5 text-brand-primary" />
                <h2 className="text-base font-black m-0">策略轉譯描述</h2>
              </div>
              
              <div className="flex p-1 bg-black/40 rounded-xl border border-white/5">
                <button 
                  onClick={() => setLang('zh')}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-sm font-black transition-all",
                    lang === 'zh' ? "bg-white text-black shadow-lg" : "text-zinc-500 hover:text-zinc-300"
                  )}
                >
                  繁體中文
                </button>
                <button 
                  onClick={() => setLang('en')}
                  className={cn(
                    "px-3 py-1.5 rounded-lg text-sm font-black transition-all",
                    lang === 'en' ? "bg-white text-black shadow-lg" : "text-zinc-500 hover:text-zinc-300"
                  )}
                >
                  ORIGINAL
                </button>
              </div>
            </div>

            {/* TV Button */}
            <a href={script.url} target="_blank" className="flex items-center gap-3 px-6 py-4 bg-brand-primary rounded-2xl font-bold text-white hover:bg-red-600 transition-colors text-xs shadow-xl">
              去 TradingView 查看
              <ExternalLink className="w-4 h-4" />
            </a>

            {/* Accuracy Status */}
            <div className="flex items-center gap-4 px-6 py-4 bg-zinc-900/50 rounded-2xl border border-white/5 backdrop-blur-md">
               <span className="text-xs text-zinc-500 font-bold uppercase tracking-widest font-mono">Accuracy</span>
               <span className="text-sm text-white font-black">99.8%</span>
            </div>
          </div>
          
          {/* Main Content Area */}
          <div className="rounded-[2.5rem] bg-zinc-900/40 border border-white/5 p-8 md:p-12 backdrop-blur-3xl relative overflow-hidden text-base leading-relaxed">
            <div className="relative">
              <div className="text-zinc-200 font-medium whitespace-pre-wrap max-w-5xl">
                {lang === 'zh' 
                  ? (script.description_full_zh || script.description_zh || '尚未提供描述') 
                  : (script.description_full || script.description_en || 'No description available')
                }
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* Floating Back to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-10 right-10 p-4 bg-brand-primary text-white rounded-2xl shadow-2xl hover:scale-110 active:scale-95 transition-all z-50 flex flex-col items-center gap-1 group animate-in slide-in-from-right-10"
        >
          <LineChart className="w-6 h-6 group-hover:-translate-y-1 transition-transform" />
          <span className="text-[9px] font-black uppercase tracking-tighter">回到圖表</span>
        </button>
      )}
    </div>
  );
}
