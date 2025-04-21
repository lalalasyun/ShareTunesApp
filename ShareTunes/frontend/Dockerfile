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

# 起動スクリプトをアプリディレクトリにコピー
COPY docker-entrypoint.sh ./
RUN chmod +x ./docker-entrypoint.sh

EXPOSE 3000

# エントリーポイントを相対パスで指定
CMD ["sh", "./docker-entrypoint.sh"]