import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* 暫時維持基礎配置以避開編譯錯誤 */
  async redirects() {
    if (process.env.NEXT_PUBLIC_HIDE_ADMIN === 'true') {
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
      ];
    }
    return [];
  },
};

export default nextConfig;
