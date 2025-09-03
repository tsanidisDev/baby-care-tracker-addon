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

# Install build dependencies for numpy/pandas
RUN echo "=== Installing build dependencies ===" && \
    apk add --no-cache gcc g++ musl-dev linux-headers libffi-dev && \
    echo "=== Build dependencies installed ==="

# Copy requirements first for better caching
COPY rootfs/app/requirements.txt .
RUN echo "=== Requirements file copied ===" && \
    cat requirements.txt && \
    echo "=== End of requirements ==="

# Install numpy first to ensure compatibility
RUN echo "=== Installing numpy first for compatibility ===" && \
    pip3 install --no-cache-dir --break-system-packages "numpy>=1.24.0,<2.0.0" && \
    echo "=== numpy installed successfully ==="

# Install pandas next to ensure compatibility with numpy
RUN echo "=== Installing pandas with compatible numpy ===" && \
    pip3 install --no-cache-dir --break-system-packages "pandas>=2.0.0,<2.2.0" && \
    echo "=== pandas installed successfully ==="

# Install remaining Python requirements with error handling and logging
RUN echo "=== Installing remaining Python packages ===" && \
    pip3 --version && \
    python3 --version && \
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt && \
    echo "=== Python packages installed successfully ==="

# Verify numpy and pandas compatibility
RUN echo "=== Verifying numpy and pandas compatibility ===" && \
    python3 -c "import numpy; print('numpy version:', numpy.__version__)" && \
    python3 -c "import pandas; print('pandas version:', pandas.__version__)" && \
    echo "=== numpy and pandas verified successfully ==="

# Remove build dependencies to reduce image size
RUN echo "=== Removing build dependencies ===" && \
    apk del gcc g++ musl-dev linux-headers libffi-dev && \
    echo "=== Build dependencies removed ==="

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
    io.hass.version="1.0.5"

CMD ["/run.sh"]
