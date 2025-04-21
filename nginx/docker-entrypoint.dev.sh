#!/bin/sh

# シンプルな開発環境用エントリーポイントスクリプト
echo "Starting Nginx in development mode (HTTP only)..."

# コマンドを実行
exec "$@"