# 使用輕量 Python 映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 複製 requirements.txt 進容器
COPY requirements.txt .

# 安裝必要系統套件（gcc, build-essential, libffi 等）
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    build-essential \
    && pip install --upgrade pip \
    && pip install -r requirements.txt \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製專案所有檔案進容器
COPY . .

# 設定環境變數（防止 Python 緩存 .pyc 檔案）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 對外開放 port（Railway 用）
EXPOSE 5000

# 啟動 app.py（確保 Flask app 在 app.py）
CMD ["python", "app.py"]
