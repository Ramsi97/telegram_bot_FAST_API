# Use a stable Python image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    ghostscript \
    tesseract-ocr \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy your project files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 10000

# Run app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]
