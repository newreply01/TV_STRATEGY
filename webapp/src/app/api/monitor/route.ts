import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function GET() {
  try {
    // 1. 檢查資料庫狀態
    let dbStatus = 'DOWN';
    try {
      await prisma.$queryRaw`SELECT 1`;
      dbStatus = 'UP';
    } catch (e) {
      console.error('DB Check Error:', e);
    }

    // 2. 獲取系統服務狀態
    let backendStatus = 'DOWN';
    try {
      const backendRes = await fetch('http://localhost:26001/api/health', { signal: AbortSignal.timeout(2000) });
      if (backendRes.ok) {
        const data = await backendRes.json();
        if (data.status === 'UP') backendStatus = 'UP';
      }
    } catch (e) {
      // Backend is down or unreachable
    }

    const systemLogs = await prisma.systemLog.findMany({
      orderBy: { checkTime: 'desc' },
      distinct: ['serviceName'],
    });

    const scriptStatusList = systemLogs.map((log: any) => ({
      script: log.serviceName,
      db_last_status: log.status,
      message: log.message,
      last_run: log.checkTime,
      live_status: 'UNKNOWN'
    }));

    // 3. 獲取動態文章統計與進度清單
    const actualTotalCount = await prisma.tradingviewScript.count();

    // We only care about scripts that have a serialId assigned for the main list
    const allScripts = await prisma.tradingviewScript.findMany({
      where: {
        serialId: { not: null }
      },
      orderBy: { serialId: 'asc' }
    });

    // The backlog ones for priority_list
    const backlogScripts = await prisma.tradingviewScript.findMany({
      where: { serialId: null },
      orderBy: { likesCount: 'desc' },
      take: 50
    });

    const implementedCount = allScripts.filter((s: any) => s.isImplemented).length;
    const pendingCount = allScripts.length - implementedCount; // 目前排程在清單上的待開發數量

    const topPending = backlogScripts.map((s: any) => ({
         slug: s.slug,
         title: s.title || `未命名 (${s.slug})`,
         likes: s.likesCount || 0,
         category: s.category || 'Stock',
         url: s.url || '#'
    }));

    const stats = {
        total_articles: actualTotalCount,
        implemented: implementedCount,
        pending: pendingCount,
        priority_list: topPending
    };

    // 4. 重構 sync_progress
    const progress = await prisma.syncProgress.findMany({
      orderBy: { dataset: 'asc' }
    });

    const systemSync = progress
      .filter((p: any) => p.dataset === 'TradingView_Scripts')
      .map((row: any) => ({
        id: row.dataset,
        dataset: 'TradingView 策略列表',
        usage: '抓取熱門與編輯精選腳本',
        last_updated: row.lastSyncDate,
        script: 'crawler.py',
        provider: 'TradingView Inc.',
        description: '每小時更新',
        inventory_desc: '標題、作者、Pine 源碼與描述',
        twse_dataset: 'N/A (外部社群數據)',
        target_url: '/monitor',
        external_url: 'https://www.tradingview.com/scripts/',
        is_implemented: false,
        category: 'System',
        serialId: '',
        likesCount: 0,
        isScriptDone: false
    }));

    const strategySync = allScripts.map((s: any) => {
        const numId = s.serialId ? s.serialId.replace(/\D/g, '') : '';
        return {
          id: s.serialId,
          dataset: `[#${numId}] ${s.title}`,
          usage: '量價與策略即時運算', 
          last_updated: s.publishedAt || s.lastSyncedAt || new Date(),
          script: 'chart_engine.py',
          provider: 'Local PostgreSQL',
          description: '1m / 15m Real-time',
          inventory_desc: '開/高/低/收/成交量',
          twse_dataset: '個股日成交資訊',
          target_url: `/scripts/${s.slug}`,
          external_url: s.url || '#',
          is_implemented: !!s.isImplemented,
          is_web_done: !!s.isWebDone,
          category: s.category || 'Stock',
          serialId: numId,
          likesCount: s.likesCount || 0,
          isScriptDone: !!s.isScriptDone
        };
    });

    const syncDetails = [...systemSync, ...strategySync];

    return NextResponse.json({
      success: true,
      status: {
        database: dbStatus,
        scheduler: 'UP',
        backend: backendStatus
      },
      stats,
      script_status: scriptStatusList,
      sync_progress: syncDetails
    });

  } catch (error: any) {
    console.error('Monitor API Error:', error);
    return NextResponse.json({ 
        success: false, 
        error: '資料讀取暫時中斷',
        details: error.message,
        status: {
            database: 'ERROR',
            scheduler: 'UNKNOWN',
            backend: 'UP'
        },
        stats: {
            total_articles: 0,
            implemented: 0,
            pending: 0,
            priority_list: []
        },
        script_status: [],
        sync_progress: []
    }, { status: 200 });
  }
}
