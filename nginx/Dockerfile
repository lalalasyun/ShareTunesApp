FROM nginx:alpine

# OpenSSLをインストール
RUN apk add --no-cache openssl

# 設定ファイルをコピー
COPY nginx.conf /etc/nginx/nginx.conf

# ディレクトリ作成
RUN mkdir -p /etc/nginx/ssl

# 起動スクリプトを追加
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["nginx", "-g", "daemon off;"]