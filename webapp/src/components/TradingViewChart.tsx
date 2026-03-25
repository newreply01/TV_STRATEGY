import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, CandlestickSeries, BaselineSeries, LineSeries, createSeriesMarkers } from 'lightweight-charts';
import { Maximize2, Minimize2, Settings2, BarChart2 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Cell, Tooltip } from 'recharts';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface ChartData {
  ohlc: any[];
  indicator: any[];
  signal: any[];
  markers: any[];
  volume_profile?: any[];
  pocs?: any[];
  error?: string;
  metadata?: any;
}

export default function TradingViewChart({ slug, symbol = 'AAPL' }: { slug: string; symbol?: string }) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<ChartData | null>(null);

  const candlestickSeriesRef = useRef<any>(null);
  const flowSeriesRef = useRef<any>(null);
  const signalSeriesRef = useRef<any>(null);

  const [isFocused, setIsFocused] = useState(false);
  const [hoverData, setHoverData] = useState<any>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    // Initial Setup
    const chart = createChart(chartContainerRef.current, {
      layout: { background: { type: ColorType.Solid, color: '#000000' }, textColor: '#d1d4dc' },
      grid: { vertLines: { color: 'rgba(42, 46, 57, 0.05)' }, horzLines: { color: 'rgba(42, 46, 57, 0.05)' } },
      width: chartContainerRef.current.clientWidth,
      height: 600,
      handleScroll: {
        mouseWheel: false,
        pressedMouseMove: true,
        horzTouchDrag: true,
        vertTouchDrag: true,
      },
      handleScale: {
        mouseWheel: false,
        pinch: true,
        axisPressedMouseMove: true,
      },
      timeScale: { timeVisible: true, rightOffset: 150 }, // 預留兩天的空位緩衝
      localization: {
        locale: 'zh-TW', dateFormat: 'MM/dd',
        timeFormatter: (t: number) => {
          const d = new Date(t * 1000);
          return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
        }
      }
    });

    chartRef.current = chart;

    // Core Setup
    const isS002 = slug.includes('Volume-Profile');
    const isS001 = slug.includes('Omni-Flow');

    // Only add indicator pane for S001
    const indicatorPane = isS001 ? chart.addPane() : null;
    if (indicatorPane) {
      indicatorPane.setHeight(240);
    }

    const candlestickSeries = chart.addSeries(CandlestickSeries, {
      upColor: '#00ffcc', downColor: '#ff2e2e', borderVisible: false,
      wickUpColor: '#00ffcc', wickDownColor: '#ff2e2e',
      priceLineVisible: false, // Disable default price line
      lastValueVisible: false // Disable last value label on scale
    }, 0);
    candlestickSeriesRef.current = candlestickSeries;

    // S001 Specific Series
    if (isS001) {
      const flowSeries = chart.addSeries(BaselineSeries, {
        baseValue: { type: 'price', price: 0 },
        topFillColor1: 'rgba(0, 255, 255, 0.4)', topFillColor2: 'rgba(0, 255, 255, 0.05)', topLineColor: '#00ffff',
        bottomFillColor1: 'rgba(255, 46, 46, 0.05)', bottomFillColor2: 'rgba(255, 46, 46, 0.4)', bottomLineColor: '#ff2e2e',
        lineWidth: 3,
        lastValueVisible: false,
        priceLineVisible: false,
        priceFormat: {
          type: 'custom',
          formatter: (price: number) => {
            const rounded = Math.round(price);
            if ([90, 70, 0, -70, -90].includes(rounded) && Math.abs(price - rounded) < 0.1) return '';
            return price.toFixed(2);
          },
        },
      }, 1);

      flowSeries.priceScale().applyOptions({
        scaleMargins: { bottom: 0.2, top: 0.1 },
      });

      flowSeriesRef.current = flowSeries;

      const signalSeries = chart.addSeries(LineSeries, {
        color: 'rgba(200, 200, 200, 0.3)', lineWidth: 1,
        lastValueVisible: false,
        priceLineVisible: false,
        priceFormat: { type: 'custom', formatter: (price: number) => price.toFixed(2) },
      }, 1);
      signalSeriesRef.current = signalSeries;

      [90, 70, 0, -70, -90].forEach(p => {
        flowSeries.createPriceLine({
          price: p,
          color: p === 0 ? 'rgba(255, 255, 255, 0.4)' : (Math.abs(p) === 90 ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'),
          lineWidth: 1,
          lineStyle: p === 0 ? 0 : 1,
          axisLabelVisible: true,
          title: p === 0 ? 'ZERO' : `${p > 0 ? '+' : ''}${p}`,
        });
      });
      
      chartRef.current = chart;
    }

    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };

    if (chartRef.current) {
        const isS001 = slug.includes('Omni-Flow');
        const isS002 = slug.includes('Volume-Profile');
        
        chartRef.current.timeScale().applyOptions({
            rightOffset: (isS001 || isS002) ? 150 : 30,
            barSpacing: 6,
            minBarSpacing: 0.5,
        });

        window.addEventListener('resize', handleResize);
    }

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []);

  // Sync Data Effect
  useEffect(() => {
    let active = true;
    const isS002 = slug.includes('Volume-Profile');
    const isTW = symbol.toUpperCase().includes('.TW') || /^\d+$/.test(symbol);
    const interval = isS002 ? '5m' : '15m';
    const period = isS002 ? (isTW ? '7d' : '5d') : '60d'; 
    const sourceParam = 'yahoo'; // 預留切換參數: 可改為 'local' 進行本地回測
    const host = typeof window !== 'undefined' ? window.location.hostname : '127.0.0.1';
    
    // Support remote API URL via env var, fallback to dynamic hostname on port 26001
    const apiBase = process.env.NEXT_PUBLIC_API_URL || '/api/py';
                      
    const url = `${apiBase}/charts/${slug}?symbol=${symbol}&interval=${interval}&period=${period}&source=${sourceParam}`;

    setLoading(true);
    fetch(url).then(res => res.json()).then((chartData: ChartData) => {
      if (!active || !chartRef.current) return;

      try {
        if (chartData.error) throw new Error(chartData.error);
        setData(chartData);

        if (chartData.ohlc && candlestickSeriesRef.current) candlestickSeriesRef.current.setData(chartData.ohlc);
        
        // S001 Specific
        if (chartData.indicator && flowSeriesRef.current) flowSeriesRef.current.setData(chartData.indicator);
        if (chartData.signal && signalSeriesRef.current) signalSeriesRef.current.setData(chartData.signal);

        if (active && chartData.markers && flowSeriesRef.current) {
            const finalMarkers = chartData.markers.map((m: any) => ({ ...m, shape: m.shape || 'circle', size: 1 }));
            finalMarkers.sort((a, b) => a.time - b.time);
            createSeriesMarkers(flowSeriesRef.current, finalMarkers);
        }

        if (active && chartRef.current) {
          if (chartData.ohlc && chartData.ohlc.length > 150) {
            const dataLength = chartData.ohlc.length;
            // 由於加入了未來時間節點，過濾出有實體資料的部分來精算起點
            const actualData = chartData.ohlc.filter((d: any) => d.close !== undefined);
            const actualLength = actualData.length;
            const lastTime = chartData.ohlc[dataLength - 1].time as any;
            // 依靠後端注入的未來虛擬節點來延伸時間軸
            const firstTime = chartData.ohlc[0].time as any;
            const lastFutureTime = chartData.ohlc[dataLength - 1].time as any;
            
            requestAnimationFrame(() => {
              if (chartRef.current) {
                chartRef.current.timeScale().setVisibleRange({ 
                  from: firstTime, 
                  to: lastFutureTime 
                });
              }
            });
          } else {
            chartRef.current.timeScale().fitContent();
          }
          
          // 保留 20 根的右側微邊距，增加呼吸感
          chartRef.current.timeScale().applyOptions({ rightOffset: 20 });
        }
        setLoading(false);

        // Crosshair Move Handling
        chartRef.current.subscribeCrosshairMove((param) => {
           if (param.time && param.seriesData.size > 0) {
              const ohlc = param.seriesData.get(candlestickSeriesRef.current);
              const flow = flowSeriesRef.current ? param.seriesData.get(flowSeriesRef.current) : null;
              const signal = signalSeriesRef.current ? param.seriesData.get(signalSeriesRef.current) : null;
              
              setHoverData({
                time: param.time,
                ohlc: ohlc,
                flow: flow,
                signal: signal
              });
           } else {
              setHoverData(null);
           }
        });

      } catch (e: any) {
        console.error('[CHART ERROR]', e);
        if (active) setError(e.message);
        setLoading(false);
      }
    }).catch(err => { if (active) { setError(err.message); setLoading(false); } });

    return () => { active = false; };
  }, [slug, symbol]);

  // Handle Focus Zoom Toggle
  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.applyOptions({
        handleScroll: { mouseWheel: isFocused },
        handleScale: { mouseWheel: isFocused }
      });
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (chartContainerRef.current && !chartContainerRef.current.contains(event.target as Node)) {
        setIsFocused(false);
      }
    };
    window.addEventListener('mousedown', handleClickOutside);
    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [isFocused]);

  const hasVolumeProfile = data?.volume_profile && data.volume_profile.length > 0;
  const isS001 = slug.includes('Omni-Flow');

  return (
    <div
      className={cn(
        "w-full bg-[#000000] rounded-2xl border transition-all duration-300 p-4 relative min-h-[650px] shadow-2xl overflow-hidden group flex flex-col gap-1",
        isFocused ? "border-brand-primary outline outline-2 outline-brand-primary/20" : "border-white/5"
      )}
      onMouseDown={() => setIsFocused(true)}
    >
      {/* Strategy Legend HUD (Professional View) */}
      <div className="absolute top-6 left-8 z-30 pointer-events-none flex flex-col gap-1">
        <div className="flex items-center gap-3">
           <span className="text-lg font-black text-white tracking-tighter">
             {symbol} <span className="opacity-30 text-xs ml-1 font-medium">{isS001 ? '15m' : '5m'}</span>
           </span>
           <div className="flex items-center gap-2">
              <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-brand-primary/10 text-brand-primary border border-brand-primary/20">LIVE</span>
           </div>
        </div>
        
        <div className="flex items-center gap-4 text-[11px] font-bold">
           {hoverData ? (
             <>
               <div className="flex items-center gap-1.5 bg-black/40 px-2 py-0.5 rounded-full border border-white/5 backdrop-blur-sm">
                  <span className="text-zinc-500 uppercase">O</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.open?.toFixed(2)}</span>
                  <span className="text-zinc-500 uppercase">H</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.high?.toFixed(2)}</span>
                  <span className="text-zinc-500 uppercase">L</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.low?.toFixed(2)}</span>
                  <span className="text-zinc-500 uppercase">C</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.close?.toFixed(2)}</span>
               </div>
               {isS001 && hoverData.flow && (
                 <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20 text-cyan-400">
                       <span className="uppercase text-[9px] opacity-70">Flow</span>
                       <span className="font-black">{hoverData.flow.value?.toFixed(2)}</span>
                    </div>
                    {hoverData.signal && (
                       <div className="flex items-center gap-1 bg-white/5 px-2 py-0.5 rounded-full border border-white/10 text-zinc-300">
                          <span className="uppercase text-[9px] opacity-70">Sig</span>
                          <span className="font-bold">{hoverData.signal.value?.toFixed(2)}</span>
                       </div>
                    )}
                 </div>
               )}
             </>
           ) : (
             <span className="text-zinc-600 animate-pulse uppercase tracking-widest text-[9px]">Awaiting Market Data Stream...</span>
           )}
        </div>
      </div>
      {!isFocused && (
        <div className="absolute inset-0 z-[60] flex items-center justify-center bg-black/5 pointer-events-none">
          <div className="px-4 py-2 bg-brand-primary text-white text-sm font-black rounded-xl shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0 text-center">
            點擊圖表以啟用縮放<br/><span className="text-[10px] font-medium opacity-70">數據來源: {data?.metadata?.source || '---'}</span>
          </div>      {/* HUD Removed per user request */}
       </div>
      )}

      <div className="flex flex-1 w-full gap-0 min-h-[600px] relative">
        {/* Right: Price Chart */}
        <div className="flex-1 h-full min-w-0 relative">
            <div ref={chartContainerRef} className="w-full h-full border border-white/5 rounded-xl overflow-hidden bg-zinc-950" />
            
            {/* Full-Width Cluster Lines */}
        {hasVolumeProfile && data.volume_profile && (
            <div className="absolute top-12 left-0 right-0 bottom-16 z-20 pointer-events-none px-4">
                {data.pocs && data.pocs.map((poc: any, i: number) => {
                    const prices = data.volume_profile!.map((v:any)=>v.price);
                    const maxP = Math.max(...prices);
                    const minP = Math.min(...prices);
                    const rangeP = maxP - minP || 1;
                    const topPos = ((maxP - poc.price) / rangeP) * 100;

                    return (
                        <div key={i} className="absolute left-0 right-0 flex items-center pl-4 pr-20" style={{ top: `${topPos}%`, transform: 'translateY(-50%)' }}>
                            {/* Left Label (Cluster Volume) */}
                            <div className="text-xs font-black whitespace-nowrap px-1 z-30 drop-shadow-md" style={{ color: poc.color }}>
                                {(poc.total_volume/1000).toFixed(1)}K
                            </div>
                            {/* Full Span Line (Ultra-Dense Custom Pattern) */}
                            <div className="flex-1 h-[1px]" style={{ 
                                backgroundImage: `linear-gradient(to right, ${poc.color} 50%, transparent 50%)`,
                                backgroundSize: '15px 1px',
                                backgroundRepeat: 'repeat-x',
                                opacity: 1,
                                filter: 'drop-shadow(0 0 2px rgba(255,255,255,0.2))'
                            }} />
                            {/* Right Label */}
                            <div className="text-xs font-black whitespace-nowrap bg-black/60 px-2 py-0.5 rounded shadow-lg border border-white/10 ml-2 z-30" style={{ color: poc.color }}>
                                Vol: {(poc.total_volume/1000).toFixed(1)}K
                            </div>
                        </div>
                    );
                })}
            </div>
        )}

        <div id="volume-profile-overlay" className="absolute top-0 right-0 bottom-0 left-0 pointer-events-none z-10 flex">
            {/* Chart Area filler */}
            <div className="flex-1" />
            
            {/* Overlay Volume Profile (Shifted further left to avoid Y-axis numbers) */}
            {hasVolumeProfile && data.volume_profile && (
                <div className="absolute top-12 right-20 bottom-16 w-40 md:w-56 lg:w-64 z-20 pointer-events-none">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data.volume_profile} layout="vertical" margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
                            <XAxis type="number" hide />
                            <YAxis dataKey="price" type="category" hide reversed />
                            <Bar dataKey="volume" isAnimationActive={false} barSize={1.2}>
                                {data.volume_profile.map((entry: any, index: number) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} fillOpacity={0.6} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
         </div>
      </div>

      <div id="chart-debug-info" className="absolute bottom-6 left-8 z-50 text-[10px] font-black uppercase tracking-widest text-zinc-700">
        [{data?.metadata?.source?.toUpperCase() || 'OFFLINE'} | {symbol} | {data?.metadata?.period || '---'}]
      </div>

      {loading && <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-40 flex items-center justify-center text-cyan-500 font-black uppercase tracking-tighter">Updating Engine...</div>}
      {error && <div className="absolute inset-0 flex items-center justify-center bg-red-950/20 backdrop-blur-md z-10 px-10 text-center text-red-500 font-bold">{error}</div>}
    </div>
  );
}

