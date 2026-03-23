const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  const scripts = await prisma.tradingviewScript.findMany({
    where: {
      OR: [
        { title: { contains: 'Supertrend', mode: 'insensitive' } },
        { slug: { contains: 'Supertrend', mode: 'insensitive' } }
      ]
    }
  });

  console.log(JSON.stringify(scripts, null, 2));
}

main()
  .catch(e => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
