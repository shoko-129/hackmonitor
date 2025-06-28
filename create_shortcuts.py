#!/usr/bin/env python3
"""
Create Desktop Shortcuts for Hackathon Monitor
Creates platform-specific desktop shortcuts for easy access
"""

import os
import platform
from pathlib import Path
import sys

class ShortcutCreator:
    def __init__(self):
        self.platform = platform.system().lower()
        self.project_root = Path(__file__).parent.absolute()
        self.desktop = Path.home() / "Desktop"
        
    def create_web_interface_shortcut(self):
        """Create desktop shortcut for web interface"""
        print(f"🔗 Creating web interface shortcut for {platform.system()}...")
        
        if self.platform == 'windows':
            shortcut_path = self.desktop / "Hackathon Monitor.bat"
            content = f'''@echo off
title Hackathon Monitor - Web Interface
color 0A
echo.
echo  🎯 Hackathon Monitor - Web Interface
echo  ===================================
echo.
echo  Starting web interface...
echo  Open browser to: http://localhost:5000
echo.

cd /d "{self.project_root}"

REM Try different Python commands
python hackathon_monitor_web.py 2>nul
if %ERRORLEVEL% NEQ 0 (
    py hackathon_monitor_web.py 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ ERROR: Could not start web interface
        echo Please ensure Python is installed and in PATH
        echo.
        pause
    )
)
'''
            
        elif self.platform == 'darwin':  # macOS
            shortcut_path = self.desktop / "Hackathon Monitor.command"
            content = f'''#!/bin/bash
echo "🎯 Hackathon Monitor - Web Interface"
echo "==================================="
echo ""
echo "Starting web interface..."
echo "Open browser to: http://localhost:5000"
echo ""

cd "{self.project_root}"

# Try different Python commands
if command -v python3 &> /dev/null; then
    python3 hackathon_monitor_web.py
elif command -v python &> /dev/null; then
    python hackathon_monitor_web.py
else
    echo "❌ ERROR: Python not found"
    echo "Please install Python 3.8+"
    read -p "Press Enter to exit..."
fi
'''
            
        elif self.platform == 'linux':
            shortcut_path = self.desktop / "hackathon-monitor.desktop"
            content = f'''[Desktop Entry]
Name=Hackathon Monitor
Comment=Monitor hackathon platforms for new events
Exec=python3 "{self.project_root}/hackathon_monitor_web.py"
Icon={self.project_root}/logo.png
Type=Application
Terminal=false
Categories=Office;Development;Network;
StartupNotify=true
'''
        
        # Write the shortcut file
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable on Unix systems
        if self.platform in ['darwin', 'linux']:
            shortcut_path.chmod(0o755)
        
        print(f"✅ Created: {shortcut_path}")
        return shortcut_path
    
    def create_launcher_shortcut(self):
        """Create desktop shortcut for universal launcher"""
        print(f"🚀 Creating launcher shortcut for {platform.system()}...")
        
        if self.platform == 'windows':
            shortcut_path = self.desktop / "Hackathon Monitor Launcher.bat"
            content = f'''@echo off
title Hackathon Monitor - Universal Launcher
color 0B
echo.
echo  🚀 Hackathon Monitor - Universal Launcher
echo  ========================================
echo.
echo  Choose your preferred interface...
echo.

cd /d "{self.project_root}"
python hackathon_monitor_launcher.py
'''
            
        elif self.platform == 'darwin':  # macOS
            shortcut_path = self.desktop / "Hackathon Monitor Launcher.command"
            content = f'''#!/bin/bash
echo "🚀 Hackathon Monitor - Universal Launcher"
echo "========================================"
echo ""
echo "Choose your preferred interface..."
echo ""

cd "{self.project_root}"
python3 hackathon_monitor_launcher.py
'''
            
        elif self.platform == 'linux':
            shortcut_path = self.desktop / "hackathon-monitor-launcher.desktop"
            content = f'''[Desktop Entry]
Name=Hackathon Monitor Launcher
Comment=Choose your preferred interface for Hackathon Monitor
Exec=python3 "{self.project_root}/hackathon_monitor_launcher.py"
Icon={self.project_root}/logo.png
Type=Application
Terminal=true
Categories=Office;Development;Network;
StartupNotify=true
'''
        
        # Write the shortcut file
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable on Unix systems
        if self.platform in ['darwin', 'linux']:
            shortcut_path.chmod(0o755)
        
        print(f"✅ Created: {shortcut_path}")
        return shortcut_path
    
    def create_cli_shortcut(self):
        """Create desktop shortcut for CLI interface"""
        print(f"⌨️ Creating CLI shortcut for {platform.system()}...")
        
        if self.platform == 'windows':
            shortcut_path = self.desktop / "Hackathon Monitor CLI.bat"
            content = f'''@echo off
title Hackathon Monitor - Command Line Interface
color 0E
echo.
echo  ⌨️ Hackathon Monitor - Command Line Interface
echo  ============================================
echo.
echo  Available commands:
echo    scrape    - Run single scraping cycle
echo    monitor   - Start continuous monitoring
echo    stats     - Show statistics
echo    export    - Export data
echo.

cd /d "{self.project_root}"

:menu
echo.
set /p choice="Enter command (or 'help' for more options): "

if "%choice%"=="scrape" (
    python hackathon_monitor_cli.py scrape
    goto menu
)
if "%choice%"=="monitor" (
    python hackathon_monitor_cli.py monitor
    goto menu
)
if "%choice%"=="stats" (
    python hackathon_monitor_cli.py stats
    goto menu
)
if "%choice%"=="export" (
    python hackathon_monitor_cli.py export
    goto menu
)
if "%choice%"=="help" (
    python hackathon_monitor_cli.py --help
    goto menu
)
if "%choice%"=="exit" (
    exit
)

echo Invalid command. Try: scrape, monitor, stats, export, help, exit
goto menu
'''
            
        elif self.platform == 'darwin':  # macOS
            shortcut_path = self.desktop / "Hackathon Monitor CLI.command"
            content = f'''#!/bin/bash
echo "⌨️ Hackathon Monitor - Command Line Interface"
echo "============================================"
echo ""
echo "Available commands:"
echo "  scrape    - Run single scraping cycle"
echo "  monitor   - Start continuous monitoring"
echo "  stats     - Show statistics"
echo "  export    - Export data"
echo ""

cd "{self.project_root}"

while true; do
    echo ""
    read -p "Enter command (or 'help' for more options): " choice
    
    case $choice in
        scrape)
            python3 hackathon_monitor_cli.py scrape
            ;;
        monitor)
            python3 hackathon_monitor_cli.py monitor
            ;;
        stats)
            python3 hackathon_monitor_cli.py stats
            ;;
        export)
            python3 hackathon_monitor_cli.py export
            ;;
        help)
            python3 hackathon_monitor_cli.py --help
            ;;
        exit)
            break
            ;;
        *)
            echo "Invalid command. Try: scrape, monitor, stats, export, help, exit"
            ;;
    esac
done
'''
            
        elif self.platform == 'linux':
            shortcut_path = self.desktop / "hackathon-monitor-cli.desktop"
            content = f'''[Desktop Entry]
Name=Hackathon Monitor CLI
Comment=Command line interface for Hackathon Monitor
Exec=gnome-terminal -- python3 "{self.project_root}/hackathon_monitor_cli.py" --help
Icon={self.project_root}/logo.png
Type=Application
Terminal=true
Categories=Office;Development;Network;ConsoleOnly;
StartupNotify=true
'''
        
        # Write the shortcut file
        with open(shortcut_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Make executable on Unix systems
        if self.platform in ['darwin', 'linux']:
            shortcut_path.chmod(0o755)
        
        print(f"✅ Created: {shortcut_path}")
        return shortcut_path
    
    def create_all_shortcuts(self):
        """Create all desktop shortcuts"""
        print(f"🔗 Creating desktop shortcuts for {platform.system()}...")
        print(f"📁 Desktop location: {self.desktop}")
        print()
        
        shortcuts = []
        
        try:
            # Create web interface shortcut
            shortcuts.append(self.create_web_interface_shortcut())
            
            # Create launcher shortcut
            shortcuts.append(self.create_launcher_shortcut())
            
            # Create CLI shortcut
            shortcuts.append(self.create_cli_shortcut())
            
            print()
            print("🎉 All shortcuts created successfully!")
            print()
            print("📋 Created shortcuts:")
            for shortcut in shortcuts:
                print(f"   🔗 {shortcut.name}")
            
            print()
            print("🚀 How to use:")
            if self.platform == 'windows':
                print("   • Double-click any .bat file on desktop")
                print("   • Or run from Start Menu")
            elif self.platform == 'darwin':
                print("   • Double-click any .command file on desktop")
                print("   • Or find in Applications folder")
            elif self.platform == 'linux':
                print("   • Double-click any .desktop file")
                print("   • Or find in Applications menu")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating shortcuts: {e}")
            return False

def main():
    print("🔗 Hackathon Monitor - Desktop Shortcut Creator")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    creator = ShortcutCreator()
    
    # Check if desktop folder exists
    if not creator.desktop.exists():
        print(f"❌ Desktop folder not found: {creator.desktop}")
        print("Please ensure the Desktop folder exists")
        return False
    
    # Create shortcuts
    success = creator.create_all_shortcuts()
    
    if success:
        print()
        print("✅ Desktop shortcuts created successfully!")
        print("🎯 Your Hackathon Monitor is now easily accessible from desktop!")
    else:
        print()
        print("❌ Failed to create some shortcuts")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
