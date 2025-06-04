# 使用官方的 Python runtime 作為基礎映像
FROM python:3.9-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements 文件
COPY requirements_optimized.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements_optimized.txt

# 複製應用程式代碼
COPY main_optimized.py .
COPY dialogflow_client.py .

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=main_optimized.py

# 暴露端口
EXPOSE 8080

# 設定啟動命令
CMD exec gunicorn --bind :8080 --workers 1 --threads 8 --timeout 0 main_optimized:app
