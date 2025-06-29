#!/usr/bin/env python3
"""
Windows Standalone Installer for Hackathon Monitor
Creates a single EXE file that downloads and installs everything
"""

import os
import sys
import subprocess
import urllib.request
import zipfile
import shutil
import winreg
from pathlib import Path
import tempfile
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import json

class HackathonMonitorInstaller:
    def __init__(self):
        self.install_dir = Path("C:/Program Files/Hackathon Monitor")
        self.temp_dir = Path(tempfile.gettempdir()) / "hackathon_monitor_install"
        self.github_repo = "https://github.com/shoko-129/hackmonitor"
        self.download_url = "https://github.com/shoko-129/hackmonitor/archive/refs/heads/main.zip"
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Hackathon Monitor Installer")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to install")
        
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the installer GUI"""
        # Title
        title_label = tk.Label(self.root, text="🎯 Hackathon Monitor Installer", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # Description
        desc_text = """Professional Hackathon Monitoring Application

This installer will:
• Download the latest version from GitHub
• Install Python dependencies automatically
• Create desktop shortcut
• Check for Google Chrome
• Set up the complete application"""
        
        desc_label = tk.Label(self.root, text=desc_text, justify=tk.LEFT)
        desc_label.pack(pady=10, padx=20)
        
        # Installation directory
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(dir_frame, text="Install to:").pack(anchor=tk.W)
        self.dir_var = tk.StringVar(value=str(self.install_dir))
        dir_entry = tk.Entry(dir_frame, textvariable=self.dir_var, width=60)
        dir_entry.pack(fill=tk.X, pady=5)
        
        # Progress bar
        progress_frame = tk.Frame(self.root)
        progress_frame.pack(pady=20, padx=20, fill=tk.X)
        
        tk.Label(progress_frame, text="Progress:").pack(anchor=tk.W)
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        # Status label
        self.status_label = tk.Label(progress_frame, textvariable=self.status_var)
        self.status_label.pack(anchor=tk.W, pady=5)
        
        # Buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=20)
        
        self.install_btn = tk.Button(button_frame, text="Install", 
                                    command=self.start_installation,
                                    bg="#4CAF50", fg="white", 
                                    font=("Arial", 12, "bold"),
                                    padx=30, pady=10)
        self.install_btn.pack(side=tk.LEFT, padx=10)
        
        self.cancel_btn = tk.Button(button_frame, text="Cancel", 
                                   command=self.root.quit,
                                   padx=30, pady=10)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
    def update_progress(self, value, status):
        """Update progress bar and status"""
        self.progress_var.set(value)
        self.status_var.set(status)
        self.root.update()
        
    def check_admin_rights(self):
        """Check if running with admin rights"""
        try:
            # Try to write to a system directory
            test_file = Path("C:/Windows/Temp/admin_test.txt")
            test_file.write_text("test")
            test_file.unlink()
            return True
        except:
            return False
            
    def request_admin_rights(self):
        """Request admin rights"""
        if not self.check_admin_rights():
            messagebox.showwarning("Admin Rights Required", 
                                 "This installer needs administrator rights to install to Program Files.\n\n"
                                 "Please run this installer as Administrator.")
            return False
        return True
        
    def check_python(self):
        """Check if Python is installed"""
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return True
        except:
            pass
        return False
        
    def install_python(self):
        """Download and install Python"""
        self.update_progress(10, "Downloading Python installer...")
        
        python_url = "https://www.python.org/ftp/python/3.11.7/python-3.11.7-amd64.exe"
        python_installer = self.temp_dir / "python_installer.exe"
        
        try:
            urllib.request.urlretrieve(python_url, python_installer)
            
            self.update_progress(20, "Installing Python...")
            
            # Install Python silently
            cmd = [str(python_installer), "/quiet", "InstallAllUsers=1", 
                   "PrependPath=1", "Include_test=0"]
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0:
                self.update_progress(30, "Python installed successfully")
                return True
            else:
                raise Exception("Python installation failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install Python: {e}")
            return False
            
    def download_application(self):
        """Download the application from GitHub"""
        self.update_progress(40, "Downloading Hackathon Monitor...")
        
        try:
            # Create temp directory
            self.temp_dir.mkdir(exist_ok=True)
            
            # Download ZIP file
            zip_file = self.temp_dir / "hackathon_monitor.zip"
            urllib.request.urlretrieve(self.download_url, zip_file)
            
            self.update_progress(50, "Extracting files...")
            
            # Extract ZIP file
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(self.temp_dir)
            
            # Find extracted folder
            extracted_folders = [f for f in self.temp_dir.iterdir() if f.is_dir()]
            if extracted_folders:
                self.source_dir = extracted_folders[0]
                return True
            else:
                raise Exception("Could not find extracted files")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download application: {e}")
            return False
            
    def install_application(self):
        """Install the application"""
        self.update_progress(60, "Installing application...")
        
        try:
            # Create installation directory
            self.install_dir = Path(self.dir_var.get())
            self.install_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files
            files_to_copy = [
                "hackathon_monitor_pyqt.py",
                "config.ini",
                "logo.png",
                "LICENSE",
                "README.md",
                "requirements_pyqt.txt",
                "scrapers",
                "storage",
                "notifications"
            ]
            
            for item in files_to_copy:
                src = self.source_dir / item
                dst = self.install_dir / item
                
                if src.exists():
                    if src.is_dir():
                        if dst.exists():
                            shutil.rmtree(dst)
                        shutil.copytree(src, dst)
                    else:
                        shutil.copy2(src, dst)
            
            self.update_progress(70, "Installing Python dependencies...")
            
            # Install Python dependencies
            requirements_file = self.install_dir / "requirements_pyqt.txt"
            if requirements_file.exists():
                cmd = [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    # Try with --user flag
                    cmd = [sys.executable, "-m", "pip", "install", "--user", "-r", str(requirements_file)]
                    subprocess.run(cmd, capture_output=True, text=True)
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install application: {e}")
            return False
            
    def create_desktop_shortcut(self):
        """Create desktop shortcut"""
        self.update_progress(80, "Creating desktop shortcut...")
        
        try:
            import win32com.client
            
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "Hackathon Monitor.lnk"
            
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(str(shortcut_path))
            shortcut.Targetpath = sys.executable
            shortcut.Arguments = f'"{self.install_dir / "hackathon_monitor_pyqt.py"}"'
            shortcut.WorkingDirectory = str(self.install_dir)
            shortcut.IconLocation = str(self.install_dir / "logo.png")
            shortcut.save()
            
            return True
            
        except Exception as e:
            # Fallback: create batch file
            try:
                batch_file = desktop / "Hackathon Monitor.bat"
                with open(batch_file, 'w') as f:
                    f.write('@echo off\n')
                    f.write(f'cd /d "{self.install_dir}"\n')
                    f.write(f'"{sys.executable}" hackathon_monitor_pyqt.py\n')
                    f.write('pause\n')
                return True
            except:
                return False

    def add_to_registry(self):
        """Add application to Windows registry"""
        try:
            # Add to Add/Remove Programs
            key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\HackathonMonitor"
            key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, key_path)

            winreg.SetValueEx(key, "DisplayName", 0, winreg.REG_SZ, "Hackathon Monitor")
            winreg.SetValueEx(key, "DisplayVersion", 0, winreg.REG_SZ, "1.0.0")
            winreg.SetValueEx(key, "Publisher", 0, winreg.REG_SZ, "Hackathon Monitor Team")
            winreg.SetValueEx(key, "InstallLocation", 0, winreg.REG_SZ, str(self.install_dir))
            winreg.SetValueEx(key, "DisplayIcon", 0, winreg.REG_SZ, str(self.install_dir / "logo.png"))

            winreg.CloseKey(key)
            return True
        except:
            return False
                
    def check_chrome(self):
        """Check if Chrome is installed"""
        self.update_progress(90, "Checking for Google Chrome...")
        
        try:
            # Check registry for Chrome
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            return False
            
    def cleanup(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except:
            pass
            
    def start_installation(self):
        """Start the installation process"""
        def install_thread():
            try:
                # Check admin rights
                if not self.request_admin_rights():
                    return
                
                # Check Python
                if not self.check_python():
                    if not self.install_python():
                        return
                
                # Download application
                if not self.download_application():
                    return
                
                # Install application
                if not self.install_application():
                    return
                
                # Create desktop shortcut
                self.create_desktop_shortcut()
                
                # Check Chrome
                chrome_installed = self.check_chrome()
                
                # Cleanup
                self.cleanup()
                
                # Success message
                self.update_progress(100, "Installation completed!")
                
                success_msg = "✅ Hackathon Monitor installed successfully!\n\n"
                success_msg += f"📍 Installed to: {self.install_dir}\n"
                success_msg += "🖥️ Desktop shortcut created\n\n"
                
                if not chrome_installed:
                    success_msg += "⚠️ Google Chrome is not installed\n"
                    success_msg += "📥 Please install Chrome for web scraping:\n"
                    success_msg += "https://www.google.com/chrome/"
                else:
                    success_msg += "✅ Google Chrome detected"
                
                messagebox.showinfo("Installation Complete", success_msg)
                
                # Enable buttons
                self.install_btn.config(state=tk.NORMAL, text="Install")
                self.cancel_btn.config(text="Close")
                
            except Exception as e:
                messagebox.showerror("Installation Error", f"Installation failed: {e}")
                self.install_btn.config(state=tk.NORMAL, text="Install")
        
        # Disable install button
        self.install_btn.config(state=tk.DISABLED, text="Installing...")
        
        # Start installation in separate thread
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
    def run(self):
        """Run the installer"""
        self.root.mainloop()

def main():
    """Main function"""
    try:
        installer = HackathonMonitorInstaller()
        installer.run()
    except Exception as e:
        messagebox.showerror("Error", f"Installer failed to start: {e}")

if __name__ == "__main__":
    main()
