# Baby Care Tracker Add-on

A comprehensive3. Add this repository URL: `https://github.com/tsanidisDev/baby-care-tracker-addon`Home Assistant add-on for tracking baby care activities including feeding, sleep, and diaper changes with device automation support.

## Features

### 📊 Comprehensive Tracking
- **Feeding Sessions**: Track breastfeeding (left/right breast), bottle feeding, and duration
- **Sleep Monitoring**: Record sleep start/end times with duration analysis
- **Diaper Changes**: Log wet, dirty, or combined diaper changes
- **Real-time Dashboard**: Live updates and statistics

### 🏠 Home Assistant Integration
- **Device Automation**: Map Zigbee buttons, switches, and sensors to baby care actions
- **MQTT Support**: Full integration with Zigbee2MQTT, Z-Wave JS, and Home Assistant
- **Entity Creation**: Automatic sensor creation for feeding, sleep, and diaper statistics
- **Event Publishing**: Send events to Home Assistant for further automation

### 📱 Modern Web Interface
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Real-time Updates**: WebSocket connection for live data synchronization
- **Dark/Light Theme**: Automatic theme switching based on system preferences
- **Touch-friendly**: Optimized for quick logging on mobile devices

### 📈 Analytics & Reports
- **Daily Statistics**: Track feeding frequency, sleep duration, and diaper changes
- **Visual Charts**: Interactive graphs showing patterns and trends
- **Data Export**: Export data as CSV, JSON, or PDF reports
- **Pattern Analysis**: Identify feeding and sleep patterns over time

### 🔧 Advanced Features
- **Database Persistence**: SQLite or PostgreSQL support for reliable data storage
- **Automatic Backups**: Scheduled database backups with retention policies
- **Multi-language Support**: Interface available in multiple languages
- **Notification System**: Feeding reminders and milestone notifications

## Installation

### Via Home Assistant Add-on Store (Recommended)

1. Open Home Assistant
2. Navigate to **Supervisor** → **Add-on Store**
3. Click the **⋮** menu and select **Repositories**
4. Add this repository URL: `https://github.com/yourusername/baby-care-tracker-addon`
5. Find "Baby Care Tracker" in the add-on store
6. Click **Install**

### Manual Installation

1. Copy the `baby-care-tracker-addon` folder to your Home Assistant add-ons directory:
   ```
   /addons/baby-care-tracker-addon/
   ```

2. Restart Home Assistant

3. Navigate to **Supervisor** → **Add-on Store** → **Local Add-ons**

4. Find "Baby Care Tracker" and click **Install**

## Configuration

### Basic Setup

```yaml
# Example configuration
mqtt:
  enabled: true
  host: "homeassistant.local"
  port: 1883
  username: "mqtt_user"
  password: "mqtt_password"

database:
  type: "sqlite"  # or "postgresql"
  backup_enabled: true
  backup_retention_days: 30

web_interface:
  port: 8099
  ssl: false

notifications:
  enabled: true
  feeding_reminder_hours: 3
  diaper_reminder_hours: 4
```

### MQTT Configuration

The add-on supports multiple MQTT integrations:

- **Zigbee2MQTT**: Automatic discovery of Zigbee devices
- **Z-Wave JS**: Integration with Z-Wave devices via MQTT
- **Home Assistant MQTT**: Direct integration with HA's MQTT broker

### Device Mapping

1. Navigate to the **Devices** page in the web interface
2. Click **Discover Devices** to scan for available devices
3. Map device actions to baby care events:
   - Button presses → Feeding start/end
   - Switch states → Sleep tracking
   - Sensor triggers → Diaper reminders

## Usage

### Quick Actions

Use the dashboard quick action buttons or map them to physical devices:

- **Left Breast**: Start feeding session (left breast)
- **Right Breast**: Start feeding session (right breast)
- **Sleep Start**: Begin sleep tracking
- **Diaper Change**: Record diaper change

### Device Automation Examples

```yaml
# Xiaomi Button → Left Breast Feeding
Device: "0x00158d0001234567"
Action: "single"
Baby Care Action: "feeding_start_left"

# Smart Switch → Sleep Toggle
Device: "bedroom_switch"
Action: "on"
Baby Care Action: "sleep_start"
```

### Analytics

- View daily, weekly, and monthly statistics
- Export data for pediatrician visits
- Track feeding patterns and sleep schedules
- Monitor growth milestones

## API Endpoints

The add-on provides a REST API for integration:

```bash
# Log a feeding event
POST /api/events
{
  "type": "feeding_start_left",
  "notes": "Good latch",
  "device_source": "button_01"
}

# Get daily statistics
GET /api/analytics/daily?date=2024-01-15

# Export data
GET /api/export?format=csv&start_date=2024-01-01&end_date=2024-01-31
```

## Database Schema

The add-on uses a simple but comprehensive database schema:

### Events Table
- `id`: Unique identifier
- `timestamp`: Event timestamp
- `event_type`: Type of event (feeding_start_left, sleep_start, etc.)
- `duration`: Duration in minutes (for completed events)
- `notes`: Optional notes
- `device_source`: Source device identifier

### Device Mappings Table
- `device_id`: Home Assistant device identifier
- `device_name`: Friendly device name
- `baby_care_action`: Mapped baby care action
- `button_action`: Specific button action (single, double, hold)
- `notes`: Configuration notes

## Troubleshooting

### Common Issues

1. **WebSocket Connection Failed**
   - Check firewall settings
   - Ensure port 8099 is accessible
   - Verify Home Assistant network configuration

2. **MQTT Devices Not Discovered**
   - Verify MQTT broker configuration
   - Check MQTT username/password
   - Ensure Zigbee2MQTT is running

3. **Database Connection Error**
   - Check database permissions
   - Verify storage space
   - Review add-on logs

### Log Files

Access logs via Home Assistant:
- Supervisor → Baby Care Tracker → Logs

Or via command line:
```bash
docker logs addon_baby_care_tracker
```

## Development

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/baby-care-tracker-addon
   cd baby-care-tracker-addon
   ```

2. Build the Docker container:
   ```bash
   docker build -t baby-care-tracker .
   ```

3. Run locally:
   ```bash
   docker run -p 8099:8099 baby-care-tracker
   ```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

- **Documentation**: [Wiki](https://github.com/tsanidisDev/baby-care-tracker-addon/wiki)
- **Issues**: [GitHub Issues](https://github.com/tsanidisDev/baby-care-tracker-addon/issues)
- **Discussions**: [GitHub Discussions](https://github.com/tsanidisDev/baby-care-tracker-addon/discussions)
- **Home Assistant Community**: [Community Forum](https://community.home-assistant.io/)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0 (Initial Release)
- Complete rewrite as Home Assistant add-on
- Full MQTT integration with device discovery
- Modern web interface with real-time updates
- Comprehensive analytics and reporting
- Database persistence with backup support
- Multi-language interface
- Mobile-optimized design

### Previous Versions
- v0.1.0-v1.2.0: Custom component releases (deprecated)

## Acknowledgments

- Home Assistant community for inspiration and support
- Bootstrap and Chart.js for UI components
- SQLAlchemy for database management
- Flask and Socket.IO for web framework

---

**Made with ❤️ for parents and caregivers**
