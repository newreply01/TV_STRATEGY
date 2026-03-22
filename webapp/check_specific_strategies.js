const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  try {
    const s2 = await prisma.tradingviewScript.findFirst({
      where: { OR: [{ serialId: '002' }, { slug: { contains: 'Supertrend-Multi-Timeframe' } }] }
    });
    console.log('S002 DB ENTRY:', JSON.stringify(s2, null, 2));
    
    const s4 = await prisma.tradingviewScript.findFirst({
      where: { serialId: '004' }
    });
    console.log('S004 DB ENTRY:', JSON.stringify(s4, null, 2));

    const s5 = await prisma.tradingviewScript.findFirst({
      where: { serialId: '005' }
    });
    console.log('S005 DB ENTRY:', JSON.stringify(s5, null, 2));

  } catch (err) {
    console.error(err);
  } finally {
    await prisma.$disconnect();
  }
}

main();
