# Use official Python runtime as base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create directories for configuration and memories
RUN mkdir -p /data/memories /root/.letta

# Link environment file to expected location
RUN ln -sf /app/.env /root/.letta/env

# Set environment variables
ENV LETTA_HOST=0.0.0.0
ENV LETTA_PORT=8283
ENV LETTA_MEMORY_DIR=/data/memories

# Expose the application port
EXPOSE 8283

# Run the application with Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8283", "--workers", "4", "--timeout", "120", "letta_server_manager:app"]
