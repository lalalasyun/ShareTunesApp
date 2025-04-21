#!/bin/bash

# このスクリプトはLet's Encryptの証明書を初めて取得する際に使用します
# EC2インスタンスで実行してください

if ! [ -x "$(command -v docker-compose)" ]; then
  echo 'Error: docker-compose is not installed.' >&2
  exit 1
fi

# ルートディレクトリの.envファイルを読み込む
if [ -f ../.env ]; then
  echo "Loading environment variables from ../.env"
  export $(grep -v '^#' ../.env | xargs)
else
  echo "Error: .env file not found in parent directory." >&2
  echo "Please create a .env file based on .env.example" >&2
  exit 1
fi

# 環境変数のチェック
if [ -z "$DOMAIN_NAME" ] || [ -z "$CERTBOT_EMAIL" ]; then
  echo "Error: Required environment variables are missing." >&2
  echo "Please make sure DOMAIN_NAME and CERTBOT_EMAIL are set in .env file" >&2
  exit 1
fi

# 環境変数の設定
domains=($DOMAIN_NAME)
# DOMAIN_NAME_WWWが設定されていれば追加
if [ ! -z "$DOMAIN_NAME_WWW" ]; then
  domains+=($DOMAIN_NAME_WWW)
fi

rsa_key_size=4096
data_path="./nginx/certs"
email=$CERTBOT_EMAIL
staging=${CERTBOT_STAGING:-0} # 環境変数がない場合は0（本番環境）をデフォルト値とする

echo "Domain: ${domains[0]}"
echo "Additional domains: ${domains[@]:1}"
echo "Email: $email"
echo "Staging: $staging (0=production, 1=test)"

# 現在のドメインに応じて証明書のパスを修正
sed -i "s/example.com/${domains[0]}/g" ./nginx/nginx.conf

# ディレクトリの作成
mkdir -p ./nginx/certbot/www
mkdir -p "$data_path"

echo "### 証明書取得の準備中..."

# Nginxのみを起動してLet's Encryptの検証に対応
docker-compose -f docker-compose.prod.yml up --force-recreate -d nginx
echo "### Nginxを起動しました"

# ワイルドカード証明書を取得（DNSチャレンジ）
echo "### Let's Encryptから証明書を取得中..."

# スタンドアロンモードでcertbotを実行
docker-compose -f docker-compose.prod.yml run --rm --entrypoint "\
  certbot certonly --webroot -w /var/www/certbot \
    ${staging:+--staging} \
    --email $email \
    --agree-tos \
    --no-eff-email \
    ${domains[@]/#/-d } \
    --force-renewal" certbot
echo

echo "### Nginxを再起動..."
docker-compose -f docker-compose.prod.yml up --force-recreate -d
echo

echo "### 完了!"