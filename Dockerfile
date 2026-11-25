# ---- Dockerfile ------------------------------------------------
FROM python:3.12-slim

# Cài các phụ thuộc hệ thống cần thiết
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài pip và các phụ thuộc Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Thu thập static files
RUN python manage.py collectstatic --noinput

# Lệnh chạy Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "du_an_ban_xe.wsgi:application"]
