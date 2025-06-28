@echo off
echo ========================================
echo   MLH Digital Hackathon Monitor Setup
echo   Windows System Installation Script
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo ✅ Python found
python --version

REM Install packages globally to system
echo.
echo 📥 Installing packages to system Python...
echo ⚠️  This will install packages globally (no virtual environment)
echo.

REM Try user installation first
echo 🔄 Attempting user installation (--user flag)...
python -m pip install --upgrade pip
pip install --user -r requirements_pyqt.txt

if errorlevel 1 (
    echo ⚠️ User installation failed, trying system-wide installation...
    echo 🔐 Installing to system (may require Administrator privileges)...

    pip install -r requirements_pyqt.txt

    if errorlevel 1 (
        echo ERROR: Failed to install packages
        echo.
        echo Troubleshooting options:
        echo   1. Right-click Command Prompt and "Run as administrator"
        echo   2. Run this script again as Administrator
        echo   3. Or manually install: pip install --user PyQt5 requests beautifulsoup4
        pause
        exit /b 1
    ) else (
        echo ✅ Packages installed to system successfully!
    )
) else (
    echo ✅ Packages installed to user directory successfully!
    echo 📍 Installed to: %%APPDATA%%\Python\Python*\site-packages\
)

echo.
echo ✅ All packages installed successfully to system Python!
echo.
echo 🎉 Setup complete!
echo.
echo To run the application:
echo   1. Double-click launch_pyqt_gui.bat
echo   2. Or run: python hackathon_monitor_pyqt.py
echo.
pause
