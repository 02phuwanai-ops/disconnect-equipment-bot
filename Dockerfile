FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY . /app

# ติดตั้ง Python packages และบังคับลง playwright เวอร์ชัน 1.40.0 ให้ตรงกับ Base Image
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install playwright==1.40.0

# ติดตั้งเบราว์เซอร์ของ Playwright ลงใน Container
RUN playwright install chromium

EXPOSE 5000

CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:5000", "--timeout", "120"]