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
        
        # Create GUI with enhanced styling
        self.root = tk.Tk()
        self.root.title("Hackathon Monitor Installer")
        self.root.geometry("650x700")
        self.root.resizable(False, False)

        # Center the window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (650 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"650x700+{x}+{y}")

        # Set window icon if available
        try:
            if hasattr(self, 'logo_path') and self.logo_path.exists():
                self.root.iconbitmap(str(self.logo_path))
        except:
            pass
        
        # Variables
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready to install")
        self.installing = False  # Prevent multiple installations
        self.silent_mode = False  # Control popup suppression during installation

        self.setup_gui()

    def browse_location(self):
        """Browse for installation location"""
        try:
            # Simple approach - just open the dialog without initial directory first
            folder = filedialog.askdirectory(title="Select Installation Directory")

            if folder:
                # Convert forward slashes to backslashes on Windows
                import os
                folder = os.path.normpath(folder)
                self.dir_var.set(folder)
                print(f"[+] Selected installation directory: {folder}")
            else:
                print("[i] No folder selected")

        except Exception as e:
            print(f"[-] Browse error: {e}")
            # Try even simpler approach
            try:
                import tkinter.filedialog as fd
                folder = fd.askdirectory()
                if folder:
                    self.dir_var.set(folder)
                    print(f"[+] Simple browse success: {folder}")
            except Exception as e2:
                print(f"[-] Simple browse failed: {e2}")
                print("[!] Folder browser not available - please type path manually")

    def on_python_deps_change(self):
        """Handle Python dependencies checkbox change"""
        if self.python_deps_var.get():
            print("[+] Python dependencies will be installed automatically")
        else:
            print("[!] Python dependencies installation disabled")

    def on_shortcut_change(self):
        """Handle desktop shortcut checkbox change"""
        if self.desktop_shortcut_var.get():
            print("[+] Desktop shortcut will be created")
        else:
            print("[!] Desktop shortcut creation disabled")

    def setup_gui(self):
        """Setup the installer GUI with enhanced styling"""
        # Configure main window with gradient-like effect
        self.root.configure(bg='#f8f9fa')

        # Header with version - enhanced styling
        header_frame = tk.Frame(self.root, bg='#e9ecef', height=65, relief='flat')
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)

        # Add subtle border at bottom of header
        header_border = tk.Frame(header_frame, bg='#dee2e6', height=1)
        header_border.pack(side=tk.BOTTOM, fill=tk.X)

        version_label = tk.Label(header_frame, text="Hackathon_monitor v1.0.0",
                                font=("Arial", 11, "normal"), bg='#e9ecef', fg='#495057')
        version_label.pack(anchor=tk.W, padx=25, pady=22)

        # Main content frame with better spacing
        content_frame = tk.Frame(self.root, bg='#f8f9fa')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=25)

        # Title with enhanced typography
        title_label = tk.Label(content_frame, text="Hackathon monitor installer",
                              font=("Arial", 20, "bold"), bg='#f8f9fa', fg='#212529')
        title_label.pack(anchor=tk.W, pady=(0, 35))

        # Checkboxes frame with enhanced styling
        checkbox_frame = tk.Frame(content_frame, bg='#f8f9fa')
        checkbox_frame.pack(fill=tk.X, pady=(0, 35))

        # Python Dependencies checkbox with cross-platform styling
        self.python_deps_var = tk.BooleanVar(value=True)
        python_checkbox = tk.Checkbutton(checkbox_frame,
                                        text="Python Dependencies automatically",
                                        variable=self.python_deps_var,
                                        font=("Arial", 12),
                                        bg='#f8f9fa', fg='#495057',
                                        activebackground='#f8f9fa',
                                        activeforeground='#212529',
                                        selectcolor='#ffffff',
                                        borderwidth=0,
                                        highlightthickness=0,
                                        command=self.on_python_deps_change)
        python_checkbox.pack(anchor=tk.W, pady=8)

        # Desktop Shortcut checkbox with cross-platform styling
        self.desktop_shortcut_var = tk.BooleanVar(value=True)
        shortcut_checkbox = tk.Checkbutton(checkbox_frame,
                                          text="Create desktop Shortcut",
                                          variable=self.desktop_shortcut_var,
                                          font=("Arial", 12),
                                          bg='#f8f9fa', fg='#495057',
                                          activebackground='#f8f9fa',
                                          activeforeground='#212529',
                                          selectcolor='#ffffff',
                                          borderwidth=0,
                                          highlightthickness=0,
                                          command=self.on_shortcut_change)
        shortcut_checkbox.pack(anchor=tk.W, pady=8)

        # Location section with enhanced styling
        location_frame = tk.Frame(content_frame, bg='#f8f9fa')
        location_frame.pack(fill=tk.X, pady=(25, 0))

        location_label = tk.Label(location_frame, text="Location :",
                                 font=("Segoe UI", 12, "normal"), bg='#f8f9fa', fg='#495057')
        location_label.pack(anchor=tk.W, pady=(0, 8))

        # Location entry and browse button with modern styling
        location_entry_frame = tk.Frame(location_frame, bg='#f8f9fa')
        location_entry_frame.pack(fill=tk.X, pady=(0, 25))

        self.dir_var = tk.StringVar(value=str(self.install_dir))
        location_entry = tk.Entry(location_entry_frame, textvariable=self.dir_var,
                                 font=("Segoe UI", 11), bg='#ffffff', fg='#495057',
                                 relief='solid', bd=1, borderwidth=1,
                                 highlightthickness=1, highlightcolor='#007bff',
                                 highlightbackground='#ced4da')
        location_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=12)

        # Add tooltip-like behavior with better UX
        def on_entry_click(event):
            if location_entry.get() == str(self.install_dir):
                location_entry.select_range(0, tk.END)

        def on_entry_focus_in(event):
            location_entry.config(highlightbackground='#007bff')

        def on_entry_focus_out(event):
            location_entry.config(highlightbackground='#ced4da')

        location_entry.bind('<Button-1>', on_entry_click)
        location_entry.bind('<FocusIn>', on_entry_focus_in)
        location_entry.bind('<FocusOut>', on_entry_focus_out)

        browse_btn = tk.Button(location_entry_frame, text="browse",
                              font=("Segoe UI", 11), bg='#e9ecef', fg='#495057',
                              relief='solid', bd=1, borderwidth=1,
                              activebackground='#dee2e6', activeforeground='#212529',
                              padx=25, pady=12, cursor='hand2',
                              command=self.browse_location)
        browse_btn.pack(side=tk.RIGHT, padx=(12, 0))

        # Process section with enhanced styling
        process_label = tk.Label(content_frame, text="Process :",
                                font=("Segoe UI", 12, "normal"), bg='#f8f9fa', fg='#495057')
        process_label.pack(anchor=tk.W, pady=(15, 8))

        # Progress bar with modern styling
        self.progress_bar = ttk.Progressbar(content_frame, variable=self.progress_var,
                                           maximum=100, style='Modern.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5), ipady=10)

        # Progress percentage and status label
        self.progress_status_label = tk.Label(content_frame, text="0% - Ready to install",
                                             font=("Arial", 10), bg='#f8f9fa', fg='#6c757d')
        self.progress_status_label.pack(anchor=tk.W, pady=(5, 20))

        # Configure modern progress bar style
        style = ttk.Style()
        style.theme_use('clam')  # Use a modern theme
        style.configure('Modern.Horizontal.TProgressbar',
                       background='#28a745',
                       troughcolor='#e9ecef',
                       borderwidth=0,
                       lightcolor='#28a745',
                       darkcolor='#28a745')

        # Buttons frame with enhanced styling
        button_frame = tk.Frame(self.root, bg='#f8f9fa')
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=35, pady=25)

        # Cancel button with modern styling
        self.cancel_btn = tk.Button(button_frame, text="Cancel",
                                   font=("Segoe UI", 12), bg='#6c757d', fg='#ffffff',
                                   relief='flat', bd=0, padx=35, pady=12,
                                   activebackground='#5a6268', activeforeground='#ffffff',
                                   cursor='hand2',
                                   command=self.root.quit)
        self.cancel_btn.pack(side=tk.RIGHT, padx=(15, 0))

        # Install button with premium styling
        self.install_btn = tk.Button(button_frame, text="Install",
                                    font=("Segoe UI", 12, "bold"), bg='#28a745', fg='#ffffff',
                                    relief='flat', bd=0, padx=35, pady=12,
                                    activebackground='#218838', activeforeground='#ffffff',
                                    cursor='hand2',
                                    command=self.start_installation)
        self.install_btn.pack(side=tk.RIGHT)

        # Add hover effects
        def on_cancel_enter(event):
            self.cancel_btn.config(bg='#5a6268')
        def on_cancel_leave(event):
            self.cancel_btn.config(bg='#6c757d')
        def on_install_enter(event):
            self.install_btn.config(bg='#218838')
        def on_install_leave(event):
            self.install_btn.config(bg='#28a745')

        self.cancel_btn.bind('<Enter>', on_cancel_enter)
        self.cancel_btn.bind('<Leave>', on_cancel_leave)
        self.install_btn.bind('<Enter>', on_install_enter)
        self.install_btn.bind('<Leave>', on_install_leave)
        
    def run_subprocess_hidden(self, cmd, **kwargs):
        """Run subprocess with maximum window suppression"""
        # Suppress any popup windows during subprocess
        startupinfo = None
        creationflags = 0

        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

            # Maximum suppression flags
            creationflags = (subprocess.CREATE_NO_WINDOW |
                           subprocess.CREATE_NEW_PROCESS_GROUP)

            kwargs['startupinfo'] = startupinfo
            kwargs['creationflags'] = creationflags

        # Set environment variables to suppress pip prompts
        env = kwargs.get('env', os.environ.copy())
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PIP_NO_INPUT'] = '1'
        env['PIP_QUIET'] = '1'
        env['PIP_DISABLE_PIP_VERSION_CHECK'] = '1'
        kwargs['env'] = env

        return subprocess.run(cmd, **kwargs)

    def run_pip_silent(self, pip_args):
        """Run pip with maximum silence and suppression"""
        # Build pip command with all suppression flags
        cmd = [sys.executable, "-m", "pip"] + pip_args + [
            "-q",  # Quiet mode
            "--no-warn-script-location",  # No script warnings
            "--disable-pip-version-check",  # No version check
            "--no-input",  # No interactive prompts
            "--exists-action", "i"  # Ignore if already exists
        ]

        # Run with maximum suppression
        return self.run_subprocess_hidden(cmd, capture_output=True, text=True)

    def show_message(self, msg_type, title, message):
        """Show message only if not in silent mode"""
        if not self.silent_mode:
            if msg_type == "error":
                messagebox.showerror(title, message)
            elif msg_type == "warning":
                messagebox.showwarning(title, message)
            elif msg_type == "info":
                messagebox.showinfo(title, message)
        else:
            # Just print to console during silent installation
            print(f"[{msg_type.upper()}] {title}: {message}")

    def update_progress(self, value, status=""):
        """Update progress bar and status with detailed logging"""
        try:
            self.progress_var.set(value)

            # Update progress status label with percentage and status
            if status:
                progress_text = f"{value}% - {status}"
                self.progress_status_label.config(text=progress_text)
                self.root.title(f"Hackathon Monitor Installer - {status}")
                print(f"[PROGRESS] {value}% - {status}")
                print(f"[MARKER] ===== {value}% CHECKPOINT =====")
            else:
                progress_text = f"{value}%"
                self.progress_status_label.config(text=progress_text)
                print(f"[PROGRESS] {value}%")
                print(f"[MARKER] ===== {value}% CHECKPOINT =====")

            # Use update_idletasks instead of update to prevent window issues
            self.root.update_idletasks()

        except Exception as e:
            print(f"[!] Progress update error: {e}")
        
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
            self.show_message("warning", "Admin Rights Required",
                            "This installer needs administrator rights to install to Program Files.\n\n"
                            "Please run this installer as Administrator.")
            return False
        return True
        
    def check_python(self):
        """Check if Python is installed"""
        try:
            result = self.run_subprocess_hidden([sys.executable, "--version"],
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
            
            # Install Python silently with window suppression
            cmd = [str(python_installer), "/quiet", "InstallAllUsers=1",
                   "PrependPath=1", "Include_test=0"]

            result = self.run_subprocess_hidden(cmd, capture_output=True)
            
            if result.returncode == 0:
                self.update_progress(30, "Python installed successfully")
                return True
            else:
                raise Exception("Python installation failed")
                
        except Exception as e:
            self.show_message("error", "Error", f"Failed to install Python: {e}")
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
            self.show_message("error", "Error", f"Failed to download application: {e}")
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
            
            # Install Python dependencies (if enabled)
            if self.python_deps_var.get():
                print("[SUBSTEP] Installing Python dependencies...")
                self.update_progress(60, "Installing Python dependencies...")

                requirements_file = self.install_dir / "requirements_pyqt.txt"
                if requirements_file.exists():
                    print("[SUBSTEP] Running pip install...")
                    self.update_progress(65, "Running pip install...")

                    # Use maximum silent pip installation
                    result = self.run_pip_silent(["install", "-r", str(requirements_file)])

                    if result.returncode != 0:
                        print("[SUBSTEP] Trying with --user flag...")
                        self.update_progress(68, "Retrying with --user flag...")
                        # Try with --user flag
                        self.run_pip_silent(["install", "--user", "-r", str(requirements_file)])

                    print("[SUBSTEP] Dependencies installation completed")
                    self.update_progress(70, "Dependencies installation completed")
            else:
                print("[SUBSTEP] Skipping Python dependencies...")
                self.update_progress(70, "Skipping Python dependencies installation...")
            
            return True
            
        except Exception as e:
            self.show_message("error", "Error", f"Failed to install application: {e}")
            return False

    def create_launcher_script(self):
        """Create a simple launcher script for the application"""
        try:
            # Create a simple Windows launcher script that hides terminal
            launcher_path = self.install_dir / "Launch Hackathon Monitor.bat"

            with open(launcher_path, 'w') as f:
                f.write('@echo off\n')
                f.write(f'cd /d "{self.install_dir}"\n')
                f.write('start /min python hackathon_monitor_pyqt.py\n')

            # Also create a VBS script for completely hidden execution
            vbs_launcher_path = self.install_dir / "Launch Hackathon Monitor.vbs"

            with open(vbs_launcher_path, 'w') as f:
                f.write('Set WshShell = CreateObject("WScript.Shell")\n')
                f.write(f'WshShell.CurrentDirectory = "{self.install_dir}"\n')
                f.write('WshShell.Run "python hackathon_monitor_pyqt.py", 0, False\n')

            print("[+] Created launcher script (hidden terminal)")
            return True

        except Exception as e:
            print(f"[!] Failed to create launcher script: {e}")
            return False

    def create_desktop_shortcut(self):
        """Create desktop shortcut (.lnk file)"""
        if not self.desktop_shortcut_var.get():
            self.update_progress(80, "Skipping desktop shortcut creation...")
            return True

        self.update_progress(80, "Creating desktop shortcut...")

        try:
            desktop = Path.home() / "Desktop"
            shortcut_path = desktop / "Hackathon Monitor.lnk"

            # Method 1: Try using win32com.client (if available)
            try:
                import win32com.client

                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(str(shortcut_path))

                # Point to the VBS script for completely hidden execution
                vbs_launcher = self.install_dir / "Launch Hackathon Monitor.vbs"
                shortcut.Targetpath = str(vbs_launcher)
                shortcut.WorkingDirectory = str(self.install_dir)

                # Set icon if available
                icon_path = self.install_dir / "logo.png"
                if icon_path.exists():
                    shortcut.IconLocation = str(icon_path)

                shortcut.save()
                print("[+] Created .lnk shortcut using win32com")
                return True

            except ImportError:
                # Method 2: Use PowerShell to create .lnk file
                print("[*] win32com not available, using PowerShell...")

                vbs_launcher = self.install_dir / "Launch Hackathon Monitor.vbs"
                powershell_script = f'''
$WshShell = New-Object -comObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{vbs_launcher}"
$Shortcut.WorkingDirectory = "{self.install_dir}"
$Shortcut.Save()
'''

                # Run PowerShell command to create .lnk file
                cmd = ["powershell", "-Command", powershell_script]
                result = self.run_subprocess_hidden(cmd, capture_output=True, text=True)

                if result.returncode == 0:
                    print("[+] Created .lnk shortcut using PowerShell")
                    return True
                else:
                    raise Exception("PowerShell shortcut creation failed")

        except Exception as e:
            print(f"[!] .lnk creation failed: {e}")
            # Fallback: create batch file
            try:
                print("[*] Creating .bat file as fallback...")
                desktop = Path.home() / "Desktop"
                batch_file = desktop / "Hackathon Monitor.bat"

                with open(batch_file, 'w') as f:
                    f.write('@echo off\n')
                    f.write(f'cd /d "{self.install_dir}"\n')
                    f.write('start /min python hackathon_monitor_pyqt.py\n')

                print("[+] Created .bat shortcut as fallback")
                return True

            except Exception as e2:
                print(f"[!] Fallback .bat creation failed: {e2}")
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
        # Prevent multiple installations
        if self.installing:
            print("[!] Installation already in progress")
            return

        self.installing = True
        self.silent_mode = True  # Enable silent mode to suppress popups during installation

        # Completely disable all messageboxes during installation
        self.original_messagebox = messagebox
        messagebox.showinfo = lambda *args, **kwargs: None
        messagebox.showwarning = lambda *args, **kwargs: None
        messagebox.showerror = lambda *args, **kwargs: None
        messagebox.askquestion = lambda *args, **kwargs: 'yes'
        messagebox.askyesno = lambda *args, **kwargs: True

        # Disable window close button during installation
        self.root.protocol("WM_DELETE_WINDOW", lambda: None)

        # Keep installer window focused and on top during installation
        self.root.focus_force()
        self.root.lift()

        def install_thread():
            try:
                print("[START] Installation thread started")
                self.update_progress(0, "Starting installation...")

                # Check admin rights
                print("[STEP] Checking admin rights...")
                self.update_progress(10, "Checking admin rights...")
                if not self.request_admin_rights():
                    return

                # Check Python
                print("[STEP] Checking Python...")
                self.update_progress(20, "Checking Python installation...")
                if not self.check_python():
                    print("[STEP] Installing Python...")
                    self.update_progress(25, "Installing Python...")
                    if not self.install_python():
                        return

                # Download application
                print("[STEP] Downloading application...")
                self.update_progress(30, "Downloading application...")
                if not self.download_application():
                    return

                print("[STEP] Extracting files...")
                self.update_progress(40, "Extracting application files...")

                # Install application
                print("[STEP] Installing application files...")
                self.update_progress(50, "Installing application files...")
                if not self.install_application():
                    return

                # Create launcher script
                print("[STEP] Creating launcher script...")
                self.update_progress(75, "Creating launcher script...")
                self.create_launcher_script()

                # Create desktop shortcut
                print("[STEP] Creating desktop shortcut...")
                self.update_progress(80, "Creating desktop shortcut...")
                self.create_desktop_shortcut()

                # Check Chrome
                print("[STEP] Checking Chrome...")
                self.update_progress(90, "Checking Google Chrome...")
                chrome_installed = self.check_chrome()

                # Cleanup
                print("[STEP] Cleaning up...")
                self.update_progress(95, "Cleaning up temporary files...")
                self.cleanup()

                # Success message
                print("[STEP] Installation completed!")
                self.update_progress(100, "Installation completed!")
                
                success_msg = "[+] Hackathon Monitor installed successfully!\n\n"
                success_msg += f"[*] Installed to: {self.install_dir}\n"
                success_msg += "[*] Desktop shortcut created\n\n"

                if not chrome_installed:
                    success_msg += "[!] Google Chrome is not installed\n"
                    success_msg += "[*] Please install Chrome for web scraping:\n"
                    success_msg += "https://www.google.com/chrome/"
                else:
                    success_msg += "[+] Google Chrome detected"
                
                # Restore messagebox functionality and show final message
                self.silent_mode = False
                messagebox.showinfo = self.original_messagebox.showinfo
                messagebox.showwarning = self.original_messagebox.showwarning
                messagebox.showerror = self.original_messagebox.showerror
                messagebox.askquestion = self.original_messagebox.askquestion
                messagebox.askyesno = self.original_messagebox.askyesno

                messagebox.showinfo("Installation Complete", success_msg)

                # Enable buttons
                self.install_btn.config(state=tk.NORMAL, text="Install")
                self.cancel_btn.config(state=tk.NORMAL, text="Close")

            except Exception as e:
                # Restore messagebox functionality for error message
                self.silent_mode = False
                messagebox.showinfo = self.original_messagebox.showinfo
                messagebox.showwarning = self.original_messagebox.showwarning
                messagebox.showerror = self.original_messagebox.showerror
                messagebox.askquestion = self.original_messagebox.askquestion
                messagebox.askyesno = self.original_messagebox.askyesno

                messagebox.showerror("Installation Error", f"Installation failed: {e}")
                self.install_btn.config(state=tk.NORMAL, text="Install")
                self.cancel_btn.config(state=tk.NORMAL, text="Cancel")
            finally:
                # Reset installation flag and re-enable close button
                self.installing = False
                self.silent_mode = False

                # Restore messagebox functionality if not already done
                try:
                    messagebox.showinfo = self.original_messagebox.showinfo
                    messagebox.showwarning = self.original_messagebox.showwarning
                    messagebox.showerror = self.original_messagebox.showerror
                    messagebox.askquestion = self.original_messagebox.askquestion
                    messagebox.askyesno = self.original_messagebox.askyesno
                except:
                    pass

                self.root.protocol("WM_DELETE_WINDOW", self.root.quit)
        
        # Disable install button and update UI
        self.install_btn.config(state=tk.DISABLED, text="Installing...")
        self.cancel_btn.config(state=tk.DISABLED)

        # Start installation in separate thread
        import threading
        thread = threading.Thread(target=install_thread)
        thread.daemon = True
        thread.start()
        
    def run(self):
        """Run the installer"""
        self.root.mainloop()

def main():
    """Main function with EXE compatibility"""
    try:
        # Check if running as EXE (PyInstaller sets sys.frozen)
        import sys
        is_exe = getattr(sys, 'frozen', False)

        if is_exe:
            # Running as EXE - ensure single instance
            import os
            import tempfile

            # Create a lock file to prevent multiple instances
            lock_file = os.path.join(tempfile.gettempdir(), "hackathon_installer.lock")

            try:
                # Try to create lock file
                if os.path.exists(lock_file):
                    print("[!] Installer already running")
                    return

                # Create lock file
                with open(lock_file, 'w') as f:
                    f.write(str(os.getpid()))

                # Run installer
                installer = HackathonMonitorInstaller()
                installer.run()

            finally:
                # Clean up lock file
                try:
                    if os.path.exists(lock_file):
                        os.remove(lock_file)
                except:
                    pass
        else:
            # Running as Python script - normal behavior
            installer = HackathonMonitorInstaller()
            installer.run()

    except Exception as e:
        print(f"[-] Installer failed to start: {e}")
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Installer failed to start: {e}")
            root.destroy()
        except:
            pass

if __name__ == "__main__":
    main()
