const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const implemented = await prisma.tradingviewScript.findMany({
    where: {
      isImplemented: true
    },
    select: {
      serialId: true,
      title: true,
      slug: true,
      isImplemented: true,
      isWebDone: true
    },
    orderBy: {
      serialId: 'asc'
    }
  });
  console.log('Implemented Scripts:', JSON.stringify(implemented, null, 2));
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
