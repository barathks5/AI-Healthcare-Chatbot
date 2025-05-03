# Use official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel cython

# Copy requirements first for Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose backend port (Flask = 5050 / FastAPI = 8000)
EXPOSE 5050

# Create a non-root user and switch to it
RUN useradd -m appuser
USER appuser

# Default command to run the app
CMD ["python3", "app.py"]

