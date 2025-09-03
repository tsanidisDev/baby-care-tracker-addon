FROM python:3.11-slim

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        g++ \
        libc6-dev \
        curl \
        jq \
        tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY rootfs/app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY rootfs/ /

# Make run script executable
RUN chmod a+x /run.sh

# Create data directory
RUN mkdir -p /data

# Expose port
EXPOSE 8099

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8099/health || exit 1

CMD ["/run.sh"]
