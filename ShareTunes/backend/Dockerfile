FROM python:3.10-slim

WORKDIR /app

# 依存関係のインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコピー
COPY . .

# 環境変数の設定
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=sharetunes.settings

# マイグレーションと静的ファイルの収集を行うスクリプト
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# コンテナ起動時に実行されるコマンド
ENTRYPOINT ["/entrypoint.sh"]
# 開発環境用のDjango開発サーバーを使用
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]