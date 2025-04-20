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
ENV ENVIRONMENT=development

# マイグレーションと静的ファイルの収集を行うスクリプト
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

# コンテナ起動時に実行されるコマンド
ENTRYPOINT ["/entrypoint.sh"]
# 環境変数によって実行コマンドを決定するスクリプト
CMD ["/bin/bash", "-c", "if [ \"$ENVIRONMENT\" = \"production\" ]; then gunicorn sharetunes.wsgi:application --bind 0.0.0.0:8000; else python manage.py runserver 0.0.0.0:8000; fi"]