import type { NextConfig } from "next";

// Local backend. deployment.md: productionda bu URL backend-in real URL-i ilə əvəzlənir.
const BACKEND_URL = process.env.BACKEND_URL ?? "http://127.0.0.1:7999";

const nextConfig: NextConfig = {
  // Repo kökündə də package-lock.json var — Next.js workspace root-u
  // qarışdırmasın deyə frontend qovluğunu açıq göstəririk.
  turbopack: {
    root: import.meta.dirname,
  },
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${BACKEND_URL}/api/:path*`,
      },
    ];
  },
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "thumb.wikimedia.org" },
      { protocol: "https", hostname: "upload.wikimedia.org" },
      { protocol: "https", hostname: "r2.thesportsdb.com" },
      { protocol: "https", hostname: "crests.football-data.org" },
      { protocol: "http", hostname: "localhost" },
      { protocol: "http", hostname: "127.0.0.1" },
    ],
  },
};

export default nextConfig;
