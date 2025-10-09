#!/usr/bin/env python3
"""
Windows-specific setup script for QR Code Attendance System
Handles Windows Python installation quirks
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def find_python_command():
    """Find the correct Python command on Windows"""
    commands_to_try = ['python', 'python3', 'py']
    
    for cmd in commands_to_try:
        try:
            result = subprocess.run(
                f'{cmd} --version', shell=True, capture_output=True, text=True, check=True
            )
            if 'Python 3.' in result.stdout:
                print(f"✅ Found Python: {cmd} -> {result.stdout.strip()}")
                return cmd
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    return None


def run_command(command, description, python_cmd="python"):
    """Run a shell command and handle errors"""
    print(f"⏳ {description}...")
    
    # Replace python with the correct command for Windows
    if command.startswith("python"):
        command = command.replace("python", python_cmd, 1)
    
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return None


def create_virtual_environment(python_cmd):
    """Create a Python virtual environment on Windows"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return True

    return run_command(f"{python_cmd} -m venv venv", "Creating virtual environment", python_cmd)


def install_dependencies(python_cmd):
    """Install Python dependencies on Windows"""
    # Windows uses different activation
    activate_cmd = "venv\\Scripts\\activate"
    pip_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    return run_command(pip_cmd, "Installing Python dependencies", python_cmd)


def check_node_and_install_clasp():
    """Check Node.js and install clasp for Google Apps Script deployment"""
    # Check if Node.js is installed
    node_check = run_command("node --version", "Checking Node.js installation")
    if not node_check:
        print("❌ Node.js is not installed. Please install Node.js first:")
        print("   - Download from https://nodejs.org")
        print("   - Make sure to check 'Add to PATH' during installation")
        print("   - Restart PowerShell after installation")
        return False

    print(f"✅ Node.js is installed: {node_check.strip()}")

    # Check if clasp is already installed
    clasp_check = run_command("clasp --version", "Checking clasp installation")
    if clasp_check:
        print(f"✅ clasp is already installed: {clasp_check.strip()}")
        return True

    # Install clasp
    result = run_command(
        "npm install -g @google/clasp@2.4.2",
        "Installing Google Apps Script CLI (clasp) stable version",
    )
    return result is not None


