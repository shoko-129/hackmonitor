#!/bin/bash

echo "========================================"
echo "  MLH Digital Hackathon Monitor Setup"
echo "  Linux/macOS System Installation"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  macOS: brew install python3"
    exit 1
fi

echo "✅ Python found"
python3 --version

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ ERROR: pip3 is not installed"
    echo "Please install pip3:"
    echo "  Ubuntu/Debian: sudo apt install python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3-pip"
    echo "  macOS: python3 -m ensurepip --upgrade"
    exit 1
fi

echo "✅ pip3 found"

# Install packages globally to system
echo
echo "📥 Installing packages to system Python..."
echo "⚠️  This will install packages globally (no virtual environment)"
echo

# Check for externally managed environment
echo "🔄 Checking Python environment..."

# Try user installation first
echo "🔄 Attempting user installation (--user flag)..."
pip3 install --user -r requirements_pyqt.txt 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ Packages installed successfully to user directory!"
    echo "📍 Installed to: ~/.local/lib/python*/site-packages/"
else
    echo "⚠️ User installation failed (externally managed environment)"
    echo "🔄 Trying with --break-system-packages flag..."

    # Try with break-system-packages flag
    pip3 install --break-system-packages -r requirements_pyqt.txt

    if [ $? -eq 0 ]; then
        echo "✅ Packages installed successfully to system!"
    else
        echo "⚠️ pip installation failed, trying system packages..."
        echo "🔐 Installing system packages (requires sudo)..."

        # Try installing system packages
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y python3-pyqt5 python3-requests python3-bs4 python3-lxml python3-openpyxl python3-selenium python3-pil python3-dateutil
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-PyQt5 python3-requests python3-beautifulsoup4 python3-lxml python3-openpyxl python3-selenium python3-pillow python3-dateutil
        elif command -v brew &> /dev/null; then
            brew install python-tk
            pip3 install --break-system-packages -r requirements_pyqt.txt
        else
            echo "❌ ERROR: Could not install packages"
            echo "Please install manually:"
            echo "  pip3 install --break-system-packages PyQt5 requests beautifulsoup4"
            exit 1
        fi

        if [ $? -eq 0 ]; then
            echo "✅ System packages installed successfully!"
        else
            echo "❌ ERROR: Failed to install system packages"
            exit 1
        fi
    fi
fi

echo
echo "🎉 Setup complete!"
echo
echo "To run the application:"
echo "  1. Run: ./launch_pyqt_gui.sh"
echo "  2. Or run: python3 hackathon_monitor_pyqt.py"
echo

# Make launcher executable
chmod +x launch_pyqt_gui.sh
echo "✅ Made launch_pyqt_gui.sh executable"
echo
