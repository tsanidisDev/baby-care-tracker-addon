# Baby Care Tracker Add-on

A comprehensive Home Assistant add-on for tracking baby care activities including feeding, sleep, and diaper changes with device automation support.

## About

This add-on provides a complete baby care tracking solution that integrates seamlessly with Home Assistant. Track feeding sessions, sleep patterns, and diaper changes with real-time analytics and device automation support.

## Installation

Add this repository to your Home Assistant add-on store:

```
https://github.com/tsanidisDev/baby-care-tracker-addon
```

For detailed installation instructions, see [INSTALLATION.md](../INSTALLATION.md).

## Features

- **Real-time Tracking**: Log feeding, sleep, and diaper events
- **Device Automation**: Map smart buttons and switches to baby care actions
- **Analytics Dashboard**: View patterns and statistics
- **MQTT Integration**: Full support for Zigbee2MQTT and Z-Wave JS
- **Data Persistence**: SQLite database with backup support
- **Mobile Optimized**: Responsive web interface

## Quick Start

1. Install the add-on from the Home Assistant add-on store
2. Configure your settings in the add-on configuration tab
3. Start the add-on
4. Access the web interface on port 8099
5. Begin tracking your baby's care activities

## Updates

The Baby Care Tracker add-on supports automatic updates through Home Assistant.

### Updating the Add-on

1. Navigate to **Supervisor** → **Add-ons** → **Baby Care Tracker**
2. If an update is available, click the **Update** button
3. Your data and configuration will be preserved automatically
4. The add-on will restart with the new version

### Version Information

- Check `/api/version` endpoint for current version information
- View the [Changelog](CHANGELOG.md) for detailed release notes
- See [Update Guide](UPDATE_GUIDE.md) for troubleshooting

### Data Safety

All your tracking data is safely preserved during updates:
- ✅ Database files remain intact
- ✅ Configuration settings are maintained  
- ✅ MQTT mappings are preserved
- ✅ Analytics history is retained

## Support

- [Documentation](../README.md)
- [Installation Guide](../INSTALLATION.md)
- [Update Guide](UPDATE_GUIDE.md)
- [GitHub Issues](https://github.com/tsanidisDev/baby-care-tracker-addon/issues)

---
**Made with ❤️ for parents and caregivers**
