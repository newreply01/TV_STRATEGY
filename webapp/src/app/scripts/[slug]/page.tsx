import { query } from '@/lib/db';
import { notFound } from 'next/navigation';
import ScriptDetailClient from './ScriptDetailClient';

async function getScript(slug: string) {
  const res = await query(`
    SELECT * 
    FROM tradingview_scripts
    WHERE slug = $1
  `, [slug]);
  return res.rows[0];
}

export default async function ScriptDetailPage({ params }: { params: { slug: string } }) {
  const { slug } = await params;
  const script = await getScript(slug);

  if (!script) {
    notFound();
  }

  // Pass data to the Client Component for interactive features (Tabs, Chart)
  return <ScriptDetailClient script={script} />;
}
