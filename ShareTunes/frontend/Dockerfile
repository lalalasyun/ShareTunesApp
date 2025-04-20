FROM node:18-alpine AS builder

WORKDIR /app

# 依存関係のインストール
COPY package*.json ./
RUN npm ci

# アプリケーションのコピー
COPY . .

# 空のpublicディレクトリを作成（存在しない場合のため）
RUN mkdir -p public

# ビルド
RUN npm run build

# 本番環境用イメージ
FROM node:18-alpine AS runner
WORKDIR /app

# 必要なファイルだけをコピー
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js

EXPOSE 3000

# 環境変数に基づいてCMDを切り分ける
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

ENTRYPOINT ["docker-entrypoint.sh"]