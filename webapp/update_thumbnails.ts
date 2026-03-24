import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  // Update S001
  await prisma.tradingviewScript.update({
    where: { slug: '3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo' },
    data: { 
      imageUrl: '3ONFG3bJ',
      author: 'LuxAlgo',
      category: 'Stock'
    }
  })
  
  // Update S002
  await prisma.tradingviewScript.update({
    where: { slug: 'lpnsjMbH-Clusters-Volume-Profile-LuxAlgo' },
    data: { 
      imageUrl: 'lpnsjMbH',
      author: 'LuxAlgo',
      category: 'Stock'
    }
  })
  
  console.log('Database updated with thumbnails and metadata.')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
