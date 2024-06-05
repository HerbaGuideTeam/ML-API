# Gunakan official Python runtime sebagai parent image
FROM python:3.12

# Set working directory di dalam container
WORKDIR /app

# Copy requirements.txt dan install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file dari local directory ke working directory di dalam container
COPY . .

# Expose port yang digunakan oleh aplikasi
EXPOSE 8000

# Set environment variable
ENV PYTHONUNBUFFERED=1

# Jalankan aplikasi menggunakan uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
