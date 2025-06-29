#!/usr/bin/env python3
"""
Build Windows EXE Installer
Creates a standalone EXE file that downloads and installs everything
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class WindowsEXEBuilder:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.dist_dir = self.project_dir / "dist"
        self.build_dir = self.project_dir / "build"
        self.exe_name = "HackathonMonitor_Installer.exe"
        
    def clean_previous_builds(self):
        """Remove previous build artifacts"""
        print("🧹 Cleaning previous builds...")
        
        dirs_to_clean = [self.dist_dir, self.build_dir]
        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   Removed: {dir_path}")
        
        exe_file = self.project_dir / self.exe_name
        if exe_file.exists():
            exe_file.unlink()
            print(f"   Removed: {exe_file}")
        
        print("✅ Cleanup completed")
    
    def install_build_dependencies(self):
        """Install required build tools"""
        print("📦 Installing build dependencies...")

        dependencies = [
            "pyinstaller>=5.0",
            "pywin32>=307",
        ]

        for dep in dependencies:
            try:
                print(f"   Installing {dep}...")
                result = subprocess.run([
                    sys.executable, "-m", "pip", "install", dep
                ], capture_output=True, text=True, check=True)
                print(f"   ✅ {dep} installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"   ⚠️ Failed to install {dep}: {e}")
                try:
                    # Try with --user flag
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", "--user", dep
                    ], check=True)
                    print(f"   ✅ {dep} installed with --user flag")
                except subprocess.CalledProcessError:
                    print(f"   ❌ Could not install {dep}")
                    return False
        
        print("✅ Build dependencies installed")
        return True
    
    def create_pyinstaller_spec(self):
        """Create PyInstaller spec file for the installer"""
        print("📝 Creating PyInstaller spec file...")
        
        spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['windows_standalone_installer.py'],
    pathex=['{self.project_dir}'],
    binaries=[],
    datas=[
        ('logo.png', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'urllib.request',
        'zipfile',
        'winreg',
        'win32com.client',
        'threading',
        'tempfile',
        'json',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{self.exe_name.replace(".exe", "")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    cofile=None,
    icon='logo.png',
    version_file=None,
    uac_admin=True,
)
'''
        
        spec_file = self.project_dir / "windows_installer.spec"
        with open(spec_file, 'w') as f:
            f.write(spec_content)
        
        print(f"✅ Created spec file: {spec_file}")
        return spec_file
    
    def build_exe(self):
        """Build the EXE using PyInstaller"""
        print("🔨 Building EXE with PyInstaller...")
        
        spec_file = self.create_pyinstaller_spec()
        
        try:
            cmd = [sys.executable, "-m", "PyInstaller", "--clean", str(spec_file)]
            print(f"   Running: {' '.join(cmd)}")
            
            result = subprocess.run(cmd, cwd=self.project_dir, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ EXE built successfully")
                
                # Move EXE to project root
                built_exe = self.dist_dir / f"{self.exe_name.replace('.exe', '')}.exe"
                final_exe = self.project_dir / self.exe_name
                
                if built_exe.exists():
                    shutil.move(built_exe, final_exe)
                    print(f"✅ EXE moved to: {final_exe}")
                
                return True
            else:
                print(f"❌ PyInstaller failed:")
                print(f"   stdout: {result.stdout}")
                print(f"   stderr: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error running PyInstaller: {e}")
            return False
    
    def create_version_info(self):
        """Create version info file for the EXE"""
        print("📝 Creating version info...")
        
        version_content = '''# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1,0,0,0),
    prodvers=(1,0,0,0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'Hackathon Monitor Team'),
        StringStruct(u'FileDescription', u'Hackathon Monitor Installer'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'HackathonMonitor_Installer'),
        StringStruct(u'LegalCopyright', u'© 2024 Hackathon Monitor Team'),
        StringStruct(u'OriginalFilename', u'HackathonMonitor_Installer.exe'),
        StringStruct(u'ProductName', u'Hackathon Monitor'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
        
        version_file = self.project_dir / "version_info.txt"
        with open(version_file, 'w') as f:
            f.write(version_content)
        
        print(f"✅ Created version info: {version_file}")
        return version_file
    
    def build_complete_installer(self):
        """Build the complete installer EXE"""
        print("🚀 Building Complete Windows Installer EXE")
        print("=" * 60)
        
        # Step 1: Clean previous builds
        self.clean_previous_builds()
        
        # Step 2: Install build dependencies
        if not self.install_build_dependencies():
            print("❌ Failed to install build dependencies")
            return False
        
        # Step 3: Create version info
        self.create_version_info()
        
        # Step 4: Build EXE
        if not self.build_exe():
            print("❌ Failed to build EXE")
            return False
        
        print("✅ Windows installer EXE creation completed!")
        return True

def main():
    """Main execution function"""
    print("🪟 Hackathon Monitor Windows EXE Builder")
    print("=" * 60)
    
    if sys.platform != "win32":
        print("⚠️ This EXE builder is designed for Windows")
        print("📋 Please run this on a Windows system")
        return
    
    builder = WindowsEXEBuilder()
    
    try:
        success = builder.build_complete_installer()
        
        if success:
            print("\n🎉 SUCCESS!")
            print("=" * 60)
            print("✅ Windows installer EXE has been created")
            print(f"📦 File: {builder.exe_name}")
            print(f"📍 Location: {builder.project_dir}")
            print("\n🚀 Distribution Instructions:")
            print(f"1. Share the file: {builder.exe_name}")
            print("2. Users double-click to install")
            print("3. Installer downloads everything automatically")
            print("4. Creates desktop shortcut")
            print("5. Checks for Chrome installation")
            print("\n📋 Features:")
            print("• Downloads latest version from GitHub")
            print("• Installs Python if needed")
            print("• Installs all dependencies")
            print("• Creates desktop shortcut")
            print("• Checks Chrome installation")
            print("• Professional GUI installer")
            
        else:
            print("\n❌ FAILED!")
            print("Could not create EXE. Check the error messages above.")
            
    except KeyboardInterrupt:
        print("\n⚠️ Build cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
