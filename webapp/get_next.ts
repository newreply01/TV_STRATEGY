import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: "postgresql://postgres:postgres123@localhost:5533/tradeview_strategy?schema=public"
    }
  }
});

async function main() {
  const strategy001: any[] = await prisma.$queryRaw`
    SELECT id, serial_id, slug, boosts_count, title 
    FROM tradingview_scripts 
    WHERE serial_id = '001';
  `;
  console.log('Strategy 001:', JSON.stringify(strategy001, null, 2));
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
