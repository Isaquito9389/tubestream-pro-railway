# ============================================================
# TubeStream Pro — Dockerfile pour Railway / Render
# ============================================================
FROM python:3.11-slim

# Install system dependencies + ffmpeg for audio extraction
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories
RUN mkdir -p templates downloads

# Set environment variables
ENV PORT=5000
ENV DOWNLOAD_DIR=/app/downloads
ENV FLASK_DEBUG=false

# Expose port
EXPOSE $PORT

# Run application
CMD gunicorn web_app:app \
    --bind 0.0.0.0:$PORT \
    --timeout 300 \
    --workers 4 \
    --threads 2 \
    --keep-alive 120 \
    --access-logfile - \
    --error-logfile -
