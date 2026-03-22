import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  try {
    const { slug } = await request.json();

    if (!slug) {
      return NextResponse.json({ error: 'Missing slug' }, { status: 400 });
    }

    // 將 serialId 設回 null，移回收容池
    const updated = await prisma.tradingviewScript.update({
      where: { slug: slug },
      data: { serialId: null, isImplemented: false, isWebDone: false }
    });

    return NextResponse.json({ success: true, slug: updated.slug });
  } catch (error: any) {
    console.error('Demote script error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}