def setup_clasp_config():
    """Set up clasp configuration files"""
    gas_dir = Path("src/google_apps_script")

    # Create .claspignore file
    claspignore_content = """# Ignore everything except specific files
**/**
!Code.gs
!Index.html
!appsscript.json
"""

    claspignore_path = gas_dir / ".claspignore"
    if not claspignore_path.exists() or claspignore_path.stat().st_size == 0:
        with open(claspignore_path, "w") as f:
            f.write(claspignore_content)
        print("✅ Created .claspignore file")
    else:
        print("✅ .claspignore file already exists")

    # Create appsscript.json if it doesn't exist or is empty
    appsscript_path = gas_dir / "appsscript.json"
    if not appsscript_path.exists() or appsscript_path.stat().st_size == 0:
        appsscript_content = {
            "timeZone": "America/New_York",
            "dependencies": {},
            "exceptionLogging": "STACKDRIVER",
            "runtimeVersion": "V8",
            "webapp": {"access": "ANYONE_ANONYMOUS", "executeAs": "USER_DEPLOYING"},
        }

        with open(appsscript_path, "w") as f:
            json.dump(appsscript_content, f, indent=2)
        print("✅ Created appsscript.json file")
    else:
        print("✅ appsscript.json file already exists")

    # Create Windows batch file for deployment
    deploy_bat_path = gas_dir / "deploy.bat"
    if not deploy_bat_path.exists() or deploy_bat_path.stat().st_size == 0:
        deploy_bat_content = '''@echo off
REM Google Apps Script Deployment Script for Windows
REM This script automates the deployment of your Google Apps Script files

echo 🚀 Starting Google Apps Script Deployment
echo ======================================

REM Check if we're in the right directory
if not exist "Code.gs" (
    echo ❌ Please run this script from the src/google_apps_script directory
    echo Try: cd src\\google_apps_script ^&^& deploy.bat
    pause
    exit /b 1
)

if not exist "Scanner.html" (
    echo ❌ Scanner.html not found in current directory
    pause
    exit /b 1
)

REM Check if clasp is installed
clasp --version >nul 2>&1
if errorlevel 1 (
    echo ❌ clasp is not installed. Please install it first:
    echo npm install -g @google/clasp
    pause
    exit /b 1
)

echo ✅ clasp is installed

REM Check if user is logged in
clasp login --status >nul 2>&1
if errorlevel 1 (
    echo ⚠️ You need to login to clasp first
    echo Running: clasp login
    clasp login
)

echo ✅ clasp login verified

REM Check if .clasp.json exists
if not exist ".clasp.json" (
    echo ⚠️ No .clasp.json found. You need to create or clone a project first.
    echo.
    echo Choose an option:
    echo 1^) Create a new Google Apps Script project
    echo 2^) Clone an existing project ^(you'll need the script ID^)
    echo 3^) Exit and do this manually
    set /p choice="Enter choice (1-3): "
    
    if "!choice!"=="1" (
        echo Creating new Google Apps Script project...
        clasp create --title "Church Attendance System" --type webapp
    ) else if "!choice!"=="2" (
        set /p script_id="Enter your Google Apps Script ID: "
        echo Cloning existing project...
        clasp clone "!script_id!"
    ) else (
        echo Exiting. You can manually run:
        echo clasp create --title "Church Attendance System" --type webapp
        echo or
        echo clasp clone YOUR_SCRIPT_ID
        pause
        exit /b 0
    )
)

echo ✅ Project configuration found

REM Push the code
echo Pushing code to Google Apps Script...
clasp push
if errorlevel 1 (
    echo ❌ Failed to push code
    pause
    exit /b 1
)

echo ✅ Code pushed successfully

REM Deploy
echo Creating/updating deployment...
clasp deploy --description "Deployment from Windows %date% %time%"
if errorlevel 1 (
    echo ❌ Failed to deploy
    pause
    exit /b 1
)

echo ✅ Deployment completed successfully!
echo.
echo You can now test your attendance system
echo To update in the future, just run this script again

pause
'''

        with open(deploy_bat_path, "w", encoding='utf-8') as f:
            f.write(deploy_bat_content)

        print("✅ Created deploy.bat script for Windows")
    else:
        print("✅ deploy.bat script already exists")

    return True


def setup_git():
    """Initialize git repository if not already done"""
    if Path(".git").exists():
        print("✅ Git repository already initialized")
        return True

    # Git should work the same on Windows
    commands = [
        "git init",
        "git add .",
        "git commit -m 'Initial commit: Project restructure'",
    ]

    for cmd in commands:
        if not run_command(cmd, f"Git: {cmd}"):
            return False

    return True


def create_example_config():
    """Create example configuration files"""
    config_path = Path("config/settings.json")
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)

        # Update paths to be Windows-compatible
        config["qr_generation"]["default_output_dir"] = "output"

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Updated configuration file")

    return True


