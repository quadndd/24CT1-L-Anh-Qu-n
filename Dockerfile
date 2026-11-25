# ---- Dockerfile ------------------------------------------------
FROM python:3.12-slim

# Cài các phụ thuộc hệ thống
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Cài pip và các phụ thuộc Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn
COPY . .

# Thu thập static files
RUN python manage.py collectstatic --noinput

# Chạy migrate, tạo dữ liệu mẫu (các dòng xe + tài khoản admin 123456) rồi khởi động Gunicorn
CMD python manage.py migrate && python manage.py tao_du_lieu_mau && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:$PORT du_an_ban_xe.wsgi:application
