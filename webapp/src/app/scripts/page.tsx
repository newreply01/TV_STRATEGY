import { prisma } from '@/lib/prisma';
import ScriptsListClient from './ScriptsListClient';

export const revalidate = 0;

async function getScripts() {
  return await prisma.tradingviewScript.findMany({
    where: {
      isWebDone: true,
    },
    orderBy: {
      lastSyncedAt: 'desc',
    },
  });
}

export default async function ScriptsPage() {
  const scripts = await getScripts();
  return <ScriptsListClient initialScripts={scripts} />;
}
