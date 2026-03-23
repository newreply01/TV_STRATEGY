const { PrismaClient } = require('@prisma/client');
const prisma = new PrismaClient();

async function main() {
  try {
    const scripts = await prisma.tradingviewScript.findMany({
      where: {
        OR: [
          { slug: { contains: 'Omni-Flow', mode: 'insensitive' } },
          { title: { contains: 'Omni-Flow', mode: 'insensitive' } }
        ]
      }
    });
    
    console.log('--- Search Results ---');
    console.log('Count:', scripts.length);
    
    scripts.forEach(s => {
        console.log('\n--- Script ---');
        console.log('ID:', s.id);
        console.log('Slug:', s.slug);
        console.log('Title:', s.title);
        console.log('Fields present:', Object.keys(s).filter(k => s[k] !== null && s[k] !== undefined));
        
        console.log('\n--- Description EN Preview ---');
        console.log(s.description_en?.substring(0, 100) + '...');
        
        console.log('\n--- Description Full Preview ---');
        console.log(s.description_full?.substring(0, 100) + '...');

        console.log('\n--- Description ZH Preview ---');
        console.log(s.description_zh?.substring(0, 100) + '...');
    });
    
  } catch (e) {
    console.error(e);
  } finally {
    await prisma.$disconnect();
  }
}

main();
