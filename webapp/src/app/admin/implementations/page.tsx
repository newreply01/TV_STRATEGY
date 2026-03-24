export const revalidate = 0;
import React from 'react';
import { query } from '@/lib/db';
import { CheckCircle2, X, Clock, Folder, Database, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

async function getImplementationStatus() {
  const res = await query(`
    SELECT s.id, s.title, s.slug, s.category, i.serial_id, i.is_implemented, i.folder_path, i.implemented_at, i.notes
    FROM tradingview_scripts s
    LEFT JOIN script_implementations i ON s.slug = i.script_slug
    ORDER BY i.serial_id ASC NULLS LAST, s.last_synced_at DESC
  `);
  return res.rows;
}

export default async function ImplementationDashboard() {
  const data = await getImplementationStatus();
  
  return (
    <div className="min-h-screen bg-[#0a0a0b] text-zinc-100 font-sans p-8 md:p-12">
      <div className="max-w-7xl mx-auto space-y-12">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Link href="/scripts" className="flex items-center gap-2 text-zinc-500 hover:text-white transition-colors text-sm font-bold mb-4">
              <ArrowLeft className="w-4 h-4" /> 返回策略清單
            </Link>
            <h1 className="text-4xl font-black tracking-tight text-white flex items-center gap-4">
              <Database className="w-10 h-10 text-brand-primary" />
              策略實作追蹤面版
            </h1>
            <p className="text-zinc-500 font-medium">即時監控所有 TradingView 策略的自動化轉譯與開發進度</p>
          </div>
          
          <div className="flex gap-4">
            <div className="px-6 py-4 bg-zinc-900/50 rounded-2xl border border-white/5 backdrop-blur-xl text-center">
              <div className="text-2xl font-black text-white">{data.filter(d => d.is_implemented).length}</div>
              <div className="text-[10px] uppercase tracking-widest font-black text-zinc-600">已實作數量</div>
            </div>
            <div className="px-6 py-4 bg-zinc-900/50 rounded-2xl border border-white/5 backdrop-blur-xl text-center">
              <div className="text-2xl font-black text-white">{data.length}</div>
              <div className="text-[10px] uppercase tracking-widest font-black text-zinc-600">總策略庫存</div>
            </div>
          </div>
        </div>

        <div className="overflow-hidden rounded-[2.5rem] bg-zinc-900/30 border border-white/5 backdrop-blur-2xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-white/5">
                <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 border-b border-white/5">序號</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 border-b border-white/5">策略名稱</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 border-b border-white/5">類別</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 border-b border-white/5">狀態</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 border-b border-white/5">存放路徑</th>
                <th className="px-8 py-6 text-[10px] font-black uppercase tracking-[0.2em] text-zinc-500 border-b border-white/5">最後更新</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {data.map((item) => (
                <tr key={item.id} className="group hover:bg-white/[0.02] transition-colors">
                  <td className="px-8 py-6">
                    {item.serial_id ? (
                      <span className="px-3 py-1 rounded-full bg-white text-black text-xs font-black">#{item.serial_id}</span>
                    ) : (
                      <span className="text-zinc-700 font-mono text-xs">---</span>
                    )}
                  </td>
                  <td className="px-8 py-6">
                    <Link href={`/scripts/${item.slug}`} className="font-bold text-zinc-200 group-hover:text-brand-primary transition-colors">
                      {item.title}
                    </Link>
                  </td>
                  <td className="px-8 py-6 text-zinc-400 text-xs font-bold">
                    {item.category === 'Stock' ? '個股' : 
                     item.category === 'ETF' ? 'ETF' :
                     item.category === 'Futures' ? '期貨' :
                     item.category === 'Crypto' ? '加密幣' : '其他'}
                  </td>
                  <td className="px-8 py-6">
                    {item.is_implemented ? (
                      <div className="flex items-center gap-2 text-emerald-500 text-xs font-bold">
                        <CheckCircle2 className="w-4 h-4" /> 已完成
                      </div>
                    ) : (
                      <div className="flex items-center gap-2 text-zinc-600 text-xs font-bold">
                        <Clock className="w-4 h-4" /> 待實作
                      </div>
                    )}
                  </td>
                  <td className="px-8 py-6">
                    {item.folder_path ? (
                      <div className="flex items-center gap-2 text-zinc-400 font-mono text-[10px]">
                        <Folder className="w-3 h-3" /> {item.folder_path}
                      </div>
                    ) : (
                      <span className="text-zinc-800">N/A</span>
                    )}
                  </td>
                  <td className="px-8 py-6 text-zinc-500 text-xs font-medium">
                    {item.implemented_at ? new Date(item.implemented_at).toLocaleDateString('zh-TW') : '---'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
