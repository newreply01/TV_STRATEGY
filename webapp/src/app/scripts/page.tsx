import { query } from '@/lib/db';
import ScriptsListClient from './ScriptsListClient';

export const revalidate = 0;

async function getScripts() {
  const res = await query(`
    SELECT * 
    FROM tradingview_scripts
    WHERE is_web_done = true
    ORDER BY last_synced_at DESC
  `);
  return res.rows;
}

export default async function ScriptsPage() {
  const scripts = await getScripts();
  return <ScriptsListClient initialScripts={scripts} />;
}
