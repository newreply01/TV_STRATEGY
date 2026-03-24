'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Activity, Database, Server, RefreshCw, AlertCircle, Calendar, Sun, Moon, ExternalLink, Link as LinkIcon, Check, List, Search, ChevronUp, ChevronDown, X, ArrowDownUp } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

type ToastType = 'success' | 'error';
interface Toast { id: number; message: string; type: ToastType; }

export default function MonitorPageClient() {
    const [statusData, setStatusData] = useState<any>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [darkMode, setDarkMode] = useState<boolean>(true);
    const [activeTab, setActiveTab] = useState<'infrastructure' | 'development'>('development');
    const [mounted, setMounted] = useState(false);
    const [togglingId, setTogglingId] = useState<string | null>(null);
    const [promotingId, setPromotingId] = useState<string | null>(null);
    const [demotingId, setDemotingId] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState<string>('');
    const [statusFilter, setStatusFilter] = useState<'all' | 'pending' | 'implemented' | 'done'>('all');
    const [sortField, setSortField] = useState<'serialId' | 'likesCount' | 'status'>('serialId');
    const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');
    const [visibleBacklogCount, setVisibleBacklogCount] = useState<number>(10);
    const [toasts, setToasts] = useState<Toast[]>([]);
    const addToast = useCallback((message: string, type: ToastType = 'success') => {
        const id = Date.now();
        setToasts(prev => [...prev, { id, message, type }]);
        setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 3000);
    }, []);

    const fetchData = async () => {

        setLoading(true);
        setError(null);
        try {
            const statusRes = await fetch('/api/monitor');
            const statusJson = await statusRes.json();

            if (statusJson.success) {
                setStatusData(statusJson);
            } else {
                throw new Error(statusJson.error || 'Failed to fetch status');
            }
        } catch (err: any) {
            console.error('Error fetching monitor data:', err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleStatus = async (id: string, currentStatus: boolean, type: 'web' | 'script' | 'implemented' = 'implemented') => {
        setTogglingId(`${id}-${type}`);
        try {
            const res = await fetch('/api/monitor/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id, isImplemented: !currentStatus, type }),
            });
            if (res.ok) {
                addToast(currentStatus ? '狀態已取消' : '狀態已更新 ✓');
                await fetchData();
            } else {
                addToast('狀態更新失敗', 'error');
            }
        } catch (err) {
            addToast('網路錯誤，請稍後再試', 'error');
        } finally {
            setTogglingId(null);
        }
    };

    const handlePromote = async (slug: string) => {
        setPromotingId(slug);
        try {
            const res = await fetch('/api/monitor/promote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slug }),
            });
            if (res.ok) {
                const data = await res.json();
                addToast(`已排入開發！序號: ${data.newSerialId} ✓`);
                await fetchData();
            } else {
                const data = await res.json();
                addToast(data.error || '排入失敗', 'error');
            }
        } catch (err) {
            addToast('網路錯誤，請稍後再試', 'error');
        } finally {
            setPromotingId(null);
        }
    };

    const handleDemote = async (slug: string, title: string) => {
        if (!confirm(`確定要將「${title}」移回收容池？
這個操作將清除序號與雙開關狀態。`)) return;
        setDemotingId(slug);
        try {
            const res = await fetch('/api/monitor/demote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ slug }),
            });
            if (res.ok) {
                addToast(`已移回收容池`);
                await fetchData();
            } else {
                const data = await res.json();
                addToast(data.error || '操作失敗', 'error');
            }
        } catch (err) {
            addToast('網路錯誤，請稍後再試', 'error');
        } finally {
            setDemotingId(null);
        }
    };

    const handleSort = (field: 'serialId' | 'likesCount' | 'status') => {
        if (sortField === field) {
            setSortDir(d => d === 'asc' ? 'desc' : 'asc');
        } else {
            setSortField(field);
            setSortDir('asc');
        }
    };

    useEffect(() => {
        setMounted(true);
        const saved = localStorage.getItem('tradeview-darkmode');
        if (saved !== null) setDarkMode(saved === 'true');
        fetchData();
        const interval = setInterval(fetchData, 5 * 60 * 1000);
        return () => clearInterval(interval);
    }, []);

    const toggleDarkMode = () => {
        setDarkMode(prev => {
            const next = !prev;
            localStorage.setItem('tradeview-darkmode', String(next));
            return next;
        });
    };

    if (!mounted) {
        return (
            <div className="min-h-screen bg-[#0a0a0b] flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-primary"></div>
            </div>
        );
    }

    const StatusBadge = ({ status }: { status: string }) => {
        const isUp = status === 'UP';
        return (
            <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${isUp ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
                <span className={`w-1.5 h-1.5 rounded-full ${isUp ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
                {isUp ? '正常運作' : '服務異常'}
            </span>
        );
    };

    return (
        <div suppressHydrationWarning className={`min-h-screen transition-colors duration-500 font-sans selection:bg-brand-primary/30 ${darkMode ? 'bg-[#0a0a0b] text-zinc-100' : 'bg-zinc-50 text-zinc-900'}`}>
            {/* Toast 面板 */}
            <div className="fixed top-6 right-6 z-50 flex flex-col gap-2 pointer-events-none">
                {toasts.map(t => (
                    <div key={t.id} className={`flex items-center gap-3 px-4 py-3 rounded-2xl text-sm font-bold shadow-2xl border animate-in slide-in-from-right-4 duration-300 ${t.type === 'success' ? 'bg-emerald-900/90 border-emerald-500/30 text-emerald-200' : 'bg-red-900/90 border-red-500/30 text-red-200'}`}>
                        {t.type === 'success' ? <Check className="w-4 h-4 shrink-0" /> : <AlertCircle className="w-4 h-4 shrink-0" />}
                        {t.message}
                    </div>
                ))}
            </div>

            <div className="max-w-7xl mx-auto p-6 sm:p-10 space-y-8">
                {/* Header section */}
                <div className={`flex flex-col sm:flex-row justify-between items-start sm:items-center gap-6 backdrop-blur-xl p-8 rounded-[2rem] border transition-all duration-500 shadow-2xl ${darkMode ? 'bg-zinc-900/40 border-white/5' : 'bg-white/80 border-zinc-200'}`}>
                    <div className="space-y-2">
                        <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-bold tracking-wider uppercase border ${darkMode ? 'bg-brand-primary/10 text-brand-primary border-brand-primary/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/20'}`}>
                            Live Operations
                        </div>
                        <h1 className="text-4xl font-black tracking-tight flex items-center gap-3">
                            <Activity className="w-8 h-8 text-brand-primary" />
                            系統管理中心
                        </h1>
                        <p className={`${darkMode ? 'text-zinc-400' : 'text-zinc-500'} max-w-lg font-medium`}>
                            即時監控 TradeView Strategy 的開發進度、資料來源與系統穩定性。
                        </p>
                    </div>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={toggleDarkMode}
                            className={`p-3 rounded-2xl border transition-all duration-300 hover:scale-110 active:scale-95 ${darkMode ? 'bg-zinc-800 border-white/10 text-yellow-400 hover:bg-zinc-700' : 'bg-white border-zinc-200 text-indigo-600 hover:bg-zinc-100 shadow-lg'}`}
                        >
                            {darkMode ? <Sun className="w-6 h-6" /> : <Moon className="w-6 h-6" />}
                        </button>
                        <button
                            onClick={fetchData}
                            disabled={loading}
                            className="group relative flex items-center gap-2 px-6 py-3 bg-brand-primary hover:bg-red-600 text-white rounded-2xl font-bold transition-all hover:scale-105 active:scale-95 disabled:opacity-50 shadow-lg shadow-brand-primary/20"
                        >
                            <RefreshCw className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`} />
                            <span>重新整理</span>
                        </button>
                    </div>
                </div>

                {/* Tab Switcher */}
                <div className="flex p-1.5 bg-zinc-900/20 backdrop-blur-xl rounded-2xl border border-white/5 max-w-md">
                    <button
                        onClick={() => setActiveTab('development')}
                        className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-black transition-all ${activeTab === 'development' ? 'bg-brand-primary text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        <Calendar className="w-4 h-4" />
                        開發進度
                    </button>
                    <button
                        onClick={() => setActiveTab('infrastructure')}
                        className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl text-sm font-black transition-all ${activeTab === 'infrastructure' ? 'bg-emerald-500 text-white shadow-lg' : 'text-zinc-500 hover:text-zinc-300'}`}
                    >
                        <Server className="w-4 h-4" />
                        系統監控
                    </button>
                </div>

                {error && (
                    <div className="bg-red-500/10 border border-red-500/20 backdrop-blur-md rounded-2xl p-6 flex items-start gap-4 text-red-400">
                        <AlertCircle className="w-6 h-6" />
                        <p>{error}</p>
                    </div>
                )}

                {activeTab === 'infrastructure' && statusData && (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                            <div className={`group backdrop-blur-xl p-8 rounded-[2rem] border transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5 hover:border-brand-primary/30' : 'bg-white border-zinc-200'}`}>
                                <div className="flex justify-between items-start mb-6">
                                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border transition-colors ${darkMode ? 'bg-blue-500/10 text-blue-400 border-blue-500/20 group-hover:bg-blue-500 group-hover:text-white' : 'bg-blue-50 text-blue-600 border-blue-100 group-hover:bg-blue-600 group-hover:text-white'}`}>
                                        <Database className="w-7 h-7" />
                                    </div>
                                    <StatusBadge status={statusData.status.database} />
                                </div>
                                <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500 mb-1">主資料庫</h3>
                                <p className="text-2xl font-black">PostgreSQL 16</p>
                            </div>

                            <div className={`group backdrop-blur-xl p-8 rounded-[2rem] border transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5 hover:border-brand-primary/30' : 'bg-white border-zinc-200 shadow-xl'}`}>
                                <div className="flex justify-between items-start mb-6">
                                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border transition-colors ${darkMode ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20 group-hover:bg-indigo-500 group-hover:text-white' : 'bg-indigo-50 text-indigo-600 border-indigo-100 group-hover:bg-indigo-600 group-hover:text-white'}`}>
                                        <Server className="w-7 h-7" />
                                    </div>
                                    <StatusBadge status={statusData.status.backend} />
                                </div>
                                <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500 mb-1">後端 API</h3>
                                <p className="text-2xl font-black">Next.js 14 API</p>
                            </div>

                            <div className={`group backdrop-blur-xl p-8 rounded-[2rem] border transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5 hover:border-brand-primary/30' : 'bg-white border-zinc-200'}`}>
                                <div className="flex justify-between items-start mb-6">
                                    <div className={`w-14 h-14 rounded-2xl flex items-center justify-center border transition-colors ${darkMode ? 'bg-brand-primary/10 text-brand-primary border-brand-primary/20 group-hover:bg-brand-primary group-hover:text-white' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/10 group-hover:bg-brand-primary group-hover:text-white'}`}>
                                        <Activity className="w-7 h-7" />
                                    </div>
                                    <StatusBadge status={statusData.status.scheduler} />
                                </div>
                                <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500 mb-1">任務排程器</h3>
                                <p className="text-2xl font-black">Centrifuge Core</p>
                            </div>
                        </div>

                        {/* 系統核心數據同步狀態 */}
                        <div className={`mt-8 backdrop-blur-xl rounded-[2.5rem] border shadow-2xl overflow-hidden transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5' : 'bg-white border-zinc-200 shadow-xl'}`}>
                            <div className={`p-8 border-b flex items-center justify-between ${darkMode ? 'border-white/5' : 'border-zinc-100'}`}>
                                <div className="flex items-center gap-3">
                                    <div className={`p-3 rounded-2xl border ${darkMode ? 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20' : 'bg-indigo-50 text-indigo-600 border-indigo-100 shadow-lg'}`}>
                                        <RefreshCw className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-black">系統基礎數據同步</h2>
                                        <p className="text-xs font-medium opacity-60">全系統層級的數據採集與盤點</p>
                                    </div>
                                </div>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead className={`text-[10px] font-black uppercase tracking-[0.2em] ${darkMode ? 'bg-zinc-950/50 text-zinc-500' : 'bg-zinc-50 text-zinc-400'}`}>
                                        <tr>
                                            <th className="px-8 py-5">數據項目</th>
                                            <th className="px-8 py-5">盤點說明</th>
                                            <th className="px-8 py-5">維護指令</th>
                                            <th className="px-8 py-5 text-right">狀態</th>
                                        </tr>
                                    </thead>
                                    <tbody className={`divide-y ${darkMode ? 'divide-white/5' : 'divide-zinc-100'}`}>
                                        {statusData?.sync_progress?.filter((item: any) => item.id === 'TradingView_Scripts').map((item: any, idx: number) => (
                                            <tr key={idx} className={`group transition-colors ${darkMode ? 'hover:bg-white/[0.02]' : 'hover:bg-zinc-50/50'}`}>
                                                <td className="px-8 py-6">
                                                    <div className={`font-bold text-base ${darkMode ? 'text-white' : 'text-zinc-900'}`}>{item.dataset}</div>
                                                    <div className="text-[10px] font-normal mt-1 uppercase tracking-wider opacity-60">{item.usage}</div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="text-sm font-medium">{item.inventory_desc}</div>
                                                    <div className="text-[10px] mt-1 opacity-60">{item.description}</div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="text-sm font-bold">{item.provider}</div>
                                                    <div className="text-[10px] opacity-60 font-mono">{item.script}</div>
                                                </td>
                                                <td className="px-8 py-6 text-right">
                                                    <span className="inline-flex items-center px-4 py-1.5 rounded-xl text-[11px] font-black bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
                                                        AVAILABLE
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </>
                )}

                {activeTab === 'development' && statusData && (
                    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
                        {/* Replicated Summary List */}
                        <div className={`mb-8 p-6 rounded-3xl border ${darkMode ? 'bg-emerald-500/5 border-emerald-500/10' : 'bg-emerald-50 border-emerald-100'}`}>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-10 h-10 rounded-2xl bg-emerald-500 flex items-center justify-center text-white shadow-lg shadow-emerald-500/20">
                                    <List className="w-5 h-5" />
                                </div>
                                <div>
                                    <h3 className="text-lg font-black tracking-tight">已復刻策略清單</h3>
                                    <p className="text-xs opacity-60">目前系統已完成 UI 與代碼實作的策略</p>
                                </div>
                            </div>
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                                {(statusData?.sync_progress || [])
                                    .filter((item: any) => item.is_implemented)
                                    .map((item: any) => (
                                        <div key={item.id} className={`flex items-center justify-between p-3 rounded-xl border transition-all ${darkMode ? 'bg-white/5 border-white/5' : 'bg-white border-zinc-100 shadow-sm'}`}>
                                            <div className="flex items-center gap-2">
                                                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                                                <span className="text-sm font-bold">{item.dataset}</span>
                                            </div>
                                            <a
                                                href={item.target_url}
                                                className="text-[10px] font-black text-brand-primary hover:underline"
                                            >
                                                進入研發頁
                                            </a>
                                        </div>
                                    ))}
                                {!(statusData?.sync_progress || []).some((i: any) => i.is_implemented) && (
                                    <div className="col-span-full py-4 text-center text-sm opacity-40 italic">暫無已復刻策略</div>
                                )}
                            </div>
                        </div>

                        {/* Stats Dashboard */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <div className={`backdrop-blur-xl p-8 rounded-[2rem] border overflow-hidden relative group transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5' : 'bg-white border-zinc-200 shadow-xl'}`}>
                                <div className="absolute top-0 right-0 p-8 opacity-10 group-hover:scale-110 transition-transform">
                                    <Calendar className="w-24 h-24" />
                                </div>
                                <div className="relative z-10">
                                    <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500 mb-4">策略總量規模</h3>
                                    <div className="flex items-end gap-3">
                                        <span className={`text-6xl font-black ${darkMode ? 'text-white' : 'text-zinc-900'}`}>{statusData?.stats?.total_articles || 0}</span>
                                        <span className="text-lg font-bold text-zinc-500 mb-2">篇</span>
                                    </div>
                                    <div className="mt-8 flex gap-4">
                                        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/20">
                                            <div className="text-[10px] font-black uppercase text-emerald-500 tracking-tighter mb-1">已實作</div>
                                            <div className="text-xl font-black text-emerald-500">{statusData?.stats?.implemented || 0}</div>
                                        </div>
                                        <div className="p-4 rounded-2xl bg-brand-primary/10 border border-brand-primary/20">
                                            <div className="text-[10px] font-black uppercase text-brand-primary tracking-tighter mb-1">待開發</div>
                                            <div className="text-xl font-black text-brand-primary">{statusData?.stats?.pending || 0}</div>
                                        </div>
                                    </div>

                                    {/* 進度條 */}
                                    <div className="mt-8 pt-6 border-t border-white/5 space-y-4">
                                        <div className="flex justify-between items-center text-xs font-bold">
                                            <span className="text-zinc-500 uppercase tracking-widest">開發完成率</span>
                                            <span className="text-emerald-500">
                                                {statusData?.stats?.implemented || 0} / {(statusData?.stats?.implemented || 0) + (statusData?.stats?.pending || 0)} 
                                                ({(() => {
                                                    const total = (statusData?.stats?.implemented || 0) + (statusData?.stats?.pending || 0);
                                                    return total === 0 ? 0 : Math.round(((statusData?.stats?.implemented || 0) / total) * 100);
                                                })()}%)
                                            </span>
                                        </div>
                                        <div className="h-2 w-full bg-zinc-800 rounded-full overflow-hidden">
                                            <div 
                                                className="h-full bg-emerald-500 transition-all duration-1000"
                                                style={{ width: `${(() => {
                                                    const total = (statusData?.stats?.implemented || 0) + (statusData?.stats?.pending || 0);
                                                    return total === 0 ? 0 : Math.round(((statusData?.stats?.implemented || 0) / total) * 100);
                                                })()}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className={`lg:col-span-2 backdrop-blur-xl p-8 rounded-[2rem] border relative group transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5' : 'bg-white border-zinc-200 shadow-xl'}`}>
                                <div className="flex items-center justify-between mb-6">
                                    <div>
                                        <h3 className="text-sm font-bold uppercase tracking-widest text-zinc-500">待開發收容池 (按讚數排名)</h3>
                                        <p className="text-xs text-zinc-500 mt-1">TradingView 社群熱度最高且「尚未排定開發序號」的指標庫存</p>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    {(statusData?.stats?.priority_list || []).slice(0, visibleBacklogCount).map((item: any, i: number) => (
                                        <div 
                                            key={i} 
                                            className={`flex flex-col sm:flex-row items-start sm:items-center justify-between p-3 rounded-xl border transition-all ${darkMode ? 'bg-white/5 border-white/5 hover:bg-white/10 hover:border-brand-primary/30' : 'bg-zinc-50 border-zinc-100 hover:bg-zinc-100 hover:border-brand-primary/30 shadow-sm'}`}
                                        >
                                            <div className="flex items-center gap-3 w-full sm:w-auto mb-2 sm:mb-0">
                                                <div className={`shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-black ${i === 0 ? 'bg-yellow-500 text-black' : i === 1 ? 'bg-zinc-400 text-black' : 'bg-zinc-600 text-white'}`}>
                                                    {i + 1}
                                                </div>
                                                <a href={item.url} target="_blank" rel="noopener noreferrer" className="text-sm font-bold truncate max-w-[200px] sm:max-w-xs hover:underline">
                                                    {item.title}
                                                </a>
                                            </div>
                                            <div className="flex items-center gap-3 shrink-0">
                                                <div className="flex items-center gap-1.5 text-brand-primary font-black text-xs min-w-[60px]">
                                                    <ExternalLink className="w-3 h-3" />
                                                    {(item.likes || 0).toLocaleString()}
                                                </div>
                                                <button
                                                    onClick={() => handlePromote(item.slug)}
                                                    disabled={promotingId === item.slug}
                                                    className={`px-3 py-1.5 text-xs font-black rounded-lg transition-all flex items-center gap-1.5 ${promotingId === item.slug ? 'bg-zinc-500 opacity-50 cursor-not-allowed text-white' : 'bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500 hover:text-white border border-emerald-500/20'}`}
                                                >
                                                    {promotingId === item.slug ? (
                                                        <RefreshCw className="w-3 h-3 animate-spin" />
                                                    ) : (
                                                        <span>+ 排入開發</span>
                                                    )}
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                    {(statusData?.stats?.priority_list || []).length > visibleBacklogCount && (
                                        <button 
                                            onClick={() => setVisibleBacklogCount(prev => prev + 10)}
                                            className={`w-full py-3 rounded-xl text-xs font-bold tracking-widest uppercase transition-all border ${darkMode ? 'border-white/5 text-zinc-400 hover:bg-white/5' : 'border-zinc-200 text-zinc-500 hover:bg-zinc-100'}`}
                                        >
                                            載入更多 (剩餘 {(statusData?.stats?.priority_list || []).length - visibleBacklogCount} 筆)
                                        </button>
                                    )}
                                    {(statusData?.stats?.priority_list || []).length === 0 && (
                                        <div className="text-center py-6 text-sm text-zinc-500 italic">目前收容池中沒有尚未排定的策略。</div>
                                    )}
                                </div>
                            </div>
                        </div>

                        <div className={`backdrop-blur-xl rounded-[2.5rem] border shadow-2xl overflow-hidden transition-all duration-500 ${darkMode ? 'bg-zinc-900/40 border-white/5' : 'bg-white border-zinc-200 shadow-xl'}`}>
                            <div className={`p-8 border-b flex items-center justify-between ${darkMode ? 'border-white/5' : 'border-zinc-100'}`}>
                                <div className="flex items-center gap-3">
                                    <div className={`p-3 rounded-2xl border ${darkMode ? 'bg-brand-primary/10 text-brand-primary border-brand-primary/20' : 'bg-brand-primary/10 text-brand-primary border-brand-primary/10 shadow-lg'}`}>
                                        <Database className="w-5 h-5" />
                                    </div>
                                    <div>
                                        <h2 className="text-xl font-black">開發進度清單</h2>
                                        <p className="text-xs font-medium opacity-60">各項策略所需數據的盤點與開發狀態</p>
                                    </div>
                                </div>
                            </div>

                            <div className="overflow-x-auto">
                                <table className="w-full text-left">
                                    <thead className={`text-[10px] font-black uppercase tracking-[0.2em] ${darkMode ? 'bg-zinc-950/50 text-zinc-500' : 'bg-zinc-50 text-zinc-400'}`}>
                                        <tr>
                                            <th className="px-8 py-5 cursor-pointer hover:text-brand-primary" onClick={() => handleSort('serialId')}>
                                                <span className="flex items-center gap-1"># 序號 {sortField === 'serialId' ? (sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />) : <ArrowDownUp className="w-3 h-3 opacity-30" />}</span>
                                            </th>
                                            <th className="px-8 py-5">開發項目 (Asset/Article)</th>
                                            <th className="px-8 py-5">類別</th>
                                            <th className="px-8 py-5 text-center">實作程式</th>
                                            <th className="px-8 py-5 cursor-pointer hover:text-brand-primary" onClick={() => handleSort('likesCount')}>
                                                <span className="flex items-center gap-1">社區熱度 {sortField === 'likesCount' ? (sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />) : <ArrowDownUp className="w-3 h-3 opacity-30" />}</span>
                                            </th>
                                            <th className="px-8 py-5">數據盤點與同步</th>
                                            <th className="px-8 py-5">目標與來源</th>
                                            <th className="px-8 py-5 cursor-pointer hover:text-brand-primary" onClick={() => handleSort('status')}>
                                                <span className="flex items-center gap-1">狀態 {sortField === 'status' ? (sortDir === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />) : <ArrowDownUp className="w-3 h-3 opacity-30" />}</span>
                                            </th>
                                            <th className="px-8 py-5">操作</th>
                                        </tr>
                                    </thead>
                                    <tbody className={`divide-y ${darkMode ? 'divide-white/5' : 'divide-zinc-100'}`}>
                                        {((): React.ReactNode => {
                                            const raw = (statusData?.sync_progress || []).filter((item: any) => item.id !== 'TradingView_Scripts');
                                            const filtered = raw.filter((item: any) => {
                                                const titleMatch = !searchQuery || (item.dataset || '').toLowerCase().includes(searchQuery.toLowerCase());
                                                const statusMatch =
                                                    statusFilter === 'all' ? true :
                                                    statusFilter === 'pending' ? (!item.is_implemented && !item.is_web_done) :
                                                    statusFilter === 'implemented' ? item.is_implemented :
                                                    statusFilter === 'done' ? item.is_web_done : true;
                                                return titleMatch && statusMatch;
                                            });
                                            const sorted = [...filtered].sort((a: any, b: any) => {
                                                let cmp = 0;
                                                if (sortField === 'serialId') cmp = (a.serialId || '').localeCompare(b.serialId || '');
                                                else if (sortField === 'likesCount') cmp = (a.likesCount || 0) - (b.likesCount || 0);
                                                else if (sortField === 'status') cmp = (a.is_web_done ? 2 : a.is_implemented ? 1 : 0) - (b.is_web_done ? 2 : b.is_implemented ? 1 : 0);
                                                return sortDir === 'asc' ? cmp : -cmp;
                                            });
                                            if (sorted.length === 0) return (
                                                <tr><td colSpan={9} className="px-8 py-12 text-center text-sm text-zinc-500 italic">沒有符合條件的策略</td></tr>
                                            );
                                            return sorted.map((item: any, idx: number) => (
                                            <tr key={idx} className={`group transition-colors ${darkMode ? 'hover:bg-white/[0.02]' : 'hover:bg-zinc-50/50'}`}>
                                                <td className="px-8 py-6">
                                                    <span className="font-mono text-xs opacity-40">#{item.serialId || '---'}</span>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className={`font-bold text-base ${darkMode ? 'text-white' : 'text-zinc-900'}`}>{item.dataset?.replace(/\[#\d+\]\s*/, '') ?? 'Unknown Dataset'}</div>
                                                    <div className="text-[10px] font-normal mt-1 flex items-center gap-2 tracking-wider opacity-60">
                                                        <span className="uppercase">{item.usage ?? 'N/A'}</span>
                                                        <span>•</span>
                                                        <span>{item.last_updated ? new Date(item.last_updated).toLocaleString('zh-TW', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) : '無更新紀錄'}</span>
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <span className={cn(
                                                        "px-2 py-1 rounded-md text-[9px] font-black uppercase tracking-tighter border",
                                                        item.category === 'Stock' ? "bg-blue-500/10 text-blue-400 border-blue-500/20" :
                                                        item.category === 'ETF' ? "bg-purple-500/10 text-purple-400 border-purple-500/20" :
                                                        "bg-amber-500/10 text-amber-400 border-amber-500/20"
                                                    )}>
                                                        {item.category || 'Stock'}
                                                    </span>
                                                </td>

                                                <td className="px-8 py-6 text-center">
                                                    <button
                                                        onClick={() => handleToggleStatus(item.id, item.isScriptDone, 'script')}
                                                        disabled={togglingId === `${item.id}-script`}
                                                        className={cn(
                                                            "w-8 h-8 rounded-lg mx-auto flex items-center justify-center transition-all border shadow-shimmer-sm",
                                                            item.isScriptDone 
                                                                ? "bg-blue-500 text-white border-blue-400/50 shadow-blue-500/20" 
                                                                : "bg-zinc-800/50 border-white/5 text-white/20 hover:text-white/40"
                                                        )}
                                                    >
                                                        {item.isScriptDone ? <Check className="w-4 h-4" /> : <div className="w-1.5 h-1.5 rounded-full bg-current" />}
                                                    </button>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="flex items-center gap-1.5 text-brand-primary font-black text-sm">
                                                        <Sun className="w-3.5 h-3.5 fill-current" />
                                                        {(item.likesCount || 0).toLocaleString()}
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6 whitespace-nowrap">
                                                    <div className="flex items-center gap-2 mb-1">
                                                        <span className="text-[10px] font-black opacity-40 uppercase">Provider:</span>
                                                        <span className="text-xs font-bold text-emerald-500">{item.provider}</span>
                                                    </div>
                                                    <div className="text-sm font-medium">{item.inventory_desc}</div>
                                                    <div className="text-[10px] mt-1 opacity-60">{item.description}</div>
                                                    <div className="mt-2 inline-flex items-center gap-1.5 px-2 py-0.5 bg-zinc-800 rounded text-[9px] font-mono opacity-50">
                                                        {item.twse_dataset}
                                                    </div>
                                                 </td>
                                                <td className="px-8 py-6">
                                                    <div className="flex flex-col gap-2">
                                                        <a 
                                                            href={item.target_url} 
                                                            target="_blank" 
                                                            rel="noopener noreferrer"
                                                            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${darkMode ? 'bg-brand-primary/10 text-brand-primary hover:bg-brand-primary hover:text-white border border-brand-primary/20' : 'bg-brand-primary/5 text-brand-primary hover:bg-brand-primary hover:text-white border border-brand-primary/10 shadow-sm'}`}
                                                        >
                                                            <ExternalLink className="w-3.5 h-3.5" />
                                                            <span>研發頁面</span>
                                                        </a>
                                                        <a 
                                                            href={item.external_url} 
                                                            target="_blank" 
                                                            rel="noopener noreferrer"
                                                            className={`inline-flex items-center gap-1.5 px-2 text-[10px] font-bold opacity-60 hover:opacity-100 transition-opacity ${darkMode ? 'text-zinc-400' : 'text-zinc-500'}`}
                                                        >
                                                            <LinkIcon className="w-3 h-3" />
                                                            <span>原始來源</span>
                                                        </a>
                                                    </div>
                                                </td>
                                                <td className="px-8 py-6">
                                                    <div className="flex flex-col gap-3">
                                                        <div className="flex items-center gap-3">
                                                            <button
                                                                onClick={() => handleToggleStatus(item.id, item.is_implemented, 'implemented')}
                                                                disabled={togglingId === `${item.id}-implemented`}
                                                                className={`w-10 h-6 p-1 rounded-full transition-all flex ${item.is_implemented ? 'bg-emerald-500 justify-end' : 'bg-zinc-600 justify-start'} ${togglingId === `${item.id}-implemented` ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                                                            >
                                                                <div className="w-4 h-4 bg-white rounded-full shadow-sm" />
                                                            </button>
                                                            {item.is_implemented ? (
                                                                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black bg-emerald-500/10 text-emerald-500 border border-emerald-500/20 uppercase">
                                                                    已復刻
                                                                </span>
                                                            ) : (
                                                                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black bg-amber-500/10 text-amber-500 border border-amber-500/20 uppercase">
                                                                    待開發
                                                                </span>
                                                            )}
                                                        </div>
                                                        <div className="flex items-center gap-3">
                                                            <button
                                                                onClick={() => handleToggleStatus(item.id, item.is_web_done, 'web')}
                                                                disabled={togglingId === `${item.id}-web`}
                                                                className={`w-10 h-6 p-1 rounded-full transition-all flex ${item.is_web_done ? 'bg-blue-500 justify-end' : 'bg-zinc-600 justify-start'} ${togglingId === `${item.id}-web` ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
                                                            >
                                                                <div className="w-4 h-4 bg-white rounded-full shadow-sm" />
                                                            </button>
                                                            {item.is_web_done ? (
                                                                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black bg-blue-500/10 text-blue-500 border border-blue-500/20 uppercase">
                                                                    已完成
                                                                </span>
                                                            ) : (
                                                                <span className="inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-black bg-zinc-500/10 text-zinc-500 border border-zinc-500/20 uppercase">
                                                                    未確認
                                                                </span>
                                                             )}
                                                         </div>
                                                     </div>
                                                 </td>
                                                 <td className="px-8 py-6">
                                                     <button
                                                         onClick={() => handleDemote(item.target_url?.split('/').pop() || '', item.dataset?.replace(/\[#\d+\]\s*/, '') || '')}
                                                         disabled={demotingId === (item.target_url?.split('/').pop() || '')}
                                                         title="移回收容池"
                                                         className={`px-2.5 py-1.5 rounded-lg text-[10px] font-black transition-all border ${demotingId === (item.target_url?.split('/').pop() || '') ? 'bg-zinc-700 opacity-50 cursor-not-allowed text-zinc-400 border-zinc-600' : 'bg-zinc-800/50 text-zinc-500 border-white/5 hover:bg-red-500/10 hover:text-red-400 hover:border-red-500/20'}`}
                                                     >
                                                         {demotingId === (item.target_url?.split('/').pop() || '') ? <RefreshCw className="w-3 h-3 animate-spin" /> : '↩ 移回'}
                                                     </button>
                                                 </td>
                                             </tr>
                                         ));
                                         })()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
