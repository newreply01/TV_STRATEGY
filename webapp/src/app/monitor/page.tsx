'use client';

import dynamic from 'next/dynamic';

const MonitorPageClient = dynamic(
  () => import('./MonitorPageClient'),
  { ssr: false }
);

export default function MonitorPage() {
  return <MonitorPageClient />;
}
