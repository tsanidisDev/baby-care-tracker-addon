ARG BUILD_FROM
FROM $BUILD_FROM

# Add build logging
RUN echo "=== Starting Baby Care Tracker build ===" && \
    echo "Build from: $BUILD_FROM" && \
    echo "Architecture: $(uname -m)"

# Install Python and basic dependencies
RUN echo "=== Installing system packages ===" && \
    apk add --no-cache \
    python3 \
    py3-pip \
    curl && \
    echo "=== System packages installed successfully ==="

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY rootfs/app/requirements.txt .
RUN echo "=== Requirements file copied ===" && \
    cat requirements.txt && \
    echo "=== End of requirements ==="

# Install Python requirements with error handling and logging
RUN echo "=== Installing Python packages ===" && \
    pip3 --version && \
    python3 --version && \
    (pip3 install --no-cache-dir --break-system-packages -r requirements.txt || \
     pip3 install --no-cache-dir -r requirements.txt) && \
    echo "=== Python packages installed successfully ==="

# Copy application files
COPY rootfs/ /
RUN echo "=== Application files copied ===" && \
    ls -la / && \
    echo "=== /app directory contents ===" && \
    ls -la /app

# Make run script executable
RUN chmod a+x /run.sh && \
    echo "=== run.sh made executable ===" && \
    ls -la /run.sh

# Create data directory
RUN mkdir -p /data && \
    echo "=== Data directory created ===" && \
    ls -la /data

# Show final structure
RUN echo "=== Final container structure ===" && \
    find /app -type f -name "*.py" | head -10 && \
    echo "=== Build completed successfully ==="

# Expose port
EXPOSE 8099

# Set labels for Home Assistant
LABEL \
    io.hass.name="Baby Care Tracker" \
    io.hass.description="Complete baby care tracking solution" \
    io.hass.arch="aarch64|amd64|armhf|armv7|i386" \
    io.hass.type="addon" \
    io.hass.version="1.0.1"

CMD ["/run.sh"]
