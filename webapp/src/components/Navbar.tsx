'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, ScrollText, Home, ArrowRight } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();

  const navItems = [
    { name: '首頁', href: '/', icon: Home },
    { name: '策略中心', href: '/scripts', icon: ScrollText },
    { name: '管理中心', href: '/monitor', icon: LayoutDashboard },
  ];

  return (
    <nav className="sticky top-0 z-50 w-full border-b border-white/5 bg-zinc-950/80 backdrop-blur-xl">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
        <div className="flex items-center gap-8">
          <Link href="/" className="flex items-center gap-2 group">
            <div className="h-8 w-8 rounded-lg bg-brand-primary flex items-center justify-center transition-transform group-hover:scale-110 shadow-lg shadow-brand-primary/20">
              <span className="text-white font-black text-lg">T</span>
            </div>
            <span className="text-xl font-black tracking-tighter text-white">
              TradeView <span className="text-brand-primary">Strategy</span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            {navItems.map((item) => {
              const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
              const Icon = item.icon;
              
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all duration-300 ${
                    isActive
                      ? 'bg-brand-primary/10 text-brand-primary shadow-[inset_0_0_12px_rgba(239,68,68,0.1)]'
                      : 'text-zinc-400 hover:text-zinc-100 hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-brand-primary' : 'text-zinc-500'}`} />
                  {item.name}
                </Link>
              );
            })}
          </div>
        </div>

        <div className="flex items-center gap-4">
          <Link
            href="/monitor"
            className="hidden lg:flex items-center gap-2 rounded-xl bg-white px-4 py-2 text-sm font-black text-black transition-all hover:bg-zinc-200 active:scale-95"
          >
            即時狀態
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </nav>
  );
}
