@echo off
echo ========================================
echo   Windows EXE Installer Builder
echo ========================================
echo.

echo 🪟 Building standalone Windows installer EXE...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

echo ✅ Python found
python --version

echo.
echo � Installing required dependencies...
echo Installing PyInstaller...
python -m pip install pyinstaller --upgrade
if errorlevel 1 (
    echo ⚠️ Failed with pip, trying with --user flag...
    python -m pip install --user pyinstaller --upgrade
)

echo Installing pywin32...
python -m pip install pywin32 --upgrade
if errorlevel 1 (
    echo ⚠️ Failed with pip, trying with --user flag...
    python -m pip install --user pywin32 --upgrade
)

echo.
echo �🔨 Building EXE installer...
python build_windows_exe.py
if errorlevel 1 (
    echo.
    echo ❌ Build failed! Common solutions:
    echo 1. Run as Administrator
    echo 2. Disable antivirus temporarily
    echo 3. Check if all files exist
    echo 4. Try: python -m pip install --upgrade pip setuptools
    echo.
    pause
    exit /b 1
)

echo.
echo 🎉 Build process completed!
echo Check for HackathonMonitor_Installer.exe in this folder
echo.
pause
