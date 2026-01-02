/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow serving GLB files
  async headers() {
    return [
      {
        source: '/models/:path*',
        headers: [
          {
            key: 'Access-Control-Allow-Origin',
            value: '*',
          },
        ],
      },
    ]
  },
}

module.exports = nextConfig
