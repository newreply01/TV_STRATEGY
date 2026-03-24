import { prisma } from '@/lib/prisma';
import { notFound } from 'next/navigation';
import ScriptDetailClient from './ScriptDetailClient';

async function getScript(slug: string) {
  const script = await prisma.tradingviewScript.findUnique({
    where: { slug }
  });
  
  if (!script) return null;

  // 手動映射回蛇形命名 (snake_case)，因為 ScriptDetailClient 預期的是原始 DB 欄位名稱
  return {
    ...script,
    image_url: script.imageUrl,
    description_en: script.descriptionEn,
    description_zh: script.descriptionZh,
    source_type: script.sourceType,
    description_full: script.descriptionFull,
    pine_script: script.pineScript,
    local_images: script.localImages,
    boosts_count: script.likesCount, // 注意：Prisma 模型中是 likesCount 映射到 boosts_count
    comments_count: script.commentsCount,
    created_at: script.createdAt,
    updated_at: script.updatedAt,
    last_synced_at: script.lastSyncedAt,
    is_implemented: script.isImplemented,
    is_web_done: script.isWebDone,
    is_script_done: script.isScriptDone,
    serial_id: script.serialId,
    published_at: script.publishedAt,
  };
}

export default async function ScriptDetailPage({ params }: { params: { slug: string } }) {
  const { slug } = await params;
  const script = await getScript(slug);

  if (!script) {
    notFound();
  }

  return <ScriptDetailClient script={script} />;
}
