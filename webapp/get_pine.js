const { PrismaClient } = require('@prisma/client');
const fs = require('fs');
const prisma = new PrismaClient();
async function main() {
  const script = await prisma.tradingviewScript.findFirst({
    where: { OR: [
      { slug: { contains: 'lpnsjMbH' } },
      { title: { contains: 'Clusters Volume Profile' } }
    ]}
  });
  if (script) {
    fs.writeFileSync('/tmp/pine_script.txt', script.pineScript || 'No code');
    console.log('Success, wrote to /tmp/pine_script.txt');
  } else {
    console.log('Script not found');
  }
}
main().catch(console.error).finally(() => prisma.$disconnect());
