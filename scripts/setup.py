#!/usr/bin/env python3
"""
Setup script for QR Code Attendance System
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None

def create_virtual_environment():
    """Create a Python virtual environment"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True
    
    return run_command("python3 -m venv venv", "Creating virtual environment")

def install_dependencies():
    """Install Python dependencies"""
    activate_cmd = "source venv/bin/activate" if os.name != 'nt' else "venv\\Scripts\\activate"
    pip_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    return run_command(pip_cmd, "Installing Python dependencies")

def setup_git():
    """Initialize git repository if not already done"""
    if Path(".git").exists():
        print("✅ Git repository already initialized")
        return True
    
    commands = [
        "git init",
        "git add .",
        "git commit -m 'Initial commit: Project restructure'"
    ]
    
    for cmd in commands:
        if not run_command(cmd, f"Git: {cmd}"):
            return False
    
    return True

def create_example_config():
    """Create example configuration files"""
    config_path = Path("config/settings.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update paths to be relative to project root
        config['qr_generation']['default_output_dir'] = "output"
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Updated configuration file")
    
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up QR Code Attendance System")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    
    # Setup steps
    steps = [
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", install_dependencies),
        ("Setting up Git repository", setup_git),
        ("Creating example configurations", create_example_config),
    ]
    
    for description, func in steps:
        if not func():
            print(f"❌ Setup failed at: {description}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment: source venv/bin/activate")
    print("2. Update config/gas_config.json with your Google Sheets ID")
    print("3. Add your student data to data/csv_files/")
    print("4. Run the QR generation script: python scripts/generate_qr_codes.py")
    print("5. Deploy Google Apps Script files to your Google Apps Script project")

if __name__ == "__main__":
    main()
