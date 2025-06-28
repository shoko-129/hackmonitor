#!/usr/bin/env python3
"""
Hackathon Monitor - Universal Launcher
Choose your preferred interface: Web, GUI, Terminal, or CLI
"""

import sys
import subprocess
import platform
from pathlib import Path

def check_dependencies():
    """Check which interfaces are available"""
    available = {
        'web': False,
        'gui': False,
        'tui': False,
        'cli': True  # CLI is always available
    }
    
    # Check Flask for web interface
    try:
        import flask
        available['web'] = True
    except ImportError:
        pass
    
    # Check tkinter for GUI
    try:
        import tkinter
        available['gui'] = True
    except ImportError:
        pass
    
    # Check Rich for TUI
    try:
        import rich
        available['tui'] = True
    except ImportError:
        pass
    
    return available

def show_interface_menu():
    """Show interface selection menu"""
    available = check_dependencies()
    
    print("🎯 Hackathon Monitor - Interface Launcher")
    print("=" * 45)
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"Python: {platform.python_version()}")
    print()
    
    print("Available Interfaces:")
    print()
    
    options = []
    
    if available['web']:
        print("1. 🌐 Web Interface (Recommended)")
        print("   • Modern web dashboard")
        print("   • Works on any device")
        print("   • Real-time updates")
        print("   • Mobile-friendly")
        options.append(('web', 'hackathon_monitor_web.py'))
        print()
    
    if available['gui']:
        print(f"{len(options) + 1}. 🖥️ Desktop GUI")
        print("   • Traditional desktop application")
        print("   • Native look and feel")
        print("   • Easy to use")
        options.append(('gui', 'hackathon_monitor_gui_crossplatform.py'))
        print()
    
    if available['tui']:
        print(f"{len(options) + 1}. 📟 Terminal Interface")
        print("   • Modern terminal UI")
        print("   • Rich text and colors")
        print("   • Keyboard navigation")
        options.append(('tui', 'hackathon_monitor_tui.py'))
        print()
    
    print(f"{len(options) + 1}. ⌨️ Command Line")
    print("   • Scriptable interface")
    print("   • Perfect for automation")
    print("   • JSON output support")
    options.append(('cli', 'hackathon_monitor_cli.py'))
    print()
    
    print(f"{len(options) + 1}. 📦 Install Missing Dependencies")
    print(f"{len(options) + 2}. ❓ Help")
    print(f"{len(options) + 3}. 🚪 Exit")
    print()
    
    return options

def install_dependencies():
    """Install missing dependencies"""
    print("📦 Installing Dependencies...")
    print("=" * 30)
    
    dependencies = {
        'Web Interface': 'flask',
        'Terminal Interface': 'rich',
        'All platforms': 'requests beautifulsoup4 openpyxl selenium schedule'
    }
    
    print("This will install:")
    for name, deps in dependencies.items():
        print(f"  • {name}: {deps}")
    print()
    
    confirm = input("Continue? (y/N): ").strip().lower()
    if confirm != 'y':
        return
    
    try:
        # Install all dependencies
        cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements_crossplatform.txt", "--upgrade"]
        print("Running:", " ".join(cmd))
        subprocess.check_call(cmd)
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError:
        print("❌ Installation failed. Try running manually:")
        print("pip install -r requirements_crossplatform.txt")
    
    input("\nPress Enter to continue...")

def show_help():
    """Show help information"""
    print("❓ Hackathon Monitor Help")
    print("=" * 25)
    print()
    
    print("🌐 Web Interface:")
    print("  • Best for most users")
    print("  • Access from any device on your network")
    print("  • Modern, responsive design")
    print("  • Real-time monitoring dashboard")
    print()
    
    print("🖥️ Desktop GUI:")
    print("  • Traditional desktop application")
    print("  • Native operating system integration")
    print("  • Familiar interface for desktop users")
    print()
    
    print("📟 Terminal Interface:")
    print("  • For terminal/command line enthusiasts")
    print("  • Rich text interface with colors")
    print("  • Keyboard-driven navigation")
    print("  • Works over SSH")
    print()
    
    print("⌨️ Command Line:")
    print("  • For automation and scripting")
    print("  • JSON output for integration")
    print("  • Perfect for cron jobs")
    print("  • Minimal resource usage")
    print()
    
    print("📋 Quick Start:")
    print("1. Choose an interface from the menu")
    print("2. The application will start automatically")
    print("3. Follow the on-screen instructions")
    print("4. Check 'hackathons_data.xlsx' for results")
    print()
    
    print("🔧 Troubleshooting:")
    print("• If an interface is missing, install dependencies")
    print("• For web interface: http://localhost:5000")
    print("• For CLI help: python hackathon_monitor_cli.py --help")
    print("• Check config.ini for settings")
    print()
    
    input("Press Enter to continue...")

def launch_interface(interface_type, script_name):
    """Launch the selected interface"""
    script_path = Path(script_name)
    
    if not script_path.exists():
        print(f"❌ Error: {script_name} not found!")
        print("Make sure all files are in the same directory.")
        input("Press Enter to continue...")
        return
    
    print(f"🚀 Starting {interface_type.title()} Interface...")
    print()
    
    try:
        if interface_type == 'web':
            print("🌐 Web interface starting...")
            print("📍 URL: http://localhost:5000")
            print("🔄 Browser will open automatically")
            print("⏹️ Press Ctrl+C to stop")
            print()
        elif interface_type == 'cli':
            print("⌨️ Command Line Interface")
            print("Use --help for available commands")
            print()
        
        # Launch the interface
        subprocess.run([sys.executable, script_name])
        
    except KeyboardInterrupt:
        print("\n👋 Interface stopped by user")
    except Exception as e:
        print(f"❌ Error starting interface: {e}")
        input("Press Enter to continue...")

def main():
    """Main launcher function"""
    while True:
        try:
            # Clear screen
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            # Show menu
            options = show_interface_menu()
            
            # Get user choice
            try:
                choice = input("Enter your choice: ").strip()
                choice_num = int(choice) - 1
            except ValueError:
                print("❌ Invalid choice. Please enter a number.")
                input("Press Enter to continue...")
                continue
            
            # Handle choice
            if 0 <= choice_num < len(options):
                interface_type, script_name = options[choice_num]
                launch_interface(interface_type, script_name)
            
            elif choice_num == len(options):
                install_dependencies()
            
            elif choice_num == len(options) + 1:
                show_help()
            
            elif choice_num == len(options) + 2:
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
                input("Press Enter to continue...")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
