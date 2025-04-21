#!/bin/sh
set -e

# SSL証明書のパス
SSL_DIR="/etc/nginx/ssl/live/example.com"
SSL_CERT="$SSL_DIR/fullchain.pem"
SSL_KEY="$SSL_DIR/privkey.pem"

# 証明書が存在しない場合は自己署名証明書を生成
if [ ! -f "$SSL_CERT" ] || [ ! -f "$SSL_KEY" ]; then
    echo "SSL証明書が見つかりませんでした。自己署名証明書を生成します..."
    
    # 証明書のためのディレクトリを作成
    mkdir -p "$SSL_DIR"
    
    # 自己署名証明書の生成
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$SSL_KEY" \
        -out "$SSL_CERT" \
        -subj "/C=JP/ST=Tokyo/L=Shibuya/O=ShareTunes/OU=Dev/CN=localhost"
    
    echo "自己署名証明書を生成しました："
    echo "- 証明書: $SSL_CERT"
    echo "- 秘密鍵: $SSL_KEY"
    echo "注意: この証明書は開発環境専用です。本番環境ではLet's Encryptを使用してください。"
else
    echo "既存のSSL証明書を使用します。"
fi

# 元のDockerコマンドを実行
exec "$@"