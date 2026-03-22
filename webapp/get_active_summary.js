const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  try {
    const scripts = await prisma.tradingviewScript.findMany({
      where: { serialId: { not: null } },
      orderBy: { serialId: 'asc' },
      select: { serialId: true, title: true, isImplemented: true, isWebDone: true, slug: true }
    });
    console.log('ACTIVE STRATEGIES:');
    scripts.forEach(s => {
      console.log(`[${s.serialId}] ${s.isImplemented ? '✅' : '⏳'} ${s.isWebDone ? '🏁' : '🛠️'} ${s.title} (${s.slug})`);
    });
  } catch (err) {
    console.error(err);
  } finally {
    await prisma.$disconnect();
  }
}

main();
