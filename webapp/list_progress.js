const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  console.log('--- Current Strategy Progress ---');
  try {
    const scripts = await prisma.tradingviewScript.findMany({
      where: {
        serialId: { not: null }
      },
      orderBy: { serialId: 'asc' }
    });

    console.log('ID | Title | Implemented | Web Done | Category');
    console.log('---|-------|-------------|----------|---------');
    scripts.forEach(s => {
      console.log(`${s.serialId} | ${s.title} | ${s.isImplemented} | ${s.isWebDone} | ${s.category}`);
    });

    const backlogCount = await prisma.tradingviewScript.count({
      where: { serialId: null }
    });
    console.log(`\nBacklog Count: ${backlogCount}`);

  } catch (err) {
    console.error(err);
  } finally {
    await prisma.$disconnect();
  }
}

main();
