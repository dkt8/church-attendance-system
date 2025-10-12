#!/bin/bash
# Church Attendance System - Complete Setup Script
# This script will install everything needed including Python, Node.js, and Oh My Zsh

set -e  # Exit on any error

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}🚀 $1${NC}"
    echo "$(echo "$1" | sed 's/./=/g')"
}

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

print_step() {
    echo -e "${CYAN}⏳ $1${NC}"
}

# Function to run command with error handling
run_command() {
    local cmd="$1"
    local description="$2"
    local optional="${3:-false}"
    
    print_step "$description..."
    
    if eval "$cmd" >/dev/null 2>&1; then
        print_status "$description completed successfully"
        return 0
    else
        if [ "$optional" = "true" ]; then
            print_warning "$description failed (optional step, continuing)"
            return 0
        else
            print_error "$description failed"
            return 1
        fi
    fi
}

# Function to detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            case $ID in
                ubuntu|debian)
                    echo "ubuntu"
                    ;;
                fedora|rhel|centos)
                    echo "fedora"
                    ;;
                arch|manjaro)
                    echo "arch"
                    ;;
                *)
                    echo "linux"
                    ;;
            esac
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        echo "windows"
    else
        echo "unknown"
    fi
}

# Function to install Python
install_python() {
    print_header "Installing Python"
    
    # Check if Python 3 is already installed
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python 3 is already installed: $python_version"
        
        # Check if version is 3.8+
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
            print_status "Python version is sufficient (3.8+)"
            return 0
        else
            print_warning "Python version is too old, attempting to upgrade..."
        fi
    else
        print_info "Python 3 not found, installing..."
    fi
    
    local os=$(detect_os)
    
    case $os in
        ubuntu)
            run_command "sudo apt update" "Updating package lists"
            run_command "sudo apt install -y python3 python3-pip python3-venv python3-dev" "Installing Python 3 and tools"
            ;;
        fedora)
            run_command "sudo dnf install -y python3 python3-pip python3-venv python3-devel" "Installing Python 3 and tools"
            ;;
        arch)
            run_command "sudo pacman -S --noconfirm python python-pip" "Installing Python 3 and tools"
            ;;
        macos)
            if command -v brew &> /dev/null; then
                run_command "brew install python3" "Installing Python 3 via Homebrew"
            else
                print_error "Homebrew not found. Please install Homebrew first:"
                echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        windows)
            print_error "Windows detected. Please install Python manually:"
            print_info "Download from: https://www.python.org/downloads/"
            print_info "Make sure to check 'Add Python to PATH' during installation"
            exit 1
            ;;
        *)
            print_error "Unsupported operating system. Please install Python 3.8+ manually."
            exit 1
            ;;
    esac
    
    # Verify installation
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python 3 installed successfully: $python_version"
    else
        print_error "Python 3 installation failed"
        exit 1
    fi
}

# Function to create virtual environment
create_virtual_environment() {
    print_header "Creating Python Virtual Environment"
    
    if [ -d "venv" ]; then
        print_status "Virtual environment already exists"
        return 0
    fi
    
    run_command "python3 -m venv venv" "Creating virtual environment"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_header "Installing Python Dependencies"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Activate virtual environment and install dependencies
    run_command "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt" "Installing Python packages"
}

# Function to install Node.js
install_nodejs() {
    print_header "Installing Node.js"
    
    # Check if Node.js is already installed
    if command -v node &> /dev/null; then
        node_version=$(node --version 2>&1)
        print_status "Node.js is already installed: $node_version"
        return 0
    fi
    
    print_info "Node.js not found, installing..."
    
    local os=$(detect_os)
    
    case $os in
        ubuntu)
            # Install Node.js via NodeSource repository for latest version
            run_command "curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -" "Adding NodeSource repository" "true"
            if [ $? -eq 0 ]; then
                run_command "sudo apt install -y nodejs" "Installing Node.js via NodeSource"
            else
                # Fallback to Ubuntu repository
                run_command "sudo apt install -y nodejs npm" "Installing Node.js via apt"
            fi
            ;;
        fedora)
            run_command "sudo dnf install -y nodejs npm" "Installing Node.js via dnf"
            ;;
        arch)
            run_command "sudo pacman -S --noconfirm nodejs npm" "Installing Node.js via pacman"
            ;;
        macos)
            if command -v brew &> /dev/null; then
                run_command "brew install node" "Installing Node.js via Homebrew"
            else
                print_warning "Homebrew not found, skipping Node.js installation"
                return 0
            fi
            ;;
        *)
            print_warning "Unsupported OS for automatic Node.js installation"
            print_info "Please install Node.js manually from: https://nodejs.org"
            return 0
            ;;
    esac
    
    # Verify installation
    if command -v node &> /dev/null; then
        node_version=$(node --version 2>&1)
        print_status "Node.js installed successfully: $node_version"
    else
        print_warning "Node.js installation may have failed, but continuing"
    fi
}

