import { query } from '@/lib/db';
import ScriptsListClient from './ScriptsListClient';

async function getScripts() {
  const res = await query(`
    SELECT * 
    FROM tradingview_scripts
    ORDER BY last_synced_at DESC
  `);
  return res.rows;
}

export default async function ScriptsPage() {
  const scripts = await getScripts();
  return <ScriptsListClient initialScripts={scripts} />;
}
