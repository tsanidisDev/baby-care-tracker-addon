# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
