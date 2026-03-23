const { Client } = require('pg');
const dotenv = require('dotenv');
const path = require('path');

// Load .env from webapp root
dotenv.config({ path: path.resolve(__dirname, '.env') });

async function main() {
  const client = new Client({
    connectionString: process.env.DATABASE_URL,
  });
  
  try {
    await client.connect();
    const slug = '3ONFG3bJ-Omni-Flow-Consensus-LuxAlgo';
    const res = await client.query('SELECT * FROM tradingview_scripts WHERE slug = $1', [slug]);
    const script = res.rows[0];
    
    if (!script) {
        console.log('Script not found');
        return;
    }
    
    console.log('--- Script Details (Postgres Raw) ---');
    console.log('ID:', script.id);
    console.log('Slug:', script.slug);
    
    console.log('\n--- description_en ---');
    console.log(script.description_en ? script.description_en.substring(0, 300) + '...' : 'NULL');
    
    console.log('\n--- description_full ---');
    console.log(script.description_full ? script.description_full.substring(0, 300) + '...' : 'NULL');

    console.log('\n--- description_zh ---');
    console.log(script.description_zh ? script.description_zh.substring(0, 300) + '...' : 'NULL');

    console.log('\n--- description_full_zh ---');
    console.log(script.description_full_zh ? script.description_full_zh.substring(0, 300) + '...' : 'NULL');
    
  } catch (e) {
    console.error(e);
  } finally {
    await client.end();
  }
}

main();
