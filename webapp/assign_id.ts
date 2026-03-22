import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: "postgresql://postgres:postgres123@localhost:5433/tradeview_strategy?schema=public"
    }
  }
});

async function main() {
  const updated = await prisma.$executeRaw`
    UPDATE tradingview_scripts 
    SET serial_id = '004' 
    WHERE id = 94;
  `;
  console.log('Update Successful, rows affected:', updated);
}

main()
  .catch((e) => {
    console.error(e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
