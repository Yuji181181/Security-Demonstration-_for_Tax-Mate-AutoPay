# ベースイメージ
FROM python:3.11-slim

# uvのインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 作業ディレクトリ
WORKDIR /app

# 依存関係のインストール
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# パスの設定
ENV PATH="/app/.venv/bin:$PATH"

# ソースコードと起動スクリプトをコピー
COPY . .

# 起動スクリプトに実行権限を付与
RUN chmod +x start.sh

# Cloud Runの設定
ENV PORT=8080

# 【変更点】Streamlit直接起動ではなく、スクリプト経由で両方起動する
CMD ["./start.sh"]