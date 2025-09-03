# Update Guide

This guide explains how to update the Baby Care Tracker add-on and what to expect during updates.

## Automatic Updates

The Baby Care Tracker add-on supports automatic updates through Home Assistant's Supervisor.

### Checking for Updates

1. Navigate to **Supervisor** → **Add-on Store**
2. Find "Baby Care Tracker" in your installed add-ons
3. If an update is available, you'll see an "Update" button
4. Click "Update" to install the latest version

### Update Process

During an update:
1. The add-on will be stopped
2. The new container image will be downloaded
3. Your configuration and data will be preserved
4. The add-on will restart with the new version

## Data Preservation

Your data is safe during updates:
- **Database**: Stored in `/data/database/` (persisted across updates)
- **Configuration**: Your add-on settings are maintained
- **Logs**: Previous logs are preserved in `/data/logs/`
- **Exports**: Any exported data remains in `/data/exports/`

## Manual Update Steps

If automatic updates fail, you can manually update:

1. **Backup your data** (recommended):
   - Export your tracking data from the web interface
   - Note your current configuration settings

2. **Uninstall the old version**:
   - Go to Supervisor → Add-ons → Baby Care Tracker
   - Click "Uninstall"

3. **Reinstall the latest version**:
   - Add the repository again if needed
   - Install the latest version
   - Restore your configuration

## Version Compatibility

- **1.0.x**: All patch versions are backward compatible
- **Database migrations**: Handled automatically on startup
- **Configuration**: New options get default values

## Troubleshooting Updates

If you encounter issues during updates:

1. **Check the logs**: Supervisor → Add-ons → Baby Care Tracker → Logs
2. **Restart the add-on**: Sometimes a restart resolves update issues
3. **Check storage space**: Ensure sufficient disk space for the new image
4. **Manual reinstall**: As a last resort, manually reinstall the add-on

## Post-Update Checklist

After updating:
1. ✅ Verify the add-on starts successfully
2. ✅ Check the web interface loads correctly
3. ✅ Confirm your data is still accessible
4. ✅ Test MQTT connectivity if configured
5. ✅ Review any new configuration options

## Release Notifications

Stay informed about updates:
- Check the [Changelog](CHANGELOG.md) for detailed release notes
- Monitor the GitHub repository for announcements
- Enable Home Assistant notifications for add-on updates
