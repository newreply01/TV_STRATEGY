import { NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function POST(request: Request) {
  try {
    const { slug } = await request.json();

    if (!slug) {
      return NextResponse.json({ error: 'Missing slug' }, { status: 400 });
    }

    // 找出目前所有已被分配的 serial_id
    const allAssigned = await prisma.tradingviewScript.findMany({
      where: { serialId: { not: null } },
      select: { serialId: true }
    });
    
    let maxNum = 0;
    for (const s of allAssigned) {
      if (s.serialId) {
        const numMatch = s.serialId.match(/\d+/);
        if (numMatch) {
          const num = parseInt(numMatch[0], 10);
          if (num > maxNum) maxNum = num;
        }
      }
    }
    
    // 生成連續的新序號
    const nextNum = maxNum + 1;
    const newSerialId = `s${nextNum.toString().padStart(3, '0')}`; // e例如 s005

    // 更新該腳本並賦予排程
    const updated = await prisma.tradingviewScript.update({
      where: { slug: slug },
      data: { serialId: newSerialId }
    });

    return NextResponse.json({ success: true, newSerialId: updated.serialId });
  } catch (error: any) {
    console.error('Promote script error:', error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  } finally {
    await prisma.$disconnect();
  }
}
