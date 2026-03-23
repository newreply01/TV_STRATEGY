const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const s004 = await prisma.tradingviewScript.findFirst({ where: { serialId: '004' } });
  const s005 = await prisma.tradingviewScript.findFirst({ where: { serialId: '005' } });

  console.log('--- S004 ---');
  console.log(s004 ? s004.pineScript?.substring(0, 500) : 'Not found');
  console.log('\n--- S005 ---');
  console.log(s005 ? s005.pineScript?.substring(0, 500) : 'Not found');
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
