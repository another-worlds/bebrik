FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    LOG_LEVEL=INFO

# Install system dependencies required for document processing
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libmagic1 \
    libmagic-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with proper permissions
RUN mkdir -p uploads && \
    chmod 755 uploads

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app && \
    chmod -R 775 /app/uploads

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Health check - using python instead of curl for better reliability
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python health_check.py || exit 1

# Add labels for better container management
LABEL maintainer="telegram-bot-team" \
      version="1.0.0" \
      description="Telegram Multi-Agent AI Bot with document processing"

# Run the application
CMD ["python", "main.py"]
