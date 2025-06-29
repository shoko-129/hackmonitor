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
echo 🔨 Building EXE installer...
python build_windows_exe.py

echo.
echo 🎉 Build process completed!
echo Check for HackathonMonitor_Installer.exe in this folder
echo.
pause
