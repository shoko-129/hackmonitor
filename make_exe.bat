@echo off
echo ==========================================
echo    Creating Hackathon Monitor EXE
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install PyInstaller
echo Installing PyInstaller...
python -m pip install pyinstaller
if errorlevel 1 (
    echo Trying with --user flag...
    python -m pip install --user pyinstaller
)
echo.

REM Create the EXE
echo Creating EXE file...
python -m PyInstaller --onefile --windowed --name "HackathonMonitor_Installer" --icon logo.png windows_standalone_installer.py

if errorlevel 1 (
    echo.
    echo BUILD FAILED!
    echo Try these solutions:
    echo 1. Run this file as Administrator
    echo 2. Temporarily disable antivirus
    echo 3. Make sure all files are in the same folder
    pause
    exit /b 1
)

echo.
echo SUCCESS! EXE file created.
echo.
echo Look for: dist\HackathonMonitor_Installer.exe
echo.

REM Copy EXE to main folder
if exist "dist\HackathonMonitor_Installer.exe" (
    copy "dist\HackathonMonitor_Installer.exe" "HackathonMonitor_Installer.exe"
    echo EXE copied to main folder: HackathonMonitor_Installer.exe
)

echo.
echo DONE! You can now distribute HackathonMonitor_Installer.exe
pause
