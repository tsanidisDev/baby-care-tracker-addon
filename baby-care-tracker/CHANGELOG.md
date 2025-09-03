# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2025-09-04

### Fixed
- Dashboard analytics cards showing 0 values on page refresh
- Missing updateDashboard() function causing JavaScript errors
- Template variable errors on settings and devices pages
- Analytics cards not loading fresh data when dashboard is refreshed

### Added
- New /api/daily-stats endpoint for real-time statistics refresh
- Automatic dashboard statistics loading on page initialization
- updateDashboard() and refreshDashboardStats() JavaScript functions
- Real-time stats updates when new events are received via WebSocket
- Enhanced error handling for analytics data fetching

### Changed
- Dashboard now fetches fresh statistics from server on every page load
- Improved WebSocket event handling for real-time dashboard updates
- Enhanced JavaScript error handling and logging

## [1.0.4] - 2025-09-04

### Fixed
- Python package installation in Alpine Linux environment
- SSL compatibility issue with Python 3.12 by replacing eventlet with gevent
- pip installation process with proper --break-system-packages flag handling
- SocketIO async mode configuration for better performance

### Changed
- Replaced eventlet with gevent for better Python 3.12 compatibility
- Enhanced pip installation with fallback mechanisms
- Improved error handling in package installation process

## [1.0.3] - 2025-09-04

### Added
- Comprehensive logging for debugging installation issues
- Enhanced error handling throughout the application
- Detailed build progress tracking in Dockerfile
- Configuration validation and debugging output

### Fixed
- numpy/pandas binary compatibility issue preventing startup
- Docker build process with proper dependency installation
- Staging of build dependencies for Alpine Linux environment

### Changed
- Improved startup script with detailed system information logging
- Enhanced Python application initialization with step-by-step tracking
- Better configuration loading with environment variable display

## [1.0.2] - 2025-09-04

### Fixed
- numpy/pandas binary compatibility error
- Docker build dependencies for scientific packages
- Proper staging of numpy installation before pandas

### Added
- Build-time verification of numpy/pandas compatibility
- Enhanced Docker build logging

## [1.0.1] - 2025-09-04

### Added
- Initial comprehensive logging system
- Enhanced debugging capabilities
- Detailed startup process tracking

## [1.0.0] - 2024-09-04

### Added
- Initial release of Baby Care Tracker add-on
- Baby care event tracking (feeding, sleep, diaper changes)
- Real-time dashboard with analytics
- MQTT device integration support
- Data persistence with SQLite
- Web interface for easy access
- Device automation mapping
- Data export functionality
