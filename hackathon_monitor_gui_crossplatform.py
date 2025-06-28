#!/usr/bin/env python3
"""
Hackathon Monitor - Cross-Platform GUI Version
Works on Windows, macOS, and Linux with native look and feel
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import subprocess
import threading
import os
import sys
import platform
from pathlib import Path
import json
from datetime import datetime

class CrossPlatformHackathonMonitorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.platform = platform.system()
        self.setup_window()
        
        # Variables
        self.monitoring_process = None
        self.is_monitoring = False
        
        self.create_widgets()
        self.load_settings()

    def setup_window(self):
        """Setup window with platform-specific styling"""
        self.root.title(f"Hackathon Monitor v1.0 - {self.platform}")
        
        # Platform-specific window setup
        if self.platform == "Darwin":  # macOS
            self.root.geometry("700x600")
            # macOS specific styling
            try:
                # Try to use native macOS styling
                self.root.tk.call('tk', 'scaling', 1.0)
            except:
                pass
        elif self.platform == "Linux":
            self.root.geometry("750x650")
            # Linux specific styling
            try:
                # Try to use system theme
                style = ttk.Style()
                style.theme_use('clam')  # Good cross-platform theme
            except:
                pass
        else:  # Windows
            self.root.geometry("700x600")
        
        self.root.resizable(True, True)
        self.root.minsize(600, 500)

        # Set window icon if available
        self.set_window_icon()

    def set_window_icon(self):
        """Set the window icon for taskbar display"""
        try:
            # Try to load the logo as window icon
            logo_path = Path("logo.png")
            if logo_path.exists():
                if self.platform == "Linux":
                    # Linux often needs PhotoImage
                    try:
                        photo = tk.PhotoImage(file=logo_path)
                        self.root.iconphoto(True, photo)
                    except:
                        pass
                else:
                    # Windows and macOS
                    try:
                        from PIL import Image, ImageTk
                        img = Image.open(logo_path)
                        img = img.resize((32, 32), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        self.root.iconphoto(True, photo)
                    except ImportError:
                        # PIL not available, try direct
                        try:
                            photo = tk.PhotoImage(file=logo_path)
                            self.root.iconphoto(True, photo)
                        except:
                            pass
        except Exception as e:
            print(f"Could not set window icon: {e}")

    def create_widgets(self):
        """Create the GUI widgets with platform-appropriate styling"""
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Main tab
        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="Monitor")

        # Settings tab
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="Settings")

        # Logs tab
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="Logs")

        self.create_main_tab()
        self.create_settings_tab()
        self.create_logs_tab()

    def create_main_tab(self):
        """Create the main monitoring tab"""
        # Header
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, text="🎯 Hackathon Monitor", 
                               font=("Arial", 16, "bold"))
        title_label.pack()

        platform_label = ttk.Label(header_frame, text=f"Running on {self.platform}",
                                  font=("Arial", 10))
        platform_label.pack()

        # Status section
        status_frame = ttk.LabelFrame(self.main_frame, text="Status", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 10))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                     font=("Arial", 11))
        self.status_label.pack()

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))

        # Control buttons
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=10)

        # Platform-specific button styling
        button_width = 15 if self.platform == "Darwin" else 20

        self.scrape_once_btn = ttk.Button(button_frame, text="🔍 Scrape Once",
                                         command=self.scrape_once, width=button_width)
        self.scrape_once_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.start_monitoring_btn = ttk.Button(button_frame, text="⏰ Start Monitoring",
                                              command=self.start_monitoring, width=button_width)
        self.start_monitoring_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_monitoring_btn = ttk.Button(button_frame, text="⏹️ Stop Monitoring",
                                             command=self.stop_monitoring, width=button_width,
                                             state="disabled")
        self.stop_monitoring_btn.pack(side=tk.LEFT)

        # Quick actions
        actions_frame = ttk.LabelFrame(self.main_frame, text="Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, pady=10)

        actions_button_frame = ttk.Frame(actions_frame)
        actions_button_frame.pack()

        ttk.Button(actions_button_frame, text="📊 Open Excel",
                  command=self.open_excel, width=button_width).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(actions_button_frame, text="🔔 Test Notification",
                  command=self.test_notification, width=button_width).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(actions_button_frame, text="📁 Open Data Folder",
                  command=self.open_data_folder, width=button_width).pack(side=tk.LEFT)

    def create_settings_tab(self):
        """Create the settings tab"""
        # Platform selection info
        platform_frame = ttk.LabelFrame(self.settings_frame, text="Platform Information", padding=10)
        platform_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(platform_frame, text=f"Operating System: {platform.system()}").pack(anchor=tk.W)
        ttk.Label(platform_frame, text=f"Architecture: {platform.machine()}").pack(anchor=tk.W)
        ttk.Label(platform_frame, text=f"Python Version: {platform.python_version()}").pack(anchor=tk.W)

        # Monitoring settings
        monitoring_frame = ttk.LabelFrame(self.settings_frame, text="Monitoring Settings", padding=10)
        monitoring_frame.pack(fill=tk.X, pady=(0, 10))

        # Interval setting
        interval_frame = ttk.Frame(monitoring_frame)
        interval_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(interval_frame, text="Check Interval (hours):").pack(side=tk.LEFT)
        self.interval_var = tk.StringVar(value="6")
        interval_spinbox = ttk.Spinbox(interval_frame, from_=1, to=24, width=10,
                                      textvariable=self.interval_var)
        interval_spinbox.pack(side=tk.LEFT, padx=(10, 0))

        # Notifications setting
        self.notifications_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(monitoring_frame, text="Enable notifications",
                       variable=self.notifications_var).pack(anchor=tk.W)

        # Platform-specific settings
        platform_settings_frame = ttk.LabelFrame(self.settings_frame, 
                                                text=f"{self.platform} Settings", padding=10)
        platform_settings_frame.pack(fill=tk.X, pady=(0, 10))

        if self.platform == "Windows":
            self.startup_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(platform_settings_frame, text="Start with Windows",
                           variable=self.startup_var).pack(anchor=tk.W)
        elif self.platform == "Darwin":
            ttk.Label(platform_settings_frame, 
                     text="Notifications use native macOS system").pack(anchor=tk.W)
        elif self.platform == "Linux":
            ttk.Label(platform_settings_frame,
                     text="Notifications use notify-send or system tray").pack(anchor=tk.W)

        # Save settings button
        ttk.Button(self.settings_frame, text="💾 Save Settings",
                  command=self.save_settings).pack(pady=10)

    def create_logs_tab(self):
        """Create the logs tab"""
        # Log display
        self.log_text = scrolledtext.ScrolledText(self.logs_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Log controls
        log_controls = ttk.Frame(self.logs_frame)
        log_controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        ttk.Button(log_controls, text="🔄 Refresh Logs",
                  command=self.refresh_logs).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(log_controls, text="🗑️ Clear Logs",
                  command=self.clear_logs).pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(log_controls, text="💾 Save Logs",
                  command=self.save_logs).pack(side=tk.LEFT)

    def scrape_once(self):
        """Run a single scraping cycle"""
        self.log_message("Starting single scraping cycle...")
        self.update_status("Scraping...", 0)
        
        def run_scrape():
            try:
                # Use the cross-platform version
                cmd = [sys.executable, "hackathon_monitor_crossplatform.py", "--once"]
                
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                                         stderr=subprocess.PIPE, text=True)
                
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    self.log_message("✅ Scraping completed successfully!")
                    self.log_message(stdout)
                    self.update_status("Scraping completed", 100)
                else:
                    self.log_message(f"❌ Scraping failed: {stderr}")
                    self.update_status("Scraping failed", 0)
                    
            except Exception as e:
                self.log_message(f"❌ Error: {str(e)}")
                self.update_status("Error occurred", 0)
        
        threading.Thread(target=run_scrape, daemon=True).start()

    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_monitoring:
            return
            
        self.log_message("Starting continuous monitoring...")
        self.is_monitoring = True
        
        # Update button states
        self.start_monitoring_btn.config(state="disabled")
        self.stop_monitoring_btn.config(state="normal")
        
        def run_monitor():
            try:
                cmd = [sys.executable, "hackathon_monitor_crossplatform.py", "--background"]
                
                self.monitoring_process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                                         stderr=subprocess.PIPE, text=True)
                
                self.update_status("Monitoring active", 50)
                self.log_message("✅ Monitoring started successfully!")
                
                # Monitor the process
                while self.is_monitoring and self.monitoring_process.poll() is None:
                    time.sleep(1)
                    
            except Exception as e:
                self.log_message(f"❌ Monitoring error: {str(e)}")
                self.stop_monitoring()
        
        threading.Thread(target=run_monitor, daemon=True).start()

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.is_monitoring:
            return
            
        self.is_monitoring = False
        
        if self.monitoring_process:
            try:
                self.monitoring_process.terminate()
                self.monitoring_process.wait(timeout=5)
            except:
                try:
                    self.monitoring_process.kill()
                except:
                    pass
            self.monitoring_process = None
        
        # Update button states
        self.start_monitoring_btn.config(state="normal")
        self.stop_monitoring_btn.config(state="disabled")
        
        self.update_status("Monitoring stopped", 0)
        self.log_message("⏹️ Monitoring stopped")

    def open_excel(self):
        """Open the Excel file with platform-appropriate method"""
        excel_file = Path("hackathons_data.xlsx")
        
        if not excel_file.exists():
            messagebox.showwarning("File Not Found", 
                                 "Excel file not found. Run scraping first to create it.")
            return
        
        try:
            if self.platform == "Windows":
                os.startfile(excel_file)
            elif self.platform == "Darwin":  # macOS
                subprocess.run(["open", excel_file])
            else:  # Linux
                subprocess.run(["xdg-open", excel_file])
                
            self.log_message(f"📊 Opened Excel file: {excel_file}")
            
        except Exception as e:
            self.log_message(f"❌ Failed to open Excel file: {e}")
            messagebox.showerror("Error", f"Failed to open Excel file: {e}")

    def test_notification(self):
        """Test the notification system"""
        self.log_message("Testing notification system...")
        
        try:
            # Import and use the cross-platform notifier
            from hackathon_monitor_crossplatform import CrossPlatformNotifier
            
            notifier = CrossPlatformNotifier()
            notifier.send_notification(
                "Hackathon Monitor Test",
                f"Notification system working on {self.platform}! 🎉"
            )
            
            self.log_message("✅ Test notification sent!")
            
        except Exception as e:
            self.log_message(f"❌ Notification test failed: {e}")
            messagebox.showerror("Notification Error", f"Failed to send notification: {e}")

    def open_data_folder(self):
        """Open the data folder"""
        data_folder = Path.cwd()
        
        try:
            if self.platform == "Windows":
                os.startfile(data_folder)
            elif self.platform == "Darwin":  # macOS
                subprocess.run(["open", data_folder])
            else:  # Linux
                subprocess.run(["xdg-open", data_folder])
                
            self.log_message(f"📁 Opened data folder: {data_folder}")
            
        except Exception as e:
            self.log_message(f"❌ Failed to open data folder: {e}")

    def update_status(self, message, progress):
        """Update status and progress"""
        self.status_var.set(message)
        self.progress_var.set(progress)
        self.root.update()

    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.root.update()

    def refresh_logs(self):
        """Refresh logs from file"""
        try:
            log_file = Path("logs/hackathon_monitor.log")
            if log_file.exists():
                with open(log_file, 'r') as f:
                    content = f.read()
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(1.0, content)
                self.log_text.see(tk.END)
        except Exception as e:
            self.log_message(f"❌ Failed to refresh logs: {e}")

    def clear_logs(self):
        """Clear the log display"""
        self.log_text.delete(1.0, tk.END)

    def save_logs(self):
        """Save logs to file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if filename:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                self.log_message(f"💾 Logs saved to: {filename}")
                
        except Exception as e:
            self.log_message(f"❌ Failed to save logs: {e}")

    def load_settings(self):
        """Load settings from file"""
        try:
            settings_file = Path("gui_settings.json")
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                
                self.interval_var.set(settings.get('interval', '6'))
                self.notifications_var.set(settings.get('notifications', True))
                
                if self.platform == "Windows":
                    self.startup_var.set(settings.get('startup', False))
                    
        except Exception as e:
            self.log_message(f"⚠️ Failed to load settings: {e}")

    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'interval': self.interval_var.get(),
                'notifications': self.notifications_var.get(),
                'platform': self.platform
            }
            
            if self.platform == "Windows":
                settings['startup'] = self.startup_var.get()
            
            with open("gui_settings.json", 'w') as f:
                json.dump(settings, f, indent=2)
                
            self.log_message("💾 Settings saved successfully!")
            messagebox.showinfo("Settings", "Settings saved successfully!")
            
        except Exception as e:
            self.log_message(f"❌ Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def on_closing(self):
        """Handle window closing"""
        if self.is_monitoring:
            if messagebox.askokcancel("Quit", "Monitoring is active. Stop monitoring and quit?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initial log message
        self.log_message(f"🎯 Hackathon Monitor GUI started on {self.platform}")
        self.log_message("Ready to monitor hackathon platforms!")
        
        self.root.mainloop()

if __name__ == "__main__":
    import time  # Add this import
    
    app = CrossPlatformHackathonMonitorGUI()
    app.run()
