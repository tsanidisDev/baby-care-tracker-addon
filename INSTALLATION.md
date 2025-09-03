# Baby Care Tracker Add-on - Installation Guide

This guide will walk you through installing and configuring the Baby Care Tracker add-on for Home Assistant.

## Prerequisites

Before installing the Baby Care Tracker add-on, ensure you have:

- **Home Assistant** version 2023.1.0 or later
- **Home Assistant Supervisor** (for add-on support)
- At least **500MB** of free storage space
- **MQTT broker** (optional, for device automation)

## Installation Methods

### Method 1: Home Assistant Add-on Store (Recommended)

1. **Open Home Assistant**
   - Navigate to your Home Assistant web interface
   - Go to **Settings** → **Add-ons**

2. **Add Repository**
   - Click the **⋮** menu in the top-right corner
   - Select **Repositories**
   - Add this repository URL:
     ```
     https://github.com/yourusername/baby-care-tracker-addon
     ```
   - Click **Add**

3. **Install the Add-on**
   - Refresh the Add-on Store page
   - Find "Baby Care Tracker" in the available add-ons
   - Click on it and select **Install**
   - Wait for the installation to complete

### Method 2: Manual Installation

1. **Access Home Assistant Files**
   - Use the **File Editor** add-on, **SSH**, or **Samba** to access files
   - Navigate to the `/addons/` directory

2. **Download Add-on Files**
   ```bash
   cd /addons/
   git clone https://github.com/yourusername/baby-care-tracker-addon.git
   ```

3. **Restart Home Assistant**
   - Go to **Settings** → **System** → **Restart**
   - Wait for Home Assistant to fully restart

4. **Install from Local Add-ons**
   - Navigate to **Settings** → **Add-ons**
   - Look for "Baby Care Tracker" under **Local Add-ons**
   - Click **Install**

## Initial Configuration

### Step 1: Basic Configuration

After installation, configure the add-on:

1. **Open Add-on Configuration**
   - Go to **Settings** → **Add-ons** → **Baby Care Tracker**
   - Click on the **Configuration** tab

2. **Basic Settings**
   ```yaml
   # Web interface configuration
   web_interface:
     port: 8099
     ssl: false
   
   # Database settings
   database:
     type: sqlite
     backup_enabled: true
     backup_retention_days: 30
   
   # Basic settings
   baby:
     name: ""
     birth_date: ""
   ```

### Step 2: MQTT Configuration (Optional)

If you want to use device automation:

```yaml
# MQTT broker configuration
mqtt:
  enabled: true
  host: "homeassistant.local"  # Your MQTT broker host
  port: 1883
  username: "your_mqtt_user"
  password: "your_mqtt_password"
  
  # Custom topics (optional)
  custom_topics:
    - "zigbee2mqtt/+/action"
    - "homeassistant/button/+/action"
```

### Step 3: Start the Add-on

1. **Save Configuration**
   - Click **Save** after making changes

2. **Start the Add-on**
   - Go to the **Info** tab
   - Click **Start**
   - Enable **Start on boot** if desired
   - Enable **Watchdog** for automatic restart

3. **Check Logs**
   - Click on the **Log** tab to verify the add-on started successfully
   - Look for messages like:
     ```
     [INFO] Baby Care Tracker starting...
     [INFO] Web server started on port 8099
     [INFO] MQTT client connected
     ```

## Accessing the Web Interface

### Step 1: Open the Interface

1. **Using Add-on Link**
   - In the Baby Care Tracker add-on page
   - Click **Open Web UI**

2. **Direct URL**
   - Navigate to: `http://your-home-assistant-ip:8099`
   - For example: `http://192.168.1.100:8099`

3. **Home Assistant Ingress** (if enabled)
   - Available directly through Home Assistant interface

### Step 2: First Time Setup

1. **Welcome Screen**
   - Enter your baby's name and birth date
   - Select your timezone and language preferences
   - Choose your preferred theme

2. **Device Discovery** (if MQTT enabled)
   - Go to **Devices** page
   - Click **Discover Devices**
   - Configure device mappings as needed

## Setting Up Device Automation

### Supported Devices

The add-on works with various smart home devices:

- **Zigbee Buttons** (via Zigbee2MQTT)
- **Z-Wave Switches** (via Z-Wave JS)
- **WiFi Smart Buttons**
- **Home Assistant Switches/Sensors**

### Example Device Mappings

1. **Xiaomi Wireless Button**
   ```yaml
   Device ID: "0x00158d0001234567"
   Device Name: "Nursery Button"
   Action: "single"
   Baby Care Event: "feeding_start_left"
   ```

2. **Smart Light Switch**
   ```yaml
   Device ID: "light.nursery_switch"
   Device Name: "Nursery Light"
   Action: "on"
   Baby Care Event: "sleep_start"
   ```

### Configuration Steps

1. **Device Discovery**
   - Navigate to **Devices** page in the web interface
   - Click **Discover Devices**
   - Wait for device scan to complete

