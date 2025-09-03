#!/usr/bin/with-contenv bashio

# ==============================================================================
# Baby Care Tracker Add-on
# Starts the Baby Care Tracker application
# ==============================================================================

# Set configuration variables
export MQTT_BROKER=$(bashio::config 'mqtt_broker')
export MQTT_USERNAME=$(bashio::config 'mqtt_username')
export MQTT_PASSWORD=$(bashio::config 'mqtt_password')
export DATABASE_TYPE=$(bashio::config 'database_type')
export LOG_LEVEL=$(bashio::config 'log_level')
export ENABLE_ANALYTICS=$(bashio::config 'enable_analytics')
export EXPORT_ENABLED=$(bashio::config 'export_enabled')
export TIMEZONE=$(bashio::config 'timezone')

# Set timezone
if bashio::config.has_value 'timezone'; then
    ln -snf "/usr/share/zoneinfo/$(bashio::config 'timezone')" /etc/localtime
    echo "$(bashio::config 'timezone')" > /etc/timezone
fi

# Create data directory if it doesn't exist
mkdir -p /data/database
mkdir -p /data/exports
mkdir -p /data/logs

# Log configuration
bashio::log.info "Starting Baby Care Tracker..."
bashio::log.info "MQTT Broker: ${MQTT_BROKER}"
bashio::log.info "Database Type: ${DATABASE_TYPE}"
bashio::log.info "Log Level: ${LOG_LEVEL}"
bashio::log.info "Analytics Enabled: ${ENABLE_ANALYTICS}"

# Start the application
cd /app
exec python -u main.py