def setup_windows_terminal_beautification():
    """Set up Windows Terminal and PowerShell beautification"""
    print("\n🎨 Windows Terminal Beautification")
    print("=" * 40)
    
    print("🖥️  For the best terminal experience on Windows:")
    print("   1. Install Windows Terminal from Microsoft Store")
    print("   2. Install Git for Windows (includes Git Bash)")
    print("   3. Consider PowerShell modules for git integration")
    
    # Check if Windows Terminal is available
    try:
        result = subprocess.run(
            "wt --version", shell=True, capture_output=True, text=True, check=True
        )
        print("✅ Windows Terminal is installed")
        
        # Try to install PowerShell modules for git
        print("📦 Setting up PowerShell git integration...")
        
        # Install posh-git for PowerShell git integration
        posh_git_cmd = "powershell -Command \"Install-Module posh-git -Scope CurrentUser -Force\""
        posh_result = run_command(posh_git_cmd, "Installing posh-git PowerShell module")
        
        if posh_result is not None:
            print("✅ posh-git installed for git branch display in PowerShell")
            
            # Create PowerShell profile to auto-load posh-git
            profile_cmd = """powershell -Command "
                if (!(Test-Path -Path $PROFILE)) {
                    New-Item -ItemType File -Path $PROFILE -Force
                }
                Add-Content -Path $PROFILE -Value 'Import-Module posh-git'
                Add-Content -Path $PROFILE -Value 'Set-PoshPrompt -Theme Paradox'
            " """
            
            profile_result = run_command(profile_cmd, "Setting up PowerShell profile")
            if profile_result is not None:
                print("✅ PowerShell profile configured for git display")
        else:
            print("⚠️  posh-git installation failed, but continuing...")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Windows Terminal not found")
        print("💡 Install Windows Terminal from Microsoft Store for better experience")
    
    # Check for Git Bash
    try:
        git_bash_check = run_command("bash --version", "Checking Git Bash")
        if git_bash_check:
            print("✅ Git Bash is available (alternative to PowerShell)")
            print("💡 Git Bash provides Unix-like experience with git integration")
    except:
        print("💡 Consider installing Git for Windows for Git Bash")
    
    print("\n🎯 Terminal Setup Recommendations:")
    print("   • Windows Terminal + PowerShell + posh-git (modern)")
    print("   • Git Bash (Unix-like experience)")
    print("   • WSL2 + Oh My Zsh (advanced users)")
    
    return True


def main():
    """Main setup function for Windows"""
    print("🚀 Setting up QR Code Attendance System (Windows)")
    print("=" * 60)

    # Find the correct Python command
    python_cmd = find_python_command()
    if not python_cmd:
        print("❌ Python 3.7+ is required but not found!")
        print("\n🔧 To fix this:")
        print("1. Install Python from https://python.org/downloads/")
        print("2. OR install from Microsoft Store by typing 'python' in cmd")
        print("3. Make sure to check 'Add Python to PATH' during installation")
        print("4. Restart PowerShell/Command Prompt after installation")
        print("5. Then run this script again")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # Check Python version
    try:
        result = subprocess.run(
            f'{python_cmd} -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}\")"',
            shell=True, capture_output=True, text=True, check=True
        )
        version = result.stdout.strip()
        major, minor = map(int, version.split('.'))
        
        if major < 3 or (major == 3 and minor < 7):
            print(f"❌ Python 3.7+ required, found {version}")
            input("Press Enter to exit...")
            sys.exit(1)
            
        print(f"✅ Python {version} detected")
    except:
        print("❌ Could not determine Python version")
        input("Press Enter to exit...")
        sys.exit(1)

    # Setup steps
    steps = [
        ("Creating virtual environment", lambda: create_virtual_environment(python_cmd)),
        ("Installing dependencies", lambda: install_dependencies(python_cmd)),
        ("Setting up Git repository", setup_git),
        ("Creating example configurations", create_example_config),
        (
            "Setting up Google Apps Script deployment",
            lambda: check_node_and_install_clasp() and setup_clasp_config(),
        ),
        ("Setting up Windows terminal beautification", setup_windows_terminal_beautification),
    ]

    for description, func in steps:
        try:
            if not func():
                if "Google Apps Script" in description:
                    print(f"⚠️  {description} skipped (Node.js may not be installed)")
                    continue
                else:
                    print(f"❌ Setup failed at: {description}")
                    input("Press Enter to exit...")
                    sys.exit(1)
        except Exception as e:
            if "Google Apps Script" in description:
                print(f"⚠️  {description} skipped: {str(e)}")
                continue
            else:
                print(f"❌ Setup failed at: {description}")
                print(f"Error: {str(e)}")
                input("Press Enter to exit...")
                sys.exit(1)

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment: venv\\Scripts\\activate")
    print(f"2. Update config/gas_config.json with your Google Sheets ID")
    print("3. Add your student data to data/csv_files/")
    print(f"4. Run the QR generation script: {python_cmd} scripts/create_qrcode_card_name.py")
    print("5. For Google Apps Script deployment:")
    print("   - Go to src/google_apps_script/")
    print("   - Run: deploy.bat")
    print("   - Follow the prompts to deploy your attendance system")
    
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()