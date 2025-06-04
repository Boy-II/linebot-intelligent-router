# Zeabur 生產版本 Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# 複製並安裝 Python 依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製 Python 文件
COPY main.py .
COPY models.py .
COPY user_manager.py .
COPY dialogflow_client.py .
COPY google_credentials.py .

# 複製啟動腳本
COPY start.sh .
RUN chmod +x start.sh

# 創建憑證目錄（但不複製實際憑證檔案）
RUN mkdir -p /app/credentials

# 設定環境變數
ENV PYTHONUNBUFFERED=1

# 創建用戶
RUN useradd -m app && chown -R app:app /app
USER app

# 暴露端口
EXPOSE 8080

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# 使用啟動腳本
CMD ["./start.sh"]
