# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.8] - 2025-09-04

### Fixed
- Analytics page template error "No filter named 'tojsonfilter'"
- Missing chart_data variable passed to analytics template
- Jinja2 template filter registration for JSON serialization

### Added
- Custom Jinja2 filter 'tojsonfilter' for converting Python objects to JSON in templates
- Proper chart_data object passed to analytics template for frontend chart rendering
- Enhanced JSON serialization with default string conversion for datetime objects

### Changed
- Analytics template now receives properly formatted chart data
- Improved template error handling and data preparation
- Version updated to 1.0.8

## [1.0.7] - 2025-09-04

### Fixed
- Analytics page crashing due to missing error handling
- Settings page failing to load with proper error isolation
- Device page not showing devices due to unhandled exceptions
- Critical startup failures not being properly logged

### Added
- Comprehensive error logging throughout application startup
- Individual component initialization with graceful failure handling
- Enhanced API endpoint error logging with stack traces
- Detailed component availability checks in all page routes
- Debug information in API responses for troubleshooting

### Changed
- Application continues to run even if individual components fail to initialize
- All page routes now have fallback data when components are unavailable
- Enhanced logging shows exactly which components succeed/fail during startup
- API endpoints now check component availability before attempting operations
- Better error isolation prevents single component failures from crashing entire app

### Security
- Added proper error message sanitization to prevent information leakage

## [1.0.6] - 2025-09-04

### Fixed
- JavaScript error "eventType.replace(...).title is not a function" when logging events
- Missing /api/devices/discover endpoint causing device discovery failures
- Dashboard stats not refreshing automatically on page load
- Template refreshDashboard() function using page reload instead of API calls

### Added
- Manual refresh button in dashboard Quick Actions section
- Automatic dashboard stats refresh on page load
- Debug information in /api/daily-stats endpoint for troubleshooting
- Missing device discovery API endpoint for MQTT device scanning

### Changed
- Improved event type display formatting with proper title case conversion
- Dashboard refresh now uses API calls instead of full page reload
- Enhanced error handling and logging for device discovery
- Better user feedback for manual dashboard refresh operations

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
