'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Database, Filter, Search } from 'lucide-react';

const CATEGORY_MAP: Record<string, string> = {
  'Stock': '個股',
  'ETF': 'ETF',
  'Futures': '期貨',
  'Warrant': '權證',
  'Crypto': '加密幣',
  'Other': '其他'
};

const CATEGORIES = ['All', 'Stock', 'ETF', 'Futures', 'Warrant', 'Other'];

export default function ScriptsListClient({ initialScripts }: { initialScripts: any[] }) {
  const [filter, setFilter] = useState('All');
  const [search, setSearch] = useState('');
  const [mounted, setMounted] = React.useState(false);

  // Helper to extract TradingView snapshot URL from slug
  const getTradingViewSnapshot = (slug: string, imageUrl: string) => {
    if (!imageUrl) return "";
    
    if (imageUrl.startsWith('http') || imageUrl.startsWith('/')) return imageUrl;
    
    const id = imageUrl.length >= 5 ? imageUrl : slug.split('-')[0];
    const firstLetter = id.charAt(0).toLowerCase();
    
    // Verified 200 OK: s3.tradingview.com/{first_char}/{id}.png
    return `https://s3.tradingview.com/${firstLetter}/${id}.png`;
  };

  React.useEffect(() => {
    setMounted(true);
  }, []);

  const filteredScripts = initialScripts.filter(s => {
    const matchesCategory = filter === 'All' || s.category === filter;
    const matchesSearch = s.title.toLowerCase().includes(search.toLowerCase()) || 
                          (s.description_zh && s.description_zh.toLowerCase().includes(search.toLowerCase()));
    
    return matchesCategory && matchesSearch;
  });

  if (!mounted) {
    return (
      <div className="min-h-screen bg-white dark:bg-[#0a0a0b] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-white dark:bg-black text-black dark:text-white p-8">
      <header className="max-w-7xl mx-auto mb-12 flex flex-col lg:flex-row lg:items-end justify-between gap-8">
        <div className="space-y-4">
          <div className="flex items-center gap-3">
             <div className="w-10 h-10 rounded-2xl bg-brand-primary/10 flex items-center justify-center border border-brand-primary/20">
               <Database className="w-5 h-5 text-brand-primary" />
             </div>
             <h1 className="text-4xl font-black tracking-tight bg-gradient-to-r from-zinc-900 to-zinc-500 dark:from-white dark:to-zinc-500 bg-clip-text text-transparent">
                策略中心
             </h1>
          </div>
          <p className="text-zinc-500 max-w-2xl font-medium">
             為您精選 TradingView 頂尖指標，呈現已驗收完畢、具備 Python 引擎重現能力的專業級分析。
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-4">
           {/* Search */}
           <div className="relative group">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500 group-focus-within:text-brand-primary transition-colors" />
              <input 
                type="text" 
                placeholder="搜尋策略名稱..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-11 pr-6 py-3 bg-zinc-100 dark:bg-zinc-900 border border-zinc-200 dark:border-white/5 rounded-2xl text-sm focus:outline-none focus:border-brand-primary/50 w-full sm:w-64 transition-all"
              />
           </div>
           
           <Link href="/monitor" className="flex items-center gap-2 px-6 py-3 rounded-2xl bg-zinc-900 text-white border border-white/10 hover:bg-zinc-800 transition-all text-sm font-bold">
             進入管理中心
           </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-12">
        <div className="flex flex-col gap-6">
          {/* Category Filters */}
          <div className="flex items-center justify-between">
            <div className="flex flex-wrap items-center gap-3">
               <div className="flex items-center gap-2 text-zinc-500 mr-2 border-r border-zinc-200 dark:border-white/10 pr-4">
                  <Filter className="w-4 h-4" />
                  <span className="text-[10px] font-black uppercase tracking-widest">類別篩選</span>
               </div>
               {CATEGORIES.map((cat) => (
                 <button
                   key={cat}
                   onClick={() => setFilter(cat)}
                   className={`px-6 py-2 rounded-full text-xs font-black tracking-widest uppercase transition-all border ${
                     filter === cat 
                       ? "bg-brand-primary text-white border-brand-primary shadow-lg shadow-brand-primary/20" 
                       : "bg-white dark:bg-zinc-900 text-zinc-500 border-zinc-200 dark:border-white/5 hover:border-zinc-400 dark:hover:border-white/20"
                   }`}
                 >
                   {cat === 'All' ? '全部' : (CATEGORY_MAP[cat] || cat)}
                 </button>
               ))}
            </div>

            <span className="text-xs font-black text-zinc-400 uppercase tracking-widest">
               找到 {filteredScripts.length} 個結果
            </span>
          </div>
        </div>

        {/* Grid Area */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {filteredScripts.map((script: any) => (
            <Link 
              key={script.slug} 
              href={`/scripts/${script.slug}`}
              className="group block rounded-[2.5rem] border border-gray-200 dark:border-white/5 bg-white dark:bg-zinc-900/40 overflow-hidden hover:border-brand-primary transition-all duration-500 hover:shadow-[0_20px_50px_-15px_rgba(255,59,48,0.15)]"
            >
              <div className="aspect-[16/10] bg-gray-100 dark:bg-zinc-900 overflow-hidden relative">
                {script.imageUrl ? (
                  <img 
                    src={getTradingViewSnapshot(script.slug, script.imageUrl)} 
                    alt={script.title}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-gray-400">No Preview</div>
                )}
                
                {/* Overlay Tags */}
                <div className="absolute top-6 right-6 flex flex-col items-end gap-2">
                  {script.serial_id && (
                    <span className="px-3 py-1 rounded-full text-[10px] font-black bg-white/90 text-black border border-white shadow-xl">
                      #{script.serial_id}
                    </span>
                  )}
                  <span className={`px-3 py-1 rounded-full text-[10px] font-black backdrop-blur-md uppercase tracking-wider ${
                    script.source_type === 'editors_picks' 
                      ? 'bg-amber-500 text-white' 
                      : 'bg-blue-500 text-white'
                  }`}>
                    {script.source_type === 'editors_picks' ? '編輯精選' : '熱門'}
                  </span>
                </div>

                {/* Category Floating Tag */}
                <div className="absolute bottom-6 left-6">
                   <span className="px-4 py-1.5 rounded-full text-[10px] font-black bg-black/60 text-white backdrop-blur-xl border border-white/20 uppercase tracking-widest shadow-2xl">
                      {CATEGORY_MAP[script.category] || '個股'}
                   </span>
                </div>
              </div>
              
              <div className="p-8 space-y-6">
                <div className="space-y-2">
                  <div className="flex items-center gap-3">
                    <h2 className="text-xl font-bold line-clamp-1 group-hover:text-brand-primary transition-colors">
                      {script.title}
                    </h2>
                    {script.is_implemented && (
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500 text-white text-[9px] font-black uppercase tracking-widest shadow-lg shadow-emerald-500/20">
                        已實作
                      </span>
                    )}
                    {script.is_web_done && (
                      <span className="px-2 py-0.5 rounded-full bg-blue-500 text-white text-[9px] font-black uppercase tracking-widest shadow-lg shadow-blue-500/20">
                        已完成
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-5 h-5 rounded-full bg-zinc-200 dark:bg-zinc-800 flex items-center justify-center text-[9px] font-black uppercase">
                      {(script.author || 'U')[0]}
                    </div>
                    <span className="text-xs text-zinc-500 font-bold">{script.author || 'Unknown'}</span>
                  </div>
                </div>

                <p className="text-sm text-zinc-500 dark:text-zinc-500 line-clamp-3 leading-relaxed font-medium">
                  {script.descriptionZh || script.descriptionEn || '尚未提供描述'}
                </p>

                {/* Datasets Info */}
                <div className="flex flex-wrap gap-2">
                   <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-zinc-100 dark:bg-zinc-800 border border-zinc-200 dark:border-white/5 text-[10px] font-bold text-zinc-500 dark:text-zinc-400">
                      <Database className="w-3 h-3" />
                      <span>所需資料集: {script.datasets || 'OHLC, Volume'}</span>
                   </div>
                </div>

                <div className="flex items-center justify-between pt-6 border-t border-gray-100 dark:border-white/5">
                  <span className="text-[10px] text-zinc-400 font-black uppercase tracking-widest">
                    {new Date(script.updatedAt || new Date()).toLocaleDateString('zh-TW')}
                  </span>
                  <span className="text-brand-primary text-xs font-black uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0">
                    分析細節 →
                  </span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </main>
    </div>
  );
}
