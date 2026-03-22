import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  try {
    const { id, isImplemented, type } = await request.json();

    if (!id) {
      return NextResponse.json({ error: 'Missing ID' }, { status: 400 });
    }

    // 嘗試從 id 提取 serialId (向下相容舊有格式)
    const serialMatch = id.match(/Strategy_(\d+)_Data/);
    let targetId = serialMatch ? `s${serialMatch[1]}` : id;

    const updateData: any = {};
    if (type === 'web') {
      updateData.isWebDone = !!isImplemented;
    } else if (type === 'script') {
      updateData.isScriptDone = !!isImplemented;
    } else {
      updateData.isImplemented = !!isImplemented;
    }

    const updated = await prisma.tradingviewScript.updateMany({
      where: {
        OR: [
          { serialId: targetId },
          { slug: targetId }
        ]
      },
      data: updateData
    });

    return NextResponse.json({ success: true, updatedCount: updated.count });
  } catch (error: any) {
    console.error('Toggle status error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}
