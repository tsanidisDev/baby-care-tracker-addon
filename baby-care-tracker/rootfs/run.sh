#!/usr/bin/with-contenv bashio

# ==============================================================================
# Baby Care Tracker Add-on
# Starts the Baby Care Tracker application
# ==============================================================================

set -e

echo "=== Baby Care Tracker Add-on Starting ==="
echo "Date: $(date)"
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Available memory: $(free -h | head -2)"
echo "Disk space: $(df -h / | tail -1)"

# Show configuration
echo "=== Configuration ==="
bashio::log.info "Checking add-on configuration..."

# Set configuration variables with defaults
export MQTT_BROKER=$(bashio::config 'mqtt_broker' 'localhost')
export MQTT_USERNAME=$(bashio::config 'mqtt_username' '')
export MQTT_PASSWORD=$(bashio::config 'mqtt_password' '')
export DATABASE_TYPE=$(bashio::config 'database_type' 'sqlite')
export LOG_LEVEL=$(bashio::config 'log_level' 'info')
export ENABLE_ANALYTICS=$(bashio::config 'enable_analytics' 'true')
export EXPORT_ENABLED=$(bashio::config 'export_enabled' 'true')
export TIMEZONE=$(bashio::config 'timezone' 'UTC')

echo "MQTT Broker: $MQTT_BROKER"
echo "MQTT Username: $MQTT_USERNAME"
echo "Database Type: $DATABASE_TYPE"
echo "Log Level: $LOG_LEVEL"
echo "Analytics Enabled: $ENABLE_ANALYTICS"
echo "Export Enabled: $EXPORT_ENABLED"
echo "Timezone: $TIMEZONE"

# Set timezone
echo "=== Setting Timezone ==="
if bashio::config.has_value 'timezone'; then
    ln -snf "/usr/share/zoneinfo/$(bashio::config 'timezone')" /etc/localtime
    echo "$(bashio::config 'timezone')" > /etc/timezone
    echo "Timezone set to: $(bashio::config 'timezone')"
fi

# Create data directory if it doesn't exist
echo "=== Creating Data Directories ==="
mkdir -p /data/database
mkdir -p /data/exports
mkdir -p /data/logs
echo "Data directories created:"
ls -la /data/

# Check application files
echo "=== Application Files Check ==="
echo "Contents of /app:"
ls -la /app/ || echo "ERROR: /app directory not found"

echo "Python files in /app:"
find /app -name "*.py" -type f | head -10 || echo "No Python files found"

echo "requirements.txt contents:"
cat /app/requirements.txt || echo "ERROR: requirements.txt not found"

# Check Python installation
echo "=== Python Environment ==="
python3 --version || echo "ERROR: Python3 not available"
pip3 --version || echo "ERROR: pip3 not available"

# Install dependencies
echo "=== Installing Python Dependencies ==="
cd /app
echo "Current directory: $(pwd)"

if [ -f requirements.txt ]; then
    echo "Installing requirements..."
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt || {
        echo "ERROR: Failed to install requirements with --break-system-packages"
        echo "Attempting installation without flag..."
        pip3 install --no-cache-dir -r requirements.txt || {
            echo "ERROR: Failed to install requirements"
            echo "Attempting alternative installation..."
            cat requirements.txt | while read requirement; do
                if [ ! -z "$requirement" ] && [ "${requirement:0:1}" != "#" ]; then
                    echo "Installing: $requirement"
                    pip3 install --no-cache-dir --break-system-packages "$requirement" || echo "Failed to install: $requirement"
                fi
            done
        }
    }
else
    echo "ERROR: requirements.txt not found in /app"
    exit 1
fi

# Verify installations
echo "=== Verifying Installations ==="
python3 -c "import flask; print('Flask version:', flask.__version__)" || echo "Flask not available"
python3 -c "import sqlalchemy; print('SQLAlchemy version:', sqlalchemy.__version__)" || echo "SQLAlchemy not available"
python3 -c "import paho.mqtt.client; print('MQTT client available')" || echo "MQTT client not available"

# Log configuration
echo "=== Final Configuration Log ==="
bashio::log.info "Starting Baby Care Tracker..."
bashio::log.info "MQTT Broker: ${MQTT_BROKER}"
bashio::log.info "Database Type: ${DATABASE_TYPE}"
bashio::log.info "Log Level: ${LOG_LEVEL}"
bashio::log.info "Analytics Enabled: ${ENABLE_ANALYTICS}"

# Start the application
echo "=== Starting Baby Care Tracker Application ==="
bashio::log.info "Starting Baby Care Tracker on port 8099..."
echo "Executing: python3 -u main.py"

cd /app
exec python3 -u main.py
