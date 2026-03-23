const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const s004 = await prisma.tradingviewScript.findFirst({ where: { serialId: '004' } });
  const s005 = await prisma.tradingviewScript.findFirst({ where: { serialId: '005' } });

  console.log('--- S004 Description ---');
  console.log(s004 ? s004.descriptionFull?.substring(0, 1000) : 'Not found');
  console.log('\n--- S005 Description ---');
  console.log(s005 ? s005.descriptionFull?.substring(0, 1000) : 'Not found');
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
