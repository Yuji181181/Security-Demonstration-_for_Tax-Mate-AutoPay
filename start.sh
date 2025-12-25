#!/bin/bash

# Cloud Run が指定するポート（デフォルト8080）
PORT=${PORT:-8080}

# 1. バックエンド (FastAPI) をバックグラウンドで起動
# 0.0.0.0 でリッスンすることで、同一コンテナ内からアクセス可能にする
uv run uvicorn src.backend.server:app --host 0.0.0.0 --port 8000 &

# 2. サーバーが立ち上がるのを少し待つ
sleep 5

# 3. フロントエンド (Streamlit) をフォアグラウンドで起動
uv run streamlit run src/frontend/app.py --server.port $PORT --server.address 0.0.0.0