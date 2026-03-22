const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  try {
    const scripts = await prisma.tradingviewScript.findMany({
      where: { serialId: { not: null } },
      orderBy: { serialId: 'asc' }
    });
    console.log(JSON.stringify(scripts, null, 2));
  } catch (err) {
    console.error(err);
  } finally {
    await prisma.$disconnect();
  }
}

main();
