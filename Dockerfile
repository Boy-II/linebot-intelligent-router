# 使用官方的 Python runtime 作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements 文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 創建數據目錄結構
RUN mkdir -p /app/data/users \
    && mkdir -p /app/data/backups \
    && mkdir -p /app/data/logs \
    && chmod -R 755 /app/data

# 複製應用程式代碼
COPY main.py .
COPY user_manager.py .

# 複製 Dialogflow 客戶端（如果存在）
COPY dialogflow_client.py . 2>/dev/null || echo "No dialogflow_client.py found"

# 複製初始數據文件（如果存在）
COPY data/users/users.json /app/data/users/users.json 2>/dev/null || echo "No initial users.json found"

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main.py
ENV DATA_DIR=/app/data
ENV PYTHONPATH=/app

# 創建非root用戶
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 設定啟動命令
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main:app