# Function to install Google Apps Script CLI (clasp)
install_clasp() {
    print_header "Installing Google Apps Script CLI (clasp)"
    
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found, skipping clasp installation"
        return 0
    fi
    
    if command -v clasp &> /dev/null; then
        clasp_version=$(clasp --version 2>&1)
        print_status "clasp is already installed: $clasp_version"
        return 0
    fi
    
    run_command "npm install -g @google/clasp@2.4.2" "Installing clasp (Google Apps Script CLI)"
    
    # Verify installation
    if command -v clasp &> /dev/null; then
        clasp_version=$(clasp --version 2>&1)
        print_status "clasp installed successfully: $clasp_version"
    else
        print_warning "clasp installation may have failed"
    fi
}

# Function to setup Google Apps Script files
setup_gas_config() {
    print_header "Setting up Google Apps Script Configuration"
    
    local gas_dir="src/google_apps_script"
    
    if [ ! -d "$gas_dir" ]; then
        print_warning "Google Apps Script directory not found, skipping"
        return 0
    fi
    
    # Create .claspignore file
    local claspignore_content="# Ignore everything except specific files
**/**
!Code.gs
!Index.html
!appsscript.json"
    
    if [ ! -f "$gas_dir/.claspignore" ] || [ ! -s "$gas_dir/.claspignore" ]; then
        echo "$claspignore_content" > "$gas_dir/.claspignore"
        print_status "Created .claspignore file"
    else
        print_status ".claspignore file already exists"
    fi
    
    # Create appsscript.json if it doesn't exist
    if [ ! -f "$gas_dir/appsscript.json" ] || [ ! -s "$gas_dir/appsscript.json" ]; then
        cat > "$gas_dir/appsscript.json" << 'EOF'
{
  "timeZone": "America/New_York",
  "dependencies": {},
  "exceptionLogging": "STACKDRIVER",
  "runtimeVersion": "V8",
  "webapp": {
    "access": "ANYONE_ANONYMOUS",
    "executeAs": "USER_DEPLOYING"
  }
}
EOF
        print_status "Created appsscript.json file"
    else
        print_status "appsscript.json file already exists"
    fi
    
    # Create deployment script
    if [ ! -f "$gas_dir/deploy.sh" ] || [ ! -s "$gas_dir/deploy.sh" ]; then
        cat > "$gas_dir/deploy.sh" << 'EOF'
#!/bin/bash
# Google Apps Script Deployment Script using clasp

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}✅ $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_error() { echo -e "${RED}❌ $1${NC}"; }

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

# Check if .clasp.json exists
if [[ ! -f ".clasp.json" ]]; then
    print_warning "No .clasp.json found. Creating new project..."
    clasp create --title "Church Attendance System" --type webapp
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

# Deploy
print_info "Creating/updating deployment..."
if clasp deploy --description "Updated $(date '+%Y-%m-%d %H:%M:%S')"; then
    print_status "Deployment completed successfully!"
    clasp deployments | grep "https://" || print_warning "Could not extract URL"
else
    print_error "Failed to deploy"
    exit 1
fi

print_status "Deployment completed!"
EOF
        chmod +x "$gas_dir/deploy.sh"
        print_status "Created deploy.sh script and made it executable"
    else
        print_status "deploy.sh script already exists"
    fi
}

# Function to install zsh and Oh My Zsh
install_zsh_and_ohmyzsh() {
    print_header "Installing Zsh and Oh My Zsh"
    
    # Check if Oh My Zsh is already installed
    if [ -d "$HOME/.oh-my-zsh" ]; then
        print_status "Oh My Zsh is already installed"
        return 0
    fi
    
    # Install zsh if not present
    if ! command -v zsh &> /dev/null; then
        print_step "Installing zsh..."
        
        local os=$(detect_os)
        case $os in
            ubuntu)
                run_command "sudo apt install -y zsh" "Installing zsh via apt"
                ;;
            fedora)
                run_command "sudo dnf install -y zsh" "Installing zsh via dnf"
                ;;
            arch)
                run_command "sudo pacman -S --noconfirm zsh" "Installing zsh via pacman"
                ;;
            macos)
                print_status "Zsh is usually pre-installed on macOS"
                ;;
            *)
                print_warning "Please install zsh manually for your system"
                return 0
                ;;
        esac
    else
        print_status "Zsh is already installed"
    fi
    
    # Install Oh My Zsh
    print_step "Installing Oh My Zsh..."
    if curl -fsSL https://raw.github.com/ohmyzsh/ohmyzsh/master/tools/install.sh | RUNZSH=no CHSH=no sh; then
        print_status "Oh My Zsh installed successfully!"
        
        # Keep robbyrussell theme (default)
        if [ -f "$HOME/.zshrc" ]; then
            if grep -q 'ZSH_THEME="robbyrussell"' "$HOME/.zshrc"; then
                print_status "Using 'robbyrussell' theme (clean and simple)"
            else
                # Set robbyrussell theme
                sed -i 's/ZSH_THEME="[^"]*"/ZSH_THEME="robbyrussell"/' "$HOME/.zshrc"
                print_status "Set theme to 'robbyrussell' (clean and simple)"
            fi
        fi
        
        print_info "💡 To make zsh your default shell, run: chsh -s \$(which zsh)"
        print_info "💡 You'll need to log out and back in for this to take effect"
    else
        print_warning "Oh My Zsh installation failed, but continuing"
    fi
}

# Function to setup git repository
setup_git() {
    print_header "Setting up Git Repository"
    
    if [ -d ".git" ]; then
        print_status "Git repository already initialized"
        return 0
    fi
    
    run_command "git init" "Initializing git repository"
    run_command "git add ." "Adding files to git"
    run_command "git commit -m 'Initial commit: Project setup'" "Creating initial commit"
}

# Function to update configuration
update_config() {
    print_header "Updating Configuration Files"
    
    local config_file="config/settings.json"
    if [ -f "$config_file" ]; then
        # Update paths to be relative to project root using Python
        python3 -c "
import json
import sys

try:
    with open('$config_file', 'r') as f:
        config = json.load(f)
    
    if 'qr_generation' in config and 'default_output_dir' in config['qr_generation']:
        config['qr_generation']['default_output_dir'] = 'output'
    
    with open('$config_file', 'w') as f:
        json.dump(config, f, indent=2)
    
    print('Configuration updated successfully')
except Exception as e:
    print(f'Warning: Could not update config: {e}', file=sys.stderr)
" && print_status "Updated configuration file" || print_warning "Could not update configuration file"
    else
        print_info "No configuration file found to update"
    fi
}

# Main setup function
main() {
    print_header "Church Attendance System - Complete Setup"
    echo
    
    # Check if we're in the right directory
    if [ ! -f "requirements.txt" ] || [ ! -f "README.md" ]; then
        print_error "Please run this script from the project root directory"
        print_info "Expected files: requirements.txt, README.md"
        exit 1
    fi
    
    print_info "Setting up Church Attendance System..."
    print_info "This will install Python, Node.js, and configure everything needed"
    echo
    
    # Setup steps
    install_python
    create_virtual_environment
    install_python_dependencies
    install_nodejs
    install_clasp
    setup_gas_config
    install_zsh_and_ohmyzsh
    setup_git
    update_config
    
    # Final success message
    echo
    print_header "🎉 Setup Completed Successfully!"
    echo
    print_info "🎯 Next steps:"
    echo "  1. Activate the virtual environment:"
    echo "     source venv/bin/activate"
    echo
    echo "  2. Update config/gas_config.json with your Google Sheets ID"
    echo
    echo "  3. Add your student data to data/csv_files/"
    echo
    echo "  4. Generate QR codes:"
    echo "     python scripts/create_qrcode_card_name.py"
    echo
    echo "  5. Deploy to Google Apps Script:"
    echo "     cd src/google_apps_script && ./deploy.sh"
    echo
    print_info "📚 Full documentation available in README.md"
    echo
    if [ -d "$HOME/.oh-my-zsh" ]; then
        print_info "💡 Oh My Zsh installed! Start a new terminal or run 'zsh' to use it"
    fi
}

# Run main function
main "$@"