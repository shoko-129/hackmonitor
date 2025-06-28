#!/usr/bin/env python3
"""
Desktop App Setup Script for Hackathon Monitor
Sets up the Electron desktop application
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil

class DesktopAppSetup:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.platform = platform.system().lower()
        
    def check_prerequisites(self):
        """Check if required tools are available"""
        print("🔍 Checking prerequisites...")
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Node.js: {result.stdout.strip()}")
                node_ok = True
            else:
                node_ok = False
        except FileNotFoundError:
            node_ok = False
        
        if not node_ok:
            print("❌ Node.js not found")
            print("📥 Please install Node.js from: https://nodejs.org/")
            return False
        
        # Check npm
        try:
            result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ npm: {result.stdout.strip()}")
                npm_ok = True
            else:
                npm_ok = False
        except FileNotFoundError:
            npm_ok = False
        
        if not npm_ok:
            print("❌ npm not found")
            print("📥 npm should come with Node.js installation")
            return False
        
        # Check Python
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        print(f"✅ Python: {python_version}")
        
        return True
    
    def install_electron_dependencies(self):
        """Install Electron and build dependencies"""
        print("📦 Installing Electron dependencies...")
        
        try:
            # Install dependencies
            subprocess.run(['npm', 'install'], check=True, cwd=self.project_root)
            print("✅ Electron dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def install_python_dependencies(self):
        """Install Python dependencies"""
        print("🐍 Installing Python dependencies...")
        
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                '-r', 'requirements_crossplatform.txt', '--upgrade'
            ], check=True)
            print("✅ Python dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def create_icons(self):
        """Create application icons"""
        print("🎨 Creating application icons...")
        
        assets_dir = self.project_root / "assets"
        assets_dir.mkdir(exist_ok=True)
        
        logo_path = self.project_root / "logo.png"
        
        if logo_path.exists():
            # Copy logo as PNG icon
            shutil.copy2(logo_path, assets_dir / "icon.png")
            shutil.copy2(logo_path, assets_dir / "tray-icon.png")
            print("✅ Icons created from logo.png")
        else:
            # Create default icon
            self.create_default_icon(assets_dir)
            print("✅ Default icons created")
        
        print("ℹ️ For better icons, convert logo.png to:")
        print("   - Windows: icon.ico")
        print("   - macOS: icon.icns")
        print("   - Use online converters or specialized tools")
    
    def create_default_icon(self, assets_dir):
        """Create a default SVG icon"""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="256" height="256" fill="url(#grad1)" rx="32"/>
  <circle cx="128" cy="128" r="80" fill="white" opacity="0.9"/>
  <text x="128" y="150" text-anchor="middle" fill="#667eea" font-size="80" font-family="Arial, sans-serif">🎯</text>
</svg>'''
        
        with open(assets_dir / "icon.svg", 'w') as f:
            f.write(svg_content)
        
        # Also create a simple PNG version
        try:
            from PIL import Image, ImageDraw
            
            # Create a 256x256 image
            img = Image.new('RGBA', (256, 256), (102, 126, 234, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw a circle
            draw.ellipse([64, 64, 192, 192], fill=(255, 255, 255, 230))
            
            # Save as PNG
            img.save(assets_dir / "icon.png")
            img.resize((32, 32)).save(assets_dir / "tray-icon.png")
            
        except ImportError:
            # PIL not available, just copy the SVG
            shutil.copy2(assets_dir / "icon.svg", assets_dir / "icon.png")
    
    def create_desktop_shortcuts(self):
        """Create desktop shortcuts for web interface"""
        print("🔗 Creating desktop shortcuts...")

        desktop = Path.home() / "Desktop"
        project_path = self.project_root.absolute()

        if self.platform == 'windows':
            # Create Windows batch file shortcut
            shortcut_path = desktop / "Hackathon Monitor.bat"
            with open(shortcut_path, 'w') as f:
                f.write(f'''@echo off
title Hackathon Monitor
echo 🎯 Starting Hackathon Monitor...
cd /d "{project_path}"
python hackathon_monitor_web.py
pause
''')
            print(f"✅ Created Windows shortcut: {shortcut_path}")

        elif self.platform == 'darwin':  # macOS
            # Create macOS command file
            shortcut_path = desktop / "Hackathon Monitor.command"
            with open(shortcut_path, 'w') as f:
                f.write(f'''#!/bin/bash
echo "🎯 Starting Hackathon Monitor..."
cd "{project_path}"
python3 hackathon_monitor_web.py
''')
            shortcut_path.chmod(0o755)
            print(f"✅ Created macOS shortcut: {shortcut_path}")

        elif self.platform == 'linux':
            # Create Linux desktop entry
            shortcut_path = desktop / "hackathon-monitor.desktop"
            with open(shortcut_path, 'w') as f:
                f.write(f'''[Desktop Entry]
Name=Hackathon Monitor
Comment=Monitor hackathon platforms for new events
Exec=python3 "{project_path}/hackathon_monitor_web.py"
Icon={project_path}/logo.png
Type=Application
Terminal=false
Categories=Office;Development;
''')
            shortcut_path.chmod(0o755)
            print(f"✅ Created Linux shortcut: {shortcut_path}")

        return True

    def test_setup(self):
        """Test the setup"""
        print("🧪 Testing setup...")

        # Check if all files exist
        required_files = [
            "package.json",
            "main.js",
            "preload.js",
            "hackathon_monitor_web.py"
        ]

        missing_files = []
        for file_path in required_files:
            if not (self.project_root / file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            print("❌ Missing files:")
            for file_path in missing_files:
                print(f"   - {file_path}")
            return False

        print("✅ All required files present")
        return True
    
    def run_development_mode(self):
        """Run the app in development mode"""
        print("🚀 Starting development mode...")
        print("📍 This will start both Python backend and Electron frontend")
        print("⏹️ Press Ctrl+C to stop")
        
        try:
            subprocess.run(['npm', 'start'], cwd=self.project_root)
        except KeyboardInterrupt:
            print("\n👋 Development mode stopped")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to start development mode: {e}")
    
    def build_app(self, platform_target='current'):
        """Build the desktop application"""
        print(f"🔨 Building desktop application for {platform_target}...")
        
        build_commands = {
            'current': 'npm run build',
            'windows': 'npm run build-win',
            'macos': 'npm run build-mac',
            'linux': 'npm run build-linux',
            'all': 'npm run build'
        }
        
        command = build_commands.get(platform_target, build_commands['current'])
        
        try:
            subprocess.run(command.split(), check=True, cwd=self.project_root)
            print("✅ Build completed successfully!")
            
            # Show build results
            dist_dir = self.project_root / "dist"
            if dist_dir.exists():
                print("\n📦 Built applications:")
                for item in dist_dir.iterdir():
                    if item.is_file():
                        size_mb = item.stat().st_size / (1024 * 1024)
                        print(f"   📄 {item.name} ({size_mb:.1f} MB)")
                    elif item.is_dir():
                        print(f"   📁 {item.name}/")
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def setup(self):
        """Main setup process"""
        print("🎯 Hackathon Monitor - Desktop App Setup")
        print("=" * 45)
        print(f"Platform: {platform.system()} {platform.release()}")
        print()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Install dependencies
        if not self.install_electron_dependencies():
            return False
        
        if not self.install_python_dependencies():
            return False
        
        # Create icons
        self.create_icons()
        
        # Test setup
        if not self.test_setup():
            return False

        # Create desktop shortcuts
        self.create_desktop_shortcuts()

        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. 🚀 Test: python setup-desktop-app.py --dev")
        print("2. 🔨 Build: python setup-desktop-app.py --build")
        print("3. 📦 Distribute the files in dist/ folder")
        print("4. 🔗 Desktop shortcut created for web interface")

        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup Hackathon Monitor Desktop App')
    parser.add_argument('--dev', action='store_true', help='Run in development mode')
    parser.add_argument('--build', choices=['current', 'windows', 'macos', 'linux', 'all'], 
                       default=None, help='Build for specific platform')
    parser.add_argument('--setup-only', action='store_true', help='Only run setup, don\'t build')
    
    args = parser.parse_args()
    
    setup = DesktopAppSetup()
    
    if args.dev:
        # Run development mode
        setup.run_development_mode()
    elif args.build:
        # Build for specific platform
        if setup.check_prerequisites():
            setup.build_app(args.build)
    else:
        # Full setup
        success = setup.setup()
        
        if success and not args.setup_only:
            # Ask user what to do next
            print("\n❓ What would you like to do next?")
            print("1. 🚀 Test in development mode")
            print("2. 🔨 Build desktop application")
            print("3. 🚪 Exit")
            
            try:
                choice = input("\nEnter choice (1-3): ").strip()
                
                if choice == '1':
                    setup.run_development_mode()
                elif choice == '2':
                    platform_choice = input("Build for (current/windows/macos/linux/all): ").strip()
                    if not platform_choice:
                        platform_choice = 'current'
                    setup.build_app(platform_choice)
                else:
                    print("👋 Setup complete! Run with --dev or --build when ready.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")

if __name__ == "__main__":
    main()
