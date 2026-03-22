const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  console.log('--- Prisma Diagnostic Start ---');
  try {
    const models = Object.keys(prisma);
    console.log('0. All Prisma Keys:', JSON.stringify(models));
    console.log('0b. tradingviewScript exists:', !!prisma.tradingviewScript);
    console.log('0c. tradingview_scripts exists:', !!prisma.tradingview_scripts);
    
    console.log('1. Testing Connection (SELECT 1)...');
    await prisma.$queryRaw`SELECT 1`;
    console.log('   Connection OK');

    const accessor = prisma.tradingviewScript || prisma.tradingview_scripts;
    if (!accessor) {
        throw new Error('Could not find accessor for TradingviewScript');
    }

    console.log('2. Testing count with accessor...');
    const total = await accessor.count();
    console.log('   Count:', total);

    console.log('3. Testing isImplemented filter...');
    const implemented = await accessor.count({
      where: { isImplemented: true }
    });
    console.log('   Implemented:', implemented);

    console.log('4. Testing Priority List Query...');
    const top = await accessor.findMany({
      where: { isImplemented: false },
      orderBy: { likesCount: 'desc' },
      take: 1
    });
    console.log('   Top Pending:', top[0]?.title || 'None');

  } catch (err) {
    console.error('!!! ERROR !!!');
    console.error(err);
  } finally {
    await prisma.$disconnect();
    console.log('--- Prisma Diagnostic End ---');
  }
}

main();
