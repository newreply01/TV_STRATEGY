import { query } from '@/lib/db';
import DevListClient from './DevListClient';

export const revalidate = 0;

async function getDevScripts() {
  const res = await query(`
    SELECT * 
    FROM tradingview_scripts
    WHERE is_web_done = false AND serial_id IS NOT NULL
    ORDER BY serial_id DESC
  `);
  return res.rows;
}

export default async function DevelopmentPage() {
  const scripts = await getDevScripts();
  return <DevListClient initialScripts={scripts} />;
}
