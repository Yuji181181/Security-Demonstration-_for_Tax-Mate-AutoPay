#!/bin/bash

# 1. バックエンド (FastAPI) をバックグラウンドで起動
# ポート8000で待ち受けます
uv run uvicorn src.backend.main:app --host 127.0.0.1 --port 8000 &

# 2. 少し待機 (バックエンドが立ち上がるのを待つ)
sleep 5

# 3. フロントエンド (Streamlit) をフォアグラウンドで起動
# Cloud Runが指定するポート(8080)で待ち受けます
uv run streamlit run src/frontend/app.py --server.port 8080 --server.address 0.0.0.0