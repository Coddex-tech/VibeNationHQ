import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  images: {
    remotePatterns: [
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "127.0.0.1",
        port: "8000",
        pathname: "/media/**",
      },
      // EXTERNAL PROVIDER CONFIG
      {
        protocol: 'https',
        hostname: 'is1-ssl.mzstatic.com',
      },
      {
        protocol: 'https',
        hostname: 'is2-ssl.mzstatic.com',
      },
      {
        protocol: 'https',
        hostname: 'is3-ssl.mzstatic.com',
      },
      {
        protocol: 'https',
        hostname: 'is4-ssl.mzstatic.com',
      },
      {
        protocol: 'https',
        hostname: 'is5-ssl.mzstatic.com',
      },
    ],
    dangerouslyAllowLocalIP: true,
  },
};

export default nextConfig;
