#!/bin/sh

# 環境変数に基づいて実行するコマンドを決定
if [ "$NEXT_PUBLIC_NODE_ENV" = "development" ] || [ "$NEXT_PUBLIC_NODE_ENV" = "dev" ]; then
  echo "Starting Next.js in development mode..."
  exec npm run dev
else
  echo "Starting Next.js in production mode..."
  exec npm start
fi