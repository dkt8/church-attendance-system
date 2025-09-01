# Installation Guide

This guide will walk you through setting up the QR Code Attendance System on your local machine.

## System Requirements

### Minimum Requirements
- Python 3.7 or higher
- 2GB RAM
- 500MB free disk space
- Internet connection for Google Sheets integration

### Recommended Requirements
- Python 3.9 or higher
- 4GB RAM
- 1GB free disk space
- Camera-enabled device for QR scanning

## Installation Steps

### 1. Download the Project

#### Option A: Download ZIP
1. Go to the project repository
2. Click "Code" → "Download ZIP"
3. Extract the ZIP file to your desired location

#### Option B: Git Clone
```bash
git clone https://github.com/yourusername/qr-attendance-system.git
cd qr-attendance-system
```

### 2. Automated Setup

Run the setup script to automatically configure everything:

```bash
python scripts/setup.py
```

This script will:
- Create a Python virtual environment
- Install all required dependencies
- Set up configuration files
- Initialize Git repository (if not already done)

### 3. Manual Setup (Alternative)

If the automated setup doesn't work, follow these manual steps:

#### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Google Sheets

#### Create Google Sheets Document
1. Go to [Google Sheets](https://sheets.google.com)
2. Create a new blank spreadsheet
3. Name it something like "Attendance System"
4. Note the spreadsheet ID from the URL

#### Setup Sheets Structure
Create the following sheets in your Google Sheets document:

1. **Master Sheet**: Contains student name mappings
   - Columns: Original Name | Sheet Name | Row Number

2. **Attendance Sheets**: One for each group/class
   - Row 9 should contain date headers (dd/mm/yyyy format)
   - Student names in the first column

#### Update Configuration
Edit `config/gas_config.json`:
```json
{
  "spreadsheet": {
    "id": "YOUR_SPREADSHEET_ID_HERE"
  }
}
```

### 5. Deploy Google Apps Script

#### Create Apps Script Project
1. Go to [Google Apps Script](https://script.google.com)
2. Click "New Project"
3. Name your project (e.g., "QR Attendance System")

#### Add Code Files
1. **Code.gs**: Copy contents from `src/google_apps_script/Code.gs`
2. **Index.html**: 
   - Click the "+" next to "Files"
   - Choose "HTML"
   - Name it "Index"
   - Copy contents from `src/google_apps_script/Index.html`

#### Deploy as Web App
1. Click "Deploy" → "New deployment"
2. Choose "Web app" as the type
3. Set execute permissions to "Anyone"
4. Click "Deploy"
5. Copy the web app URL

### 6. Test the Installation

#### Test QR Generation
```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Generate test QR codes
python scripts/generate_qr_codes.py data/templates/students_template.csv --create-cards
```

#### Test Web Interface
1. Open your Google Apps Script web app URL
2. Allow camera permissions
3. Try scanning a generated QR code

## Troubleshooting

### Common Issues

#### Python Version Error
```
Error: Python 3.7 or higher is required
```
**Solution**: Install a newer version of Python from [python.org](https://python.org)

#### Permission Denied (Scripts)
```
Permission denied: scripts/setup.py
```
**Solution**: Make the script executable:
```bash
chmod +x scripts/setup.py
```

#### Camera Access Denied
**Solution**: 
- Check browser permissions
- Use HTTPS for the web app
- Try a different browser

#### Google Sheets Access Error
**Solution**:
- Verify spreadsheet ID in configuration
- Check Google Apps Script permissions
- Ensure sheets are properly named

#### Import Errors
```
ModuleNotFoundError: No module named 'qrcode'
```
**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Getting Help

If you encounter issues not covered here:

1. Check the [FAQ](FAQ.md)
2. Search [existing issues](https://github.com/yourusername/qr-attendance-system/issues)
3. Create a [new issue](https://github.com/yourusername/qr-attendance-system/issues/new) with:
   - Your operating system
   - Python version (`python --version`)
   - Error messages
   - Steps you've tried

## Next Steps

After successful installation:

1. Read the [Usage Guide](usage.md)
2. Review [Configuration Options](configuration.md)
3. Check out [Examples](../examples/)

## Uninstallation

To remove the system:

1. Delete the project directory
2. Remove the virtual environment
3. Delete the Google Apps Script project (optional)
4. Delete the Google Sheets document (optional)
