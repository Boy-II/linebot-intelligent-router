# 使用官方 Python 基礎映像
FROM python:3.9-slim-buster

# 設定工作目錄
WORKDIR /app

# 將 requirements.txt 複製到工作目錄
COPY requirements.txt .

# 安裝所有 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 將應用程式程式碼複製到工作目錄
COPY . .

# 設定環境變數 PORT。Cloud Run 會注入這個變數來告訴容器監聽哪個端口。
# Gunicorn 將會監聽這個端口。
ENV PORT 8080

# 運行 Gunicorn 作為生產級的 WSGI 伺服器
# --bind :$PORT 告訴 Gunicorn 監聽所有網路接口的 $PORT
# --workers 1 每個 worker 都處理一個並發請求
# --threads 8 允許每個 worker 處理多個並發請求
# main:app 告訴 Gunicorn 從 main.py 檔案中找到名為 'app' 的 Flask 應用程式實例
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 main:app