2. **Map Devices**
   - Click **Map** next to any discovered device
   - Select the baby care action to trigger
   - Choose specific button action (single, double, hold)
   - Add optional notes
   - Click **Save Mapping**

3. **Test Mapping**
   - Click **Test** to verify the mapping works
   - Check the dashboard for the logged event

## Network Configuration

### Firewall Settings

Ensure port 8099 is accessible:

```bash
# UFW (Ubuntu/Debian)
sudo ufw allow 8099

# iptables
sudo iptables -A INPUT -p tcp --dport 8099 -j ACCEPT
```

### Reverse Proxy (Optional)

To access via HTTPS or custom domain:

#### Nginx Configuration
```nginx
server {
    listen 443 ssl;
    server_name babycare.yourdomain.com;
    
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    location / {
        proxy_pass http://localhost:8099;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Backup and Restore

### Automatic Backups

Configure automatic backups in the add-on settings:

```yaml
database:
  backup_enabled: true
  backup_interval: "daily"  # daily, weekly, monthly
  backup_retention_days: 30
```

### Manual Backup

1. **Via Web Interface**
   - Go to **Settings** page
   - Click **Create Backup** under Database Settings
   - Download the backup file

2. **Via Command Line**
   ```bash
   # Access add-on container
   docker exec -it addon_baby_care_tracker /bin/bash
   
   # Create backup
   cp /data/baby_care.db /backup/baby_care_backup_$(date +%Y%m%d).db
   ```

### Restore from Backup

1. **Via Web Interface**
   - Go to **Settings** page
   - Click **Import Data**
   - Select backup file
   - Choose import mode (append or replace)
   - Click **Import Data**

2. **Via Command Line**
   ```bash
   # Stop the add-on first
   # Copy backup file to data directory
   cp /backup/baby_care_backup.db /data/baby_care.db
   # Restart the add-on
   ```

## Integration with Home Assistant

### Creating Sensors

The add-on can automatically create Home Assistant sensors:

```yaml
# In add-on configuration
homeassistant:
  create_entities: true
  publish_events: true
```

This creates sensors like:
- `sensor.baby_feeding_count_today`
- `sensor.baby_sleep_hours_today`
- `sensor.baby_diaper_changes_today`
- `sensor.baby_last_feeding`

### Automation Examples

```yaml
# Feeding reminder automation
automation:
  - alias: "Baby Feeding Reminder"
    trigger:
      - platform: numeric_state
        entity_id: sensor.baby_hours_since_last_feeding
        above: 3
    action:
      - service: notify.mobile_app
        data:
          message: "It's been 3 hours since last feeding"
          title: "Feeding Reminder"

# Sleep notification
automation:
  - alias: "Baby Sleep Notification"
    trigger:
      - platform: state
        entity_id: sensor.baby_sleep_status
        to: "sleeping"
    action:
      - service: notify.family
        data:
          message: "Baby is now sleeping 😴"
```

## Troubleshooting

### Common Issues

1. **Add-on Won't Start**
   ```bash
   # Check logs
   docker logs addon_baby_care_tracker
   
   # Common fixes:
   # - Check port 8099 is not in use
   # - Verify configuration syntax
   # - Ensure sufficient disk space
   ```

2. **MQTT Connection Failed**
   ```bash
   # Test MQTT connection manually
   mosquitto_pub -h localhost -t test/topic -m "test message"
   
   # Check credentials and firewall
   ```

3. **Web Interface Not Loading**
   - Verify Home Assistant can reach port 8099
   - Check browser console for JavaScript errors
   - Try clearing browser cache

4. **Device Discovery Not Working**
   - Ensure MQTT is properly configured
   - Check that devices are paired to your system
   - Verify Zigbee2MQTT or Z-Wave JS is running

### Log Analysis

Enable debug logging:

```yaml
# Add to add-on configuration
log_level: debug
```

Common log patterns to look for:
```
[INFO] Starting Baby Care Tracker...
[INFO] Database initialized successfully
[INFO] MQTT client connected to localhost:1883
[INFO] Web server listening on port 8099
[WARNING] Device 0x123456 not responding
[ERROR] Database connection failed
```

### Getting Help

If you encounter issues:

1. **Check the Logs**
   - Add-on logs in Home Assistant
   - Home Assistant core logs
   - MQTT broker logs

2. **Community Support**
   - [Home Assistant Community Forum](https://community.home-assistant.io/)
   - [GitHub Issues](https://github.com/yourusername/baby-care-tracker-addon/issues)

3. **Debug Information**
   When asking for help, include:
   - Home Assistant version
   - Add-on configuration (remove sensitive data)
   - Relevant log entries
   - Steps to reproduce the issue

## Next Steps

After successful installation:

1. **Configure Devices** - Set up your smart buttons and switches
2. **Customize Dashboard** - Adjust settings and themes
3. **Set Up Notifications** - Configure feeding and diaper reminders
4. **Create Automations** - Integrate with your Home Assistant automations
5. **Export Data** - Set up regular data exports for records

Congratulations! Your Baby Care Tracker add-on is now ready to help you track your baby's care activities. 🍼👶
