import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "TradeView Strategy | 策略監控與轉譯中樞",
  description: "專業的 TradingView 策略抓取、翻譯與監控平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="zh-TW"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col bg-zinc-950">
        <Navbar />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
