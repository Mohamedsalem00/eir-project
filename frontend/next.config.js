/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  images: {
    domains: ['localhost'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/:path*`,
      },
    ]
  },
  experimental: {
    allowedDevOrigins: [
      'http://localhost:3000',
      'http://192.168.2.145:3000', // your LAN/dev IP
    ],
  },
}

module.exports = nextConfig
