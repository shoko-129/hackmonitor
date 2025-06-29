@echo off
echo ========================================
echo   Simple EXE Builder (Alternative)
echo ========================================
echo.

REM Check Python
python --version
if errorlevel 1 (
    echo Python not found! Install Python first.
    pause
    exit /b 1
)

echo.
echo Installing PyInstaller...
python -m pip install pyinstaller
echo.

echo Building simple EXE...
python -m PyInstaller --onefile --windowed --name "HackathonMonitor_Simple" --icon logo.png windows_standalone_installer.py

echo.
echo Done! Check dist folder for HackathonMonitor_Simple.exe
pause
