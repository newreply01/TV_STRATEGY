import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* 暫時維持基礎配置以避開編譯錯誤 */
  env: {
    NEXT_PUBLIC_HIDE_ADMIN: process.env.VERCEL === '1' ? 'true' : (process.env.NEXT_PUBLIC_HIDE_ADMIN || 'false'),
  },
  async redirects() {
    const shouldHide = process.env.VERCEL === '1' || process.env.NEXT_PUBLIC_HIDE_ADMIN === 'true';
    if (shouldHide) {
      return [
        {
          source: '/monitor',
          destination: '/',
          permanent: false,
        },
        {
          source: '/admin',
          destination: '/',
          permanent: false,
        },
        {
          source: '/development',
          destination: '/',
          permanent: false,
        },
      ];
    }
    return [];
  },
  async rewrites() {
    return [
      {
        source: '/api/py/:path*',
        destination: 'http://127.0.0.1:26001/api/:path*',
      },
    ];
  },
};

export default nextConfig;
