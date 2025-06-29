# Gunakan Python slim image
FROM python:3.11-slim

# Install OS dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Salin file requirements dan install dependensi Python
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Salin semua source code ke image
COPY . .

# Jalankan script utama
CMD ["python", "main.py"]
