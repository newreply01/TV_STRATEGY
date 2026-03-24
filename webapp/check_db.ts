import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function main() {
  const scripts = await prisma.tradingviewScript.findMany({
    where: {
      slug: {
        in: ['3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo', 'lpnsjMbH-Clusters-Volume-Profile-LuxAlgo']
      }
    }
  })
  console.log(JSON.stringify(scripts, null, 2))
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
