/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['i.scdn.co', 'mosaic.scdn.co', 'image-cdn-fa.spotifycdn.com', 'i.pravatar.cc'],
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        // IPv6ではなくIPv4を明示的に指定
        destination: 'http://127.0.0.1:8000/api/:path*',
      },
    ];
  },
};

module.exports = nextConfig;