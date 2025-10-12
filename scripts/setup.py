#!/usr/bin/env python3
"""
Setup script for QR Code Attendance System
"""

import json
import os
import subprocess
import sys
from pathlib import Path


def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"⏳ {description}...")
    try:
        result = subprocess.run(
            command, shell=True, check=True, capture_output=True, text=True
        )
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
    if os.name != "nt":
        # Use bash explicitly for source command on Unix systems
        pip_cmd = "bash -c 'source venv/bin/activate && pip install -r requirements.txt'"
    else:
        pip_cmd = "venv\\Scripts\\activate && pip install -r requirements.txt"
    return run_command(pip_cmd, "Installing Python dependencies")


def install_nodejs():
    """Install Node.js if not already installed"""
    # Check if Node.js is already installed
    node_check = run_command("node --version", "Checking Node.js installation")
    if node_check:
        print(f"✅ Node.js is already installed: {node_check.strip()}")
        return True
    
    print("📦 Node.js not found. Installing Node.js...")
    
    # Detect the operating system and install accordingly
    if os.name == "nt":  # Windows
        print("❌ Please install Node.js manually on Windows:")
        print("   Download from https://nodejs.org")
        return False
    elif sys.platform == "darwin":  # macOS
        # Try Homebrew first
        if run_command("brew --version", "Checking Homebrew"):
            return run_command("brew install node", "Installing Node.js via Homebrew")
        else:
            print("❌ Please install Node.js manually on macOS:")
            print("   - Install Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            print("   - Then run: brew install node")
            print("   - Or download from https://nodejs.org")
            return False
    else:  # Linux
        # Try to detect the Linux distribution
        try:
            with open("/etc/os-release", "r") as f:
                os_release = f.read()
            
            if "ubuntu" in os_release.lower() or "debian" in os_release.lower():
                # Ubuntu/Debian
                print("🐧 Detected Ubuntu/Debian. Installing Node.js via apt...")
                update_result = run_command("sudo apt update", "Updating package lists")
                if update_result is not None:
                    return run_command("sudo apt install -y nodejs npm", "Installing Node.js and npm")
            elif "fedora" in os_release.lower() or "rhel" in os_release.lower() or "centos" in os_release.lower():
                # Fedora/RHEL/CentOS
                print("🎩 Detected Fedora/RHEL/CentOS. Installing Node.js via dnf/yum...")
                return run_command("sudo dnf install -y nodejs npm || sudo yum install -y nodejs npm", "Installing Node.js and npm")
            elif "arch" in os_release.lower():
                # Arch Linux
                print("🏹 Detected Arch Linux. Installing Node.js via pacman...")
                return run_command("sudo pacman -S --noconfirm nodejs npm", "Installing Node.js and npm")
            else:
                print("❌ Unknown Linux distribution. Please install Node.js manually:")
                print("   - Use your package manager (nodejs npm)")
                print("   - Or download from https://nodejs.org")
                return False
        except FileNotFoundError:
            print("❌ Could not detect Linux distribution. Please install Node.js manually:")
            print("   - Use your package manager (nodejs npm)")
            print("   - Or download from https://nodejs.org")
            return False
    
    return False


def check_node_and_install_clasp():
    """Check Node.js and install clasp for Google Apps Script deployment"""
    # Install Node.js if not present
    if not install_nodejs():
        return False

    # Verify Node.js installation
    node_check = run_command("node --version", "Verifying Node.js installation")
    if not node_check:
        print("❌ Node.js installation failed or not accessible")
        return False

    print(f"✅ Node.js is ready: {node_check.strip()}")

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

    # Create deployment script if it doesn't exist or is empty
    deploy_script_path = gas_dir / "deploy.sh"
    if not deploy_script_path.exists() or deploy_script_path.stat().st_size == 0:
        deploy_script_content = '''#!/bin/bash
"""
Google Apps Script Deployment Script using clasp
This script automates the deployment of your Google Apps Script files
"""

set -e  # Exit on any error

# Colors for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
BLUE='\\033[0;34m'
NC='\\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the right directory
if [[ ! -f "Code.gs" || ! -f "Index.html" ]]; then
    print_error "Please run this script from the src/google_apps_script directory"
    print_info "Try: cd src/google_apps_script && ./deploy.sh"
    exit 1
fi

print_info "🚀 Starting Google Apps Script Deployment"
echo "======================================"

# Check if clasp is installed
if ! command -v clasp &> /dev/null; then
    print_error "clasp is not installed. Please install it first:"
    echo "npm install -g @google/clasp"
    exit 1
fi

print_status "clasp is installed"

# Check if user is logged in
if ! clasp login --status &> /dev/null; then
    print_warning "You need to login to clasp first"
    print_info "Running: clasp login"
    clasp login
fi

print_status "clasp login verified"

# Check if .clasp.json exists (indicates project is already created)
if [[ ! -f ".clasp.json" ]]; then
    print_warning "No .clasp.json found. You need to create or clone a project first."
    echo
    echo "Choose an option:"
    echo "1) Create a new Google Apps Script project"
    echo "2) Clone an existing project (you'll need the script ID)"
    echo "3) Exit and do this manually"
    read -p "Enter choice (1-3): " choice
    
    case $choice in
        1)
            print_info "Creating new Google Apps Script project..."
            clasp create --title "Church Attendance System" --type webapp
            ;;
        2)
            read -p "Enter your Google Apps Script ID: " script_id
            print_info "Cloning existing project..."
            clasp clone "$script_id"
            ;;
        3)
            print_info "Exiting. You can manually run:"
            echo "clasp create --title 'Church Attendance System' --type webapp"
            echo "or"
            echo "clasp clone YOUR_SCRIPT_ID"
            exit 0
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
fi

print_status "Project configuration found"

# Push the code
print_info "Pushing code to Google Apps Script..."
if clasp push; then
    print_status "Code pushed successfully"
else
    print_error "Failed to push code"
    exit 1
fi

# Get current deployments
print_info "Checking existing deployments..."
deployments=$(clasp deployments 2>/dev/null || echo "")

if [[ -n "$deployments" && "$deployments" != *"No deployments"* ]]; then
    print_info "Found existing deployments:"
    echo "$deployments"
    echo
    read -p "Do you want to update the existing deployment? (y/n): " update_existing
    
    if [[ "$update_existing" =~ ^[Yy]$ ]]; then
        # Extract the first deployment ID
        deployment_id=$(echo "$deployments" | grep -o '@[0-9]*' | head -1 | cut -c2-)
        if [[ -n "$deployment_id" ]]; then
            print_info "Updating deployment ID: $deployment_id"
            if clasp deploy --deploymentId "$deployment_id" --description "Updated $(date '+%Y-%m-%d %H:%M:%S')"; then
                print_status "Deployment updated successfully!"
                
                # Get the web app URL
                print_info "Getting web app URL..."
                clasp deployments | grep "https://" || print_warning "Could not extract URL. Check your Google Apps Script console."
            else
                print_error "Failed to update deployment"
                exit 1
            fi
        else
            print_error "Could not extract deployment ID"
            exit 1
        fi
    else
        print_info "Skipping deployment update"
    fi
else
    # No existing deployments, create new one
    print_info "No existing deployments found. Creating new deployment..."
    if clasp deploy --description "Initial deployment $(date '+%Y-%m-%d %H:%M:%S')"; then
        print_status "New deployment created successfully!"
        
        # Get the web app URL
        print_info "Getting web app URL..."
        clasp deployments | grep "https://" || print_warning "Could not extract URL. Check your Google Apps Script console."
    else
        print_error "Failed to create deployment"
        exit 1
    fi
fi

echo
print_status "Deployment completed!"
print_info "You can now test your attendance system"
print_info "To update in the future, just run this script again"

# Optional: Open the script in browser
read -p "Do you want to open the Google Apps Script editor? (y/n): " open_editor
if [[ "$open_editor" =~ ^[Yy]$ ]]; then
    clasp open
fi
'''

        with open(deploy_script_path, "w") as f:
            f.write(deploy_script_content)

        # Make the script executable
        import stat

        current_permissions = deploy_script_path.stat().st_mode
        deploy_script_path.chmod(current_permissions | stat.S_IEXEC)

        print("✅ Created deploy.sh script and made it executable")
    else:
        print("✅ deploy.sh script already exists")

    return True


def setup_git():
    """Initialize git repository if not already done"""
    if Path(".git").exists():
        print("✅ Git repository already initialized")
        return True

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

        # Update paths to be relative to project root
        config["qr_generation"]["default_output_dir"] = "output"

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print("✅ Updated configuration file")

    return True


def setup_zsh_prettification():
    """Install Oh My Zsh for a prettier terminal"""
    print("\n🎨 Terminal Beautification")
    print("=" * 30)
    
    # Check if Oh My Zsh is already installed
    oh_my_zsh_path = Path.home() / ".oh-my-zsh"
    if oh_my_zsh_path.exists():
        print("✅ Oh My Zsh is already installed")
        return True
    
    # Check if zsh is installed first
    zsh_check = run_command("zsh --version", "Checking if zsh is installed")
    if not zsh_check:
        print("📦 Zsh not found. Installing zsh first...")
        
        # Install zsh based on the operating system
        if os.name == "nt":  # Windows
            print("⚠️  Zsh installation on Windows requires WSL or manual setup")
            print("💡 Consider using Windows Terminal with PowerShell themes instead")
            return True
        elif sys.platform == "darwin":  # macOS
            if run_command("brew --version", "Checking Homebrew"):
                zsh_install = run_command("brew install zsh", "Installing zsh via Homebrew")
                if not zsh_install:
                    return True
            else:
                print("✅ Zsh is usually pre-installed on macOS")
        else:  # Linux
            try:
                with open("/etc/os-release", "r") as f:
                    os_release = f.read()
                
                if "ubuntu" in os_release.lower() or "debian" in os_release.lower():
                    zsh_install = run_command("sudo apt install -y zsh", "Installing zsh via apt")
                elif "fedora" in os_release.lower() or "rhel" in os_release.lower():
                    zsh_install = run_command("sudo dnf install -y zsh || sudo yum install -y zsh", "Installing zsh")
                elif "arch" in os_release.lower():
                    zsh_install = run_command("sudo pacman -S --noconfirm zsh", "Installing zsh via pacman")
                else:
                    print("⚠️  Please install zsh manually using your package manager")
                    return True
                    
                if not zsh_install:
                    print("⚠️  Zsh installation failed, skipping Oh My Zsh")
                    return True
            except FileNotFoundError:
                print("⚠️  Could not detect system, skipping zsh installation")
                return True
    
    print("📦 Installing Oh My Zsh for prettier terminal...")
    print("⚠️  Note: This installation will be unattended")
    
    # Install Oh My Zsh with unattended installation
    install_cmd = 'RUNZSH=no CHSH=no sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"'
    result = run_command(install_cmd, "Installing Oh My Zsh")
    
    if result is not None:
        print("🎉 Oh My Zsh installed successfully!")
        print("💡 Your terminal will be prettier when you switch to zsh")
        print("💡 To switch to zsh: chsh -s $(which zsh)")
        print("💡 Popular themes: 'robbyrussell' (default), 'agnoster', 'powerlevel10k'")
        print("💡 To change theme: edit ~/.zshrc and change ZSH_THEME")
        
        # Keep the default robbyrussell theme (clean and simple)
        zshrc_path = Path.home() / ".zshrc"
        if zshrc_path.exists():
            try:
                with open(zshrc_path, 'r') as f:
                    content = f.read()
                
                # Verify that robbyrussell theme is set (it should be the default)
                if 'ZSH_THEME="robbyrussell"' in content:
                    print("✅ Using 'robbyrussell' theme (clean and simple)")
                else:
                    # If for some reason it's not robbyrussell, set it
                    import re
                    content = re.sub(r'ZSH_THEME="[^"]*"', 'ZSH_THEME="robbyrussell"', content)
                    with open(zshrc_path, 'w') as f:
                        f.write(content)
                    print("✅ Set theme to 'robbyrussell' (clean and simple)")
                
            except Exception as e:
                print(f"⚠️  Could not verify theme: {e} (using default)")
        
        # Offer to change default shell
        print("\n💡 Optional: To make zsh your default shell, run:")
        print("   chsh -s $(which zsh)")
        print("   (You'll need to log out and back in for this to take effect)")
        
        return True
    else:
        print("⚠️  Oh My Zsh installation failed, but continuing with project setup")
        print("💡 You can install it manually later with:")
        print('   sh -c "$(curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"')
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
        (
            "Setting up Google Apps Script deployment",
            lambda: check_node_and_install_clasp() and setup_clasp_config(),
        ),
        ("Setting up terminal beautification", setup_zsh_prettification),
    ]

    for description, func in steps:
        try:
            if not func():
                if "Google Apps Script" in description:
                    print(f"⚠️  {description} skipped (Node.js may not be installed)")
                    continue
                else:
                    print(f"❌ Setup failed at: {description}")
                    sys.exit(1)
        except Exception as e:
            if "Google Apps Script" in description:
                print(f"⚠️  {description} skipped: {str(e)}")
                continue
            else:
                print(f"❌ Setup failed at: {description}")
                print(f"Error: {str(e)}")
                sys.exit(1)

    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Activate the virtual environment: source venv/bin/activate")
    print("2. Update config/gas_config.json with your Google Sheets ID")
    print("3. Add your student data to data/csv_files/")
    print("4. Run the QR generation script: python scripts/create_qrcode_card_name.py")
    print("5. For Google Apps Script deployment:")
    print("   - Go to src/google_apps_script/")
    print("   - Run: ./deploy.sh")
    print("   - Follow the prompts to deploy your attendance system")
    print("\n💡 If you installed Oh My Zsh, restart your terminal or run 'source ~/.zshrc' for the new theme!")


if __name__ == "__main__":
    main()
