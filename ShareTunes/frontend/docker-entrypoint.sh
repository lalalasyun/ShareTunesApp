#!/bin/sh

source import-env .env.local

if [ "$NEXT_PUBLIC_NODE_ENV" = "development" ]; then
  echo "Starting Next.js in development mode"
  npm run dev
else
  echo "Starting Next.js in production mode"
  npm start
fi