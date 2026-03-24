import { prisma } from '@/lib/prisma';
import ScriptsListClient from './ScriptsListClient';

export const revalidate = 0;

async function getScripts() {
  try {
    return await prisma.tradingviewScript.findMany({
      where: {
        isWebDone: true,
      },
      orderBy: {
        lastSyncedAt: 'desc',
      },
    });
  } catch (error: any) {
    console.error('Prisma Error in getScripts:', error);
    return { error: error.message || 'Unknown database error' };
  }
}

export default async function ScriptsPage() {
  const result = await getScripts();
  
  if ('error' in result) {
    return (
      <div className="min-h-screen bg-black text-white p-12 flex flex-col items-center justify-center gap-4">
        <h1 className="text-2xl font-bold text-red-500">無法連線至資料庫</h1>
        <p className="text-zinc-400 font-mono text-sm max-w-2xl bg-zinc-900 p-6 rounded-xl border border-white/5 whitespace-pre-wrap">
          {result.error}
        </p>
        <p className="text-zinc-500 text-xs italic">
          請檢查 Vercel Dashboard 的環境變數 DATABASE_URL 是否正確，且包含 sslmode=require。
        </p>
      </div>
    );
  }

  return <ScriptsListClient initialScripts={result} />;
}
