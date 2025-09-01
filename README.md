# QR Code Attendance System

A comprehensive attendance tracking system that combines QR code generation, scanning, and Google Sheets integration for efficient attendance management.

## 🌟 Features

- **QR Code Generation**: Generate unique QR codes for each student from CSV data
- **ID Card Creation**: Create professional ID cards with QR codes and student information
- **Real-time Scanning**: Web-based QR code scanner with camera integration
- **Google Sheets Integration**: Automatic attendance logging to Google Sheets
- **Time-based Logic**: Smart attendance marking based on arrival time
- **Responsive Web Interface**: Mobile-friendly scanner interface
- **Batch Processing**: Generate QR codes for entire groups at once

## 📋 Prerequisites

- Python 3.7 or higher
- Google Account with Google Sheets and Google Apps Script access
- Modern web browser with camera support
- pip (Python package installer)

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/yourusername/qr-attendance-system.git
cd qr-attendance-system
```

### 2. Run Setup Script

```bash
python scripts/setup.py
```

This will:
- Create a Python virtual environment
- Install required dependencies
- Initialize Git repository
- Set up configuration files

### 3. Configure Google Sheets

1. Create a new Google Sheets document
2. Copy the spreadsheet ID from the URL
3. Update `config/gas_config.json` with your spreadsheet ID
4. Create sheets as needed (Master, attendance sheets)

### 4. Deploy Google Apps Script

1. Go to [Google Apps Script](https://script.google.com)
2. Create a new project
3. Copy the contents of `src/google_apps_script/Code.gs` to the script editor
4. Create an HTML file named "Index" and copy `src/google_apps_script/Index.html`
5. Deploy as a web app

### 5. Generate QR Codes

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Generate QR codes from CSV
python scripts/generate_qr_codes.py data/csv_files/your_students.csv --create-cards
```

## 📁 Project Structure

```
qr-attendance-system/
├── config/                    # Configuration files
│   ├── settings.json         # Application settings
│   └── gas_config.json       # Google Apps Script configuration
├── src/                      # Source code
│   ├── google_apps_script/   # Google Apps Script files
│   ├── qr_generation/        # QR code generation modules
│   └── image_processing/     # Image processing utilities
├── data/                     # Data files
│   ├── csv_files/           # Student data CSV files
│   └── templates/           # CSV templates
├── assets/                   # Static assets
│   ├── backgrounds/         # Background images for ID cards
│   ├── qr_codes/           # Generated QR codes
│   └── id_cards/           # Generated ID cards
├── output/                   # Generated files and reports
├── scripts/                  # Utility scripts
└── examples/                 # Example files and documentation
```

## 📊 CSV Data Format

Your student data CSV should follow this format:

```csv
ID,Saint Name,First Name,Last Name,Group
1,Maria,Anna,Smith,Group A
2,Joseph,John,Doe,Group A
3,Peter,Michael,Johnson,Group B
```

See `data/templates/students_template.csv` for a complete example.

## ⚙️ Configuration

### Application Settings (`config/settings.json`)
- QR code generation parameters
- Image processing settings
- Font and layout configurations
- File paths and directories

### Google Apps Script Settings (`config/gas_config.json`)
- Spreadsheet ID and sheet names
- Time-based attendance rules
- Status codes and behavior

## 🎯 Usage Examples

### Generate QR Codes Only
```bash
python scripts/generate_qr_codes.py data/csv_files/group1.csv
```

### Generate QR Codes with ID Cards
```bash
python scripts/generate_qr_codes.py data/csv_files/group1.csv --create-cards
```

### Custom Output Directory
```bash
python scripts/generate_qr_codes.py data/csv_files/group1.csv --output-dir custom_output
```

## 📱 Attendance Scanning

1. Open your deployed Google Apps Script web app
2. Allow camera permissions
3. Point camera at QR codes to scan
4. Attendance is automatically recorded in Google Sheets
5. View real-time results on the scanner interface

## 🕐 Time-based Attendance Logic

- **Before 9:00 AM**: Marked as Present (X)
- **9:00-9:10 AM**: Marked as Late (T)
- **9:10-10:00 AM**: No attendance recorded (skip window)
- **After 10:00 AM**: Marked as Present in afternoon column
- **After 12:00 PM**: Marked as Late for afternoon (O)

## 🛠️ Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/qr-attendance-system.git
cd qr-attendance-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Code Structure

- `src/qr_generation/`: QR code creation and processing
- `src/image_processing/`: Image overlay and ID card creation
- `src/google_apps_script/`: Web interface and backend logic
- `scripts/`: Utility and setup scripts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [qrcode](https://github.com/lincolnloop/python-qrcode) library for QR code generation
- [Pillow](https://github.com/python-pillow/Pillow) for image processing
- [html5-qrcode](https://github.com/mebjas/html5-qrcode) for web-based QR scanning
- Google Apps Script for serverless backend

## 📞 Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Search [existing issues](https://github.com/yourusername/qr-attendance-system/issues)
3. Create a [new issue](https://github.com/yourusername/qr-attendance-system/issues/new)

## 🔮 Roadmap

- [ ] Database integration (SQLite/PostgreSQL)
- [ ] Advanced reporting and analytics
- [ ] Multiple language support
- [ ] Mobile app for scanning
- [ ] Bulk import/export features
- [ ] Email notifications
- [ ] Integration with other attendance systems
