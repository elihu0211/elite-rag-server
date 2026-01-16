# ============================================================
# Elite RAG Server - Multi-stage Dockerfile
# Python 3.14 + uv + sentence-transformers
# ============================================================

# Stage 1: Build stage
FROM python:3.14-slim AS builder

# 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# 複製依賴文件
COPY pyproject.toml uv.lock ./

# 創建虛擬環境並安裝依賴
# UV_LINK_MODE=copy 確保複製而非 symlink（跨階段需要）
ENV UV_LINK_MODE=copy
RUN uv venv /app/.venv && \
    . /app/.venv/bin/activate && \
    uv sync --frozen --no-dev --no-editable

# Stage 2: Runtime stage
FROM python:3.14-slim AS runtime

# 設定環境變數
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    TRANSFORMERS_CACHE=/app/models \
    HF_HOME=/app/models

# 建立非 root 用戶
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# 從 builder 複製虛擬環境
COPY --from=builder /app/.venv /app/.venv

# 複製應用程式原始碼
COPY --chown=appuser:appgroup src/ ./src/

# 建立資料和模型目錄
RUN mkdir -p /app/data /app/models && \
    chown -R appuser:appgroup /app/data /app/models

# 預載入嵌入模型（減少首次啟動時間）
RUN . /app/.venv/bin/activate && \
    python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" && \
    chown -R appuser:appgroup /app/models

# 切換到非 root 用戶
USER appuser

# 暴露端口
EXPOSE 8000

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/graphql')" || exit 1

# 啟動命令
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
