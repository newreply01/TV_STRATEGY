import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  console.log('Starting forced update...')
  
  // Update S001 (Omni-Flow)
  const r1 = await prisma.$executeRaw`UPDATE tradingview_scripts SET image_url = '3ONFG3bJ', author = 'LuxAlgo' WHERE slug LIKE '%3ONFG3bJ-Omni-Flow%'`
  console.log('S001 Update rows:', r1)
  
  // Update S002 (Clusters)
  const r2 = await prisma.$executeRaw`UPDATE tradingview_scripts SET image_url = 'lpnsjMbH', author = 'LuxAlgo' WHERE slug LIKE '%lpnsjMbH-Clusters%'`
  console.log('S002 Update rows:', r2)
  
  // Verify
  const verify = await prisma.tradingviewScript.findMany({
    where: { slug: { contains: 'LuxAlgo' } },
    select: { slug: true, imageUrl: true, author: true, updatedAt: true }
  })
  console.log('Verification:', JSON.stringify(verify, null, 2))
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
