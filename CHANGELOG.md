# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [3.0.0] - fast scan (master map) + one universal link
    3.2.4 added dự bị bí tích class
    3.2.5 update some student's info đợt 3
    3.2.6 added logic to check in dự trưởng at the evening
    3.2.7 fixed logic to check in dự trưởng at the evening (let them also be checked-in in the morning)
    3.2.8 handle danh sanh bo sung
## [2.0.0] - loop through class + multiple link
## [1.0.0] - set up the system

### Added
- Initial release of QR Code Attendance System
- Google Apps Script integration for web-based QR scanning
- Python modules for QR code generation and image processing
- ID card creation with QR codes and student information
- Time-based attendance logic (early, on-time, late, afternoon)
- Comprehensive configuration system
- Automated setup scripts
- CSV template and data processing
- Background image support for ID cards
- Mobile-responsive web interface
- Real-time attendance feedback
- Google Sheets integration for data storage
- Batch QR code generation from CSV files
- Project documentation and setup guides

### Features
- **QR Generation**: Create unique QR codes for students
- **Card Creation**: Generate professional ID cards with QR codes
- **Web Scanner**: Camera-based QR code scanning interface
- **Smart Timing**: Automatic attendance categorization by time
- **Sheets Integration**: Direct logging to Google Sheets
- **Batch Processing**: Handle multiple students efficiently
- **Configuration**: Flexible settings for different use cases
- **Mobile Support**: Works on smartphones and tablets

### Technical Details
- Python 3.7+ compatibility
- PIL/Pillow for image processing
- html5-qrcode for web scanning
- Google Apps Script for serverless backend
- JSON-based configuration
- Git version control ready
- Virtual environment support

### Documentation
- Comprehensive README with quick start guide
- Installation instructions
- Configuration documentation
- Contributing guidelines
- MIT license
- Example data and templates

## [Unreleased]

### Planned Features
- Database integration (SQLite/PostgreSQL)
- Advanced reporting and analytics
- Multiple language support
- Mobile app for scanning
- Email notifications
- Bulk import/export features
- Integration with other attendance systems
