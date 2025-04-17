#!/bin/bash

# マイグレーションの適用
echo "マイグレーションを適用しています..."
python manage.py migrate --noinput

# 静的ファイルの収集
echo "静的ファイルを収集しています..."
python manage.py collectstatic --noinput

# 実行権限の確認
exec "$@"