# Gunakan base image Python
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy file ke dalam container
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Perintah untuk menjalankan bot
CMD ["python", "bot.py"]
