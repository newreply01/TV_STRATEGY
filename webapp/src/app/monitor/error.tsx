'use client';

import { useEffect } from 'react';
import { AlertCircle, RefreshCcw, Home } from 'lucide-react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Monitor Page Error:', error);
  }, [error]);

  return (
    <div className="min-h-[calc(100vh-64px)] flex flex-col items-center justify-center p-6 bg-zinc-950 text-white">
      <div className="max-w-md w-full text-center space-y-8 animate-in fade-in zoom-in duration-300">
        {/* Icon */}
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-red-500/10 border border-red-500/20 text-red-500 mb-4">
          <AlertCircle className="w-10 h-10" />
        </div>

        {/* Text */}
        <div className="space-y-4">
          <h2 className="text-3xl font-black tracking-tight">監控中心載入失敗</h2>
          <p className="text-zinc-400 font-medium">
            抱歉，讀取系統狀態時發生了非預期錯誤。這可能是由於資料庫連線不穩定或系統結構正在更新中。
          </p>
          <div className="text-xs font-mono p-4 bg-white/5 border border-white/10 rounded-xl text-zinc-500 overflow-auto max-h-32 text-left">
            Error: {error.message || 'Unknown server-side exception'}
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <button
            onClick={() => reset()}
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 bg-brand-primary hover:bg-orange-500 text-white rounded-2xl font-bold transition-all hover:scale-105 active:scale-95"
          >
            <RefreshCcw className="w-5 h-5" />
            嘗試重新整理
          </button>
          
          <Link
            href="/"
            className="w-full sm:w-auto flex items-center justify-center gap-2 px-8 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white rounded-2xl font-bold transition-all"
          >
            <Home className="w-5 h-5" />
            回首頁
          </Link>
        </div>
      </div>
    </div>
  );
}
