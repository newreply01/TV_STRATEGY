import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, IChartApi, CandlestickSeries, BaselineSeries, LineSeries, createSeriesMarkers } from 'lightweight-charts';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Cell } from 'recharts';
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
  const timescaleSeriesRef = useRef<any>(null);
  const dynamicSeriesRef = useRef<any[]>([]); // To track dynamically added series for cleanup

  const [isFocused, setIsFocused] = useState(false);
  const [hoverData, setHoverData] = useState<any>(null);
  const [indicatorValues, setIndicatorValues] = useState<any[]>([]);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    const chart = createChart(chartContainerRef.current, {
      layout: { background: { type: ColorType.Solid, color: '#000000' }, textColor: '#d1d4dc' },
      grid: { vertLines: { color: 'rgba(42, 46, 57, 0.02)' }, horzLines: { color: 'rgba(42, 46, 57, 0.02)' } },
      width: chartContainerRef.current.clientWidth,
      height: 600,
      handleScroll: { mouseWheel: false, pressedMouseMove: true, horzTouchDrag: true, vertTouchDrag: true },
      handleScale: { mouseWheel: false, pinch: true, axisPressedMouseMove: true },
      timeScale: { timeVisible: true, rightOffset: 5 },
      localization: {
        locale: 'zh-TW',
        dateFormat: 'MM/dd',
        timeFormatter: (t: number) => {
          const d = new Date(t * 1000);
          return `${d.getMonth() + 1}/${d.getDate()} ${d.getHours().toString().padStart(2, '0')}:${d.getMinutes().toString().padStart(2, '0')}`;
        }
      }
    });

    chartRef.current = chart;

    // 1. Candlestick (Main Series)
    candlestickSeriesRef.current = chart.addSeries(CandlestickSeries, {
      upColor: '#00ffcc', downColor: '#ff2e2e', borderVisible: false,
      wickUpColor: '#00ffcc', wickDownColor: '#ff2e2e',
      priceLineVisible: false, lastValueVisible: false
    }, 0);

    // 2. Hidden Timescale Support
    timescaleSeriesRef.current = chart.addSeries(LineSeries, {
      color: 'transparent', priceLineVisible: false, lastValueVisible: false,
      crosshairMarkerVisible: false, priceFormat: { type: 'custom', formatter: () => '' }
    });

    const handleResize = () => {
      if (chartRef.current && chartContainerRef.current) {
        chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
      }
    };
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    let active = true;
    const isS001 = slug.includes('Omni-Flow');
    const isS002 = slug.includes('Volume-Profile');
    
    // Interval defaults
    const interval = isS002 ? '5m' : '15m';
    const period = isS002 ? '7d' : '60d';
    const apiBase = process.env.NEXT_PUBLIC_API_URL || '/api/py';
    const url = `${apiBase}/charts/${slug}?symbol=${symbol}&interval=${interval}&period=${period}`;

    setLoading(true);
    fetch(url).then(res => res.json()).then((chartData: any) => {
      if (!active || !chartRef.current) return;

      try {
        if (chartData.error) throw new Error(chartData.error);
        setData(chartData);

        // CRITICAL: Clear any residue markers and series before rendering new data
        if (candlestickSeriesRef.current) {
          createSeriesMarkers(candlestickSeriesRef.current, []);
        }
        
        // Cleanup old dynamic series (indicators)
        dynamicSeriesRef.current.forEach(s => chartRef.current?.removeSeries(s));
        dynamicSeriesRef.current = [];

        const actualOHLC = (chartData.ohlc || []).filter((d: any) => d.close !== undefined);
        if (candlestickSeriesRef.current) candlestickSeriesRef.current.setData(actualOHLC);
        
        if (timescaleSeriesRef.current && chartData.ohlc) {
          const lastClose = actualOHLC[actualOHLC.length - 1]?.close || 0;
          const dummyData = chartData.ohlc.map((d: any) => ({ time: d.time, value: lastClose }));
          timescaleSeriesRef.current.setData(dummyData);
        }

        // --- DYNAMIC INDICATORS RENDERING ---
        // S001 Legacy Pane Support
        if (isS001) {
           if (chartData.indicator) {
              const flowSeries = chartRef.current.addSeries(BaselineSeries, {
                baseValue: { type: 'price', price: 0 },
                topFillColor1: 'rgba(0, 255, 255, 0.4)', topFillColor2: 'rgba(0, 255, 255, 0.05)', topLineColor: '#00ffff',
                bottomFillColor1: 'rgba(255, 46, 46, 0.05)', bottomFillColor2: 'rgba(255, 46, 46, 0.4)', bottomLineColor: '#ff2e2e',
                lineWidth: 3, lastValueVisible: false, priceLineVisible: false,
                title: 'FLOW'
              }, 1);
              flowSeries.setData(chartData.indicator.filter((d:any) => typeof d.value === 'number'));
              flowSeries.priceScale().applyOptions({ scaleMargins: { bottom: 0.2, top: 0.1 } });

              // Add reference levels for Omni-Flow (90, 70, 0, -70, -90)
              [90, 70, 0, -70, -90].forEach(p => {
                flowSeries.createPriceLine({
                  price: p,
                  color: p === 0 ? 'rgba(255, 255, 255, 0.4)' : (Math.abs(p) === 90 ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)'),
                  lineWidth: 1,
                  lineStyle: p === 0 ? 0 : 2, // 0: Solid, 2: Dashed
                  axisLabelVisible: false, // 隱藏右側標籤框
                });
              });

              dynamicSeriesRef.current.push(flowSeries);

              if (chartData.signal) {
                const signalSeries = chartRef.current.addSeries(LineSeries, {
                    color: 'rgba(200, 200, 200, 0.3)', lineWidth: 1, lastValueVisible: false, priceLineVisible: false,
                    title: 'SIGNAL'
                }, 1);
                signalSeries.setData(chartData.signal.filter((d:any) => typeof d.value === 'number'));
                dynamicSeriesRef.current.push(signalSeries);
              }

              if (chartData.markers) {
                 const finalMarkers = chartData.markers.map((m: any) => ({ ...m, shape: m.shape || 'circle', size: 1 }));
                 finalMarkers.sort((a:any, b:any) => a.time - b.time);
                 createSeriesMarkers(flowSeries, finalMarkers);
              }
           }
        }

        // S008 / Generic Indicators (Plural)
        if (chartData.indicators && Array.isArray(chartData.indicators)) {
           chartData.indicators.forEach((ind: any) => {
              const series = chartRef.current?.addSeries(LineSeries, {
                 color: ind.color || '#ffffff',
                 lineWidth: ind.lineWidth || 1,
                 lastValueVisible: false,
                 priceLineVisible: false,
                 title: ind.name
              }, ind.pane || 0);
              if (series && ind.data) {
                 series.setData(ind.data);
                 dynamicSeriesRef.current.push(series);
              }
           });
        }

        // Generic Markers on Main Series
        if (chartData.markers && !isS001 && candlestickSeriesRef.current) {
            const finalMarkers = chartData.markers.map((m: any) => ({ ...m, size: 1 }));
            finalMarkers.sort((a:any, b:any) => a.time - b.time);
            createSeriesMarkers(candlestickSeriesRef.current, finalMarkers);
        }

        if (chartData.ohlc && chartData.ohlc.length > 0) {
          const start = chartData.ohlc[0].time;
          const end = chartData.ohlc[chartData.ohlc.length - 1].time;
          requestAnimationFrame(() => {
            if (chartRef.current) {
              chartRef.current.timeScale().setVisibleRange({ from: start, to: end });
              chartRef.current.timeScale().applyOptions({ rightOffset: 5 });
            }
          });
        }
        setLoading(false);

        chartRef.current.subscribeCrosshairMove((param) => {
          if (param.time && param.seriesData.size > 0) {
            const ohlc = param.seriesData.get(candlestickSeriesRef.current);
            const dynamicVals: any[] = [];
            dynamicSeriesRef.current.forEach(s => {
                const val = param.seriesData.get(s);
                if (val) {
                    dynamicVals.push({ 
                        title: s.options().title, 
                        value: (val as any).value || (val as any).close,
                        color: s.options().color || s.options().topLineColor 
                    });
                }
            });
            setHoverData({ time: param.time, ohlc });
            setIndicatorValues(dynamicVals);
          } else {
            setHoverData(null);
            setIndicatorValues([]);
          }
        });
      } catch (e: any) {
        console.error(e);
        if (active) setError(e.message);
        setLoading(false);
      }
    }).catch(err => { if (active) { setError(err.message); setLoading(false); } });

    return () => { active = false; };
  }, [slug, symbol]);

  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.applyOptions({
        handleScroll: { mouseWheel: isFocused },
        handleScale: { mouseWheel: isFocused }
      });
    }
  }, [isFocused]);

  const hasVol = data?.volume_profile && data.volume_profile.length > 0;
  const isS001 = slug.includes('Omni-Flow');

  return (
    <div
      className={cn(
        "w-full bg-black rounded-2xl border transition-all duration-300 p-4 relative min-h-[650px] shadow-2xl overflow-hidden group flex flex-col gap-1",
        isFocused ? "border-brand-primary outline outline-2 outline-brand-primary/20" : "border-white/5"
      )}
      onMouseDown={() => setIsFocused(true)}
    >
      <div className="absolute top-6 left-8 z-30 pointer-events-none flex flex-col gap-1">
        <div className="flex items-center gap-3">
          <span className="text-lg font-black text-white tracking-tighter">
            {symbol} <span className="opacity-30 text-xs ml-1 font-medium">{isS001 ? '15m' : '5m'}</span>
          </span>
          <span className="text-[10px] font-black px-1.5 py-0.5 rounded bg-brand-primary/10 text-brand-primary border border-brand-primary/20">LIVE</span>
        </div>
        <div className="flex flex-wrap items-center gap-3 text-[11px] font-bold">
          {hoverData ? (
            <>
              <div className="flex items-center gap-1.5 bg-black/40 px-2 py-0.5 rounded-full border border-white/5 backdrop-blur-sm">
                <span className="text-zinc-500 uppercase">O</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.open?.toFixed(2)}</span>
                <span className="text-zinc-500 uppercase">H</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.high?.toFixed(2)}</span>
                <span className="text-zinc-500 uppercase">L</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.low?.toFixed(2)}</span>
                <span className="text-zinc-500 uppercase">C</span><span className={hoverData.ohlc?.close > hoverData.ohlc?.open ? "text-cyan-400" : "text-rose-500"}>{hoverData.ohlc?.close?.toFixed(2)}</span>
              </div>
              
              {/* Dynamic Indicator Values */}
              <div className="flex items-center gap-2">
                {indicatorValues.map((iv, idx) => (
                  <div key={idx} className="flex items-center gap-1.5 bg-black/40 px-2 py-0.5 rounded-full border border-white/5 backdrop-blur-sm">
                    <span className="text-zinc-500 uppercase text-[9px]">{iv.title}</span>
                    <span style={{ color: iv.color }}>{iv.value?.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <span className="text-zinc-600 animate-pulse uppercase tracking-widest text-[9px]">Awaiting Market Data Stream...</span>
          )}
        </div>
      </div>

      {!isFocused && (
        <div className="absolute inset-0 z-[60] flex items-center justify-center bg-black/5 pointer-events-none">
          <div className="px-4 py-2 bg-brand-primary text-white text-sm font-black rounded-xl shadow-2xl opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0 text-center">
            點擊圖表以啟用縮放<br/><span className="text-[10px] font-medium opacity-70">數據來源: Yahoo</span>
          </div>
        </div>
      )}

      <div className="flex flex-1 w-full relative min-h-[600px]">
        <div className="flex-1 h-full relative">
          <div ref={chartContainerRef} className="w-full h-full border border-white/5 rounded-xl overflow-hidden bg-zinc-950" />
          {hasVol && data.volume_profile && (
            <>
              <div className="absolute top-12 left-0 right-0 bottom-16 z-20 pointer-events-none px-4">
                {data.pocs?.map((poc: any, i: number) => {
                  const prices = data.volume_profile!.map((v: any) => v.price);
                  const maxP = Math.max(...prices);
                  const minP = Math.min(...prices);
                  const topPos = ((maxP - poc.price) / (maxP - minP || 1)) * 100;
                  return (
                    <div key={i} className="absolute left-0 right-0 flex items-center pl-4 pr-20" style={{ top: `${topPos}%`, transform: 'translateY(-50%)' }}>
                      <div className="text-xs font-black" style={{ color: poc.color }}>{(poc.total_volume/1000).toFixed(1)}K</div>
                      <div className="flex-1 h-[1px]" style={{ backgroundImage: `linear-gradient(to right, ${poc.color} 50%, transparent 50%)`, backgroundSize: '15px 1px' }} />
                      <div className="text-xs font-black bg-black/60 px-2 py-0.5 rounded border border-white/10 ml-2" style={{ color: poc.color }}>Vol: {(poc.total_volume/1000).toFixed(1)}K</div>
                    </div>
                  );
                })}
              </div>
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
            </>
          )}
        </div>
      </div>

      <div className="absolute bottom-6 left-8 z-50 text-[10px] font-black uppercase text-zinc-700">
        [YAHOO | {symbol} | {data?.metadata?.period || '---'}]
      </div>

      {loading && <div className="absolute inset-0 bg-black/60 backdrop-blur-sm z-40 flex items-center justify-center text-cyan-500 font-black">Updating Engine...</div>}
      {error && <div className="absolute inset-0 flex items-center justify-center bg-black/40 z-10 text-red-500 font-bold">{error}</div>}
    </div>
  );
}
