const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const s001 = await prisma.tradingviewScript.findFirst({ where: { serialId: '001' } });

  console.log('--- S001 ---');
  console.log(s001 ? s001.pineScript?.substring(0, 500) : 'Not found');
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
