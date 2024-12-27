# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /usr/src/app

# Install system dependencies including GDAL and PostGIS client libraries
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    gcc \
    g++ \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Get GDAL version and set it as an environment variable
RUN export GDAL_VERSION=$(gdal-config --version) && \
    export CPLUS_INCLUDE_PATH=/usr/include/gdal && \
    export C_INCLUDE_PATH=/usr/include/gdal

# Copy entrypoint and make executable
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install GDAL==$(gdal-config --version) && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Set the entrypoint
ENTRYPOINT ["./entrypoint.sh"]