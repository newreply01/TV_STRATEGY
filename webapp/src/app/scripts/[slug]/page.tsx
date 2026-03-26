import { prisma } from '@/lib/prisma';
import { notFound } from 'next/navigation';
import ScriptDetailClient from './ScriptDetailClient';
 
export const revalidate = 0;

async function getScript(slug: string) {
  const script = await prisma.tradingviewScript.findUnique({
    where: { slug }
  });
  
  if (!script) return null;

  const cleanScript = {
    id: script.id,
    slug: script.slug,
    title: script.title,
    author: script.author,
    url: script.url,
    category: script.category,
    image_url: script.imageUrl,
    description_en: script.descriptionEn,
    description_zh: script.descriptionZh,
    source_type: script.sourceType,
    description_full: script.descriptionFull,
    description_full_zh: script.descriptionFullZh,
    pine_script: script.pineScript,
    local_images: script.localImages,
    boosts_count: script.likesCount,
    comments_count: script.commentsCount,
    created_at: script.createdAt ? new Date(script.createdAt).toISOString() : null,
    updated_at: script.updatedAt ? new Date(script.updatedAt).toISOString() : null,
    last_synced_at: script.lastSyncedAt ? new Date(script.lastSyncedAt).toLocaleDateString('zh-TW') : '---',
    is_implemented: script.isImplemented,
    is_web_done: script.isWebDone,
    is_script_done: script.isScriptDone,
    serial_id: script.serialId,
    published_at: script.publishedAt ? new Date(script.publishedAt).toLocaleDateString('zh-TW') : '---',
  };

  return JSON.parse(JSON.stringify(cleanScript));
}

export default async function ScriptDetailPage({ params }: { params: { slug: string } }) {
  const { slug } = await params;
  const script = await getScript(slug);

  if (!script) {
    notFound();
  }

  return <ScriptDetailClient script={script} />;
}
