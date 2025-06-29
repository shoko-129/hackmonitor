#!/usr/bin/env python3
"""
Simple EXE Creator for Hackathon Monitor
Creates a standalone EXE file using PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def install_pyinstaller():
    """Install PyInstaller"""
    print("📦 Installing PyInstaller...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        print("✅ PyInstaller installed successfully")
        return True
    except subprocess.CalledProcessError:
        try:
            print("⚠️ Trying with --user flag...")
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"], check=True)
            print("✅ PyInstaller installed with --user flag")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install PyInstaller")
            return False

def create_exe():
    """Create the EXE file"""
    print("🔨 Creating EXE file...")
    
    # Check if source file exists
    if not Path("windows_standalone_installer.py").exists():
        print("❌ Error: windows_standalone_installer.py not found!")
        return False
    
    # Check if icon exists
    icon_arg = []
    if Path("logo.png").exists():
        icon_arg = ["--icon", "logo.png"]
    
    try:
        cmd = [
            sys.executable, "-m", "PyInstaller",
            "--onefile",
            "--windowed",
            "--name", "HackathonMonitor_Installer"
        ] + icon_arg + ["windows_standalone_installer.py"]
        
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ EXE created successfully!")
            
            # Copy EXE to main folder
            exe_path = Path("dist") / "HackathonMonitor_Installer.exe"
            if exe_path.exists():
                shutil.copy2(exe_path, "HackathonMonitor_Installer.exe")
                print(f"✅ EXE copied to: HackathonMonitor_Installer.exe")
            
            return True
        else:
            print("❌ PyInstaller failed:")
            print(f"Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating EXE: {e}")
        return False

def main():
    """Main function"""
    print("🎯 Hackathon Monitor EXE Creator")
    print("=" * 40)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    
    # Install PyInstaller
    if not install_pyinstaller():
        print("\n❌ Cannot proceed without PyInstaller")
        input("Press Enter to exit...")
        return
    
    # Create EXE
    if create_exe():
        print("\n🎉 SUCCESS!")
        print("📦 EXE file created: HackathonMonitor_Installer.exe")
        print("\n📋 Next steps:")
        print("1. Test the EXE file")
        print("2. Upload it for users to download")
        print("3. Users just double-click to install")
    else:
        print("\n❌ FAILED!")
        print("💡 Try these solutions:")
        print("1. Run as Administrator")
        print("2. Disable antivirus temporarily")
        print("3. Check if all files are present")
        print("4. Update pip: python -m pip install --upgrade pip")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
