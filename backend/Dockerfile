# Use official GDAL image as base
FROM ghcr.io/osgeo/gdal:ubuntu-full-3.8.0

# Set working directory
WORKDIR /app

# Install Python and pip
RUN apt-get update && apt-get install -y \
    python3-pip \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for uploads and data
RUN mkdir -p uploads data

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Start command - use shell form to allow env var substitution
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
