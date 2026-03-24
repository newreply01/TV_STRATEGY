import { prisma } from '@/lib/prisma';
import DevListClient from './DevListClient';

export const revalidate = 0;

async function getDevScripts() {
  return await prisma.tradingviewScript.findMany({
    where: {
      isWebDone: false,
      serialId: {
        not: null,
      },
    },
    orderBy: {
      serialId: 'desc',
    },
  });
}

export default async function DevelopmentPage() {
  const scripts = await getDevScripts();
  return <DevListClient initialScripts={scripts} />;
}
