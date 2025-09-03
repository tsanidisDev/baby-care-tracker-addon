# Baby Care Tracker Add-on Documentation

## About

The Baby Care Tracker add-on provides a comprehensive solution for tracking baby care activities including feeding, sleep, and diaper changes. It features real-time analytics, device automation support, and persistent data storage.

## Installation

1. Add this repository to your Home Assistant add-on store
2. Install the "Baby Care Tracker" add-on
3. Configure your settings
4. Start the add-on

## Configuration

The add-on can be configured via the Home Assistant add-on configuration interface:

### MQTT Settings
- **mqtt_broker**: MQTT broker hostname (default: "core-mosquitto")
- **mqtt_username**: MQTT username (optional)
- **mqtt_password**: MQTT password (optional)

### Database Settings
- **database_type**: Database type - "sqlite" or "postgresql" (default: "sqlite")

### General Settings
- **log_level**: Log level for debugging (default: "info")
- **enable_analytics**: Enable analytics features (default: true)
- **export_enabled**: Enable data export features (default: true)
- **timezone**: Timezone for timestamps (default: "UTC")

## Usage

After starting the add-on:

1. Access the web interface via the "Open Web UI" button
2. Configure your baby's details and preferences
3. Set up device mappings for automation (optional)
4. Begin tracking feeding, sleep, and diaper events

## Features

- **Real-time Dashboard**: Track events as they happen
- **Device Automation**: Map smart buttons and switches to baby care actions
- **Analytics**: View feeding patterns, sleep statistics, and diaper change frequency
- **Data Export**: Export data for pediatrician visits or personal records
- **MQTT Integration**: Full support for Zigbee2MQTT and Z-Wave JS devices

## Support

For issues and feature requests, please visit the [GitHub repository](https://github.com/tsanidisDev/baby-care-tracker-addon).
