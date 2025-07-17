# ใช้ base image จาก Python
FROM python:3.11

# ตั้ง working directory
WORKDIR /app

# คัดลอกไฟล์ requirements.txt ไปใน container
COPY requirements.txt .

# ติดตั้ง dependencies
RUN pip install --no-cache-dir -r requirements.txt

# คัดลอกโปรเจกต์ Django ทั้งหมดไปใน container
COPY . .

# เปิดพอร์ต 8000
EXPOSE 8000

# คำสั่งรันเซิร์ฟเวอร์
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
