ARG BUILD_FROM
FROM $BUILD_FROM

# Install Python and system dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev \
    gcc \
    g++ \
    musl-dev \
    curl \
    jq \
    tzdata

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY rootfs/app/requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

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

# Set labels for Home Assistant
LABEL \
    io.hass.name="Baby Care Tracker" \
    io.hass.description="Complete baby care tracking solution" \
    io.hass.arch="aarch64|amd64|armhf|armv7|i386" \
    io.hass.type="addon" \
    io.hass.version="1.0.0"

CMD ["/run.sh"]
