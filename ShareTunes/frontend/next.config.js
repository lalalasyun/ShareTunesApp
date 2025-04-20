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
  // Dockerでのホットリロードを改善するための設定
  webpackDevMiddleware: (config) => {
    // Windows+Docker環境でのファイル監視を向上させるための設定
    config.watchOptions = {
      poll: 1000, // ポーリング間隔を1秒に設定
      aggregateTimeout: 300, // 変更を集約する時間
      ignored: /node_modules/,
    };
    return config;
  },
};

module.exports = nextConfig;