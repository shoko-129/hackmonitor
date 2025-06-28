#!/usr/bin/env python3
"""
Hackathon Monitor - Terminal User Interface (TUI)
Modern terminal-based interface using Rich library
"""

import time
import threading
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.layout import Layout
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.live import Live
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
    from rich.columns import Columns
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from hackathon_monitor_crossplatform import HackathonMonitor

class TUIHackathonMonitor:
    def __init__(self):
        if not RICH_AVAILABLE:
            print("❌ Rich library not available. Install with: pip install rich")
            print("Falling back to simple terminal interface...")
            self.use_rich = False
        else:
            self.use_rich = True
            self.console = Console()
        
        self.monitor = HackathonMonitor()
        self.is_monitoring = False
        self.monitoring_thread = None
        self.status = "Ready"
        self.progress_value = 0
        self.logs = []
        self.stats = {'total': 0, 'new_today': 0, 'last_update': None}
    
    def log_message(self, message):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[{timestamp}] {message}")
        if len(self.logs) > 50:
            self.logs = self.logs[-50:]
    
    def update_stats(self):
        """Update statistics"""
        try:
            hackathons = self.monitor.excel_manager.get_existing_hackathons()
            self.stats['total'] = len(hackathons)
            self.stats['last_update'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Count new hackathons today
            today = datetime.now().date()
            new_today = 0
            for h in hackathons:
                try:
                    scraped_date = datetime.fromisoformat(h.get('scraped_at', '')).date()
                    if scraped_date == today:
                        new_today += 1
                except:
                    pass
            self.stats['new_today'] = new_today
        except Exception as e:
            self.log_message(f"Stats update error: {str(e)}")
    
    def create_layout(self):
        """Create the TUI layout"""
        if not self.use_rich:
            return None
        
        layout = Layout()
        
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", ratio=1),
            Layout(name="footer", size=3)
        )
        
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        layout["left"].split_column(
            Layout(name="status", size=8),
            Layout(name="controls", size=10),
            Layout(name="stats", size=8)
        )
        
        layout["right"].split_column(
            Layout(name="logs")
        )
        
        return layout
    
    def create_header(self):
        """Create header panel"""
        return Panel(
            Text("🎯 Hackathon Monitor - Terminal Interface", justify="center", style="bold blue"),
            style="blue"
        )
    
    def create_status_panel(self):
        """Create status panel"""
        status_text = Text()
        status_text.append("Status: ", style="bold")
        status_text.append(self.status, style="green" if "active" in self.status.lower() else "yellow")
        
        progress_bar = f"Progress: {'█' * int(self.progress_value / 5)}{'░' * (20 - int(self.progress_value / 5))} {self.progress_value}%"
        
        content = f"{status_text}\n\n{progress_bar}\n\nMonitoring: {'🟢 Active' if self.is_monitoring else '🔴 Stopped'}"
        
        return Panel(content, title="📊 Status", border_style="green")
    
    def create_controls_panel(self):
        """Create controls panel"""
        controls = """
[1] 🔍 Scrape Once
[2] ⏰ Start Monitoring  
[3] ⏹️ Stop Monitoring
[4] 🔔 Test Notification
[5] 📊 Open Excel File
[6] ⚙️ Settings
[7] 📝 View Full Logs
[8] 🚪 Exit

Enter choice (1-8):
        """
        return Panel(controls.strip(), title="🎛️ Controls", border_style="blue")
    
    def create_stats_panel(self):
        """Create statistics panel"""
        stats_table = Table(show_header=False, box=None)
        stats_table.add_column("Label", style="cyan")
        stats_table.add_column("Value", style="bold white")
        
        stats_table.add_row("Total Hackathons:", str(self.stats['total']))
        stats_table.add_row("New Today:", str(self.stats['new_today']))
        stats_table.add_row("Last Update:", self.stats['last_update'] or "Never")
        
        return Panel(stats_table, title="📈 Statistics", border_style="magenta")
    
    def create_logs_panel(self):
        """Create logs panel"""
        logs_text = "\n".join(self.logs[-15:]) if self.logs else "No logs yet..."
        return Panel(logs_text, title="📝 Recent Logs", border_style="yellow")
    
    def create_footer(self):
        """Create footer panel"""
        return Panel(
            Text("Use number keys to navigate • Press Ctrl+C to exit", justify="center"),
            style="dim"
        )
    
    def run_rich_interface(self):
        """Run the Rich-based TUI"""
        layout = self.create_layout()
        
        with Live(layout, refresh_per_second=2, screen=True) as live:
            while True:
                try:
                    # Update layout components
                    layout["header"].update(self.create_header())
                    layout["status"].update(self.create_status_panel())
                    layout["controls"].update(self.create_controls_panel())
                    layout["stats"].update(self.create_stats_panel())
                    layout["logs"].update(self.create_logs_panel())
                    layout["footer"].update(self.create_footer())
                    
                    # Handle input (simplified for demo)
                    time.sleep(0.5)
                    
                except KeyboardInterrupt:
                    break
        
        self.console.print("\n👋 Goodbye!", style="bold blue")
    
    def run_simple_interface(self):
        """Run simple terminal interface without Rich"""
        while True:
            # Clear screen
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("🎯 Hackathon Monitor - Terminal Interface")
            print("=" * 50)
            print(f"Status: {self.status}")
            print(f"Progress: {'█' * int(self.progress_value / 5)}{'░' * (20 - int(self.progress_value / 5))} {self.progress_value}%")
            print(f"Monitoring: {'🟢 Active' if self.is_monitoring else '🔴 Stopped'}")
            print()
            print("📈 Statistics:")
            print(f"  Total Hackathons: {self.stats['total']}")
            print(f"  New Today: {self.stats['new_today']}")
            print(f"  Last Update: {self.stats['last_update'] or 'Never'}")
            print()
            print("🎛️ Controls:")
            print("  [1] 🔍 Scrape Once")
            print("  [2] ⏰ Start Monitoring")
            print("  [3] ⏹️ Stop Monitoring")
            print("  [4] 🔔 Test Notification")
            print("  [5] 📊 Open Excel File")
            print("  [6] 📝 View Logs")
            print("  [7] 🚪 Exit")
            print()
            
            if self.logs:
                print("📝 Recent Logs:")
                for log in self.logs[-5:]:
                    print(f"  {log}")
                print()
            
            try:
                choice = input("Enter choice (1-7): ").strip()
                self.handle_choice(choice)
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
    
    def handle_choice(self, choice):
        """Handle user choice"""
        if choice == '1':
            self.scrape_once()
        elif choice == '2':
            self.start_monitoring()
        elif choice == '3':
            self.stop_monitoring()
        elif choice == '4':
            self.test_notification()
        elif choice == '5':
            self.open_excel()
        elif choice == '6':
            self.view_logs()
        elif choice == '7':
            exit(0)
        else:
            self.log_message("Invalid choice")
            time.sleep(1)
    
    def scrape_once(self):
        """Run single scraping cycle"""
        def run_scrape():
            try:
                self.status = "Scraping..."
                self.progress_value = 25
                self.log_message("Starting single scraping cycle")
                
                self.monitor.run_scraping_cycle()
                
                self.progress_value = 100
                self.status = "Scraping completed"
                self.log_message("Scraping completed successfully")
                self.update_stats()
                
                time.sleep(2)
                self.status = "Ready"
                self.progress_value = 0
                
            except Exception as e:
                self.status = f"Scraping failed: {str(e)}"
                self.log_message(f"Scraping error: {str(e)}")
                self.progress_value = 0
        
        threading.Thread(target=run_scrape, daemon=True).start()
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.is_monitoring:
            self.log_message("Monitoring already active")
            return
        
        self.is_monitoring = True
        self.status = "Monitoring active"
        self.progress_value = 50
        self.log_message("Background monitoring started")
        
        def monitoring_loop():
            while self.is_monitoring:
                try:
                    self.status = "Running scheduled scrape..."
                    self.progress_value = 75
                    self.monitor.run_scraping_cycle()
                    self.update_stats()
                    
                    self.status = "Monitoring active - waiting for next cycle"
                    self.progress_value = 50
                    
                    # Wait for next cycle
                    interval_hours = float(self.monitor.config['SETTINGS']['scraping_interval'])
                    wait_minutes = interval_hours * 60
                    
                    for _ in range(int(wait_minutes)):
                        if not self.is_monitoring:
                            break
                        time.sleep(60)
                        
                except Exception as e:
                    self.log_message(f"Monitoring error: {str(e)}")
                    time.sleep(300)
        
        self.monitoring_thread = threading.Thread(target=monitoring_loop, daemon=True)
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        if not self.is_monitoring:
            self.log_message("Monitoring not active")
            return
        
        self.is_monitoring = False
        self.status = "Monitoring stopped"
        self.progress_value = 0
        self.log_message("Background monitoring stopped")
    
    def test_notification(self):
        """Test notification system"""
        try:
            from hackathon_monitor_crossplatform import CrossPlatformNotifier
            notifier = CrossPlatformNotifier()
            notifier.send_notification(
                "Hackathon Monitor Test",
                "TUI notification test successful! 🎉"
            )
            self.log_message("Test notification sent")
        except Exception as e:
            self.log_message(f"Notification test failed: {str(e)}")
    
    def open_excel(self):
        """Open Excel file"""
        excel_file = Path("hackathons_data.xlsx")
        if not excel_file.exists():
            self.log_message("Excel file not found. Run scraping first.")
            return
        
        try:
            import platform
            import subprocess
            
            if platform.system() == "Windows":
                import os
                os.startfile(excel_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", excel_file])
            else:  # Linux
                subprocess.run(["xdg-open", excel_file])
            
            self.log_message(f"Opened Excel file: {excel_file}")
        except Exception as e:
            self.log_message(f"Failed to open Excel file: {e}")
    
    def view_logs(self):
        """View full logs"""
        if not self.use_rich:
            print("\n📝 Full Logs:")
            print("-" * 50)
            for log in self.logs:
                print(log)
            input("\nPress Enter to continue...")
        else:
            self.console.print("\n📝 Full Logs:", style="bold blue")
            for log in self.logs:
                self.console.print(log)
            input("\nPress Enter to continue...")
    
    def run(self):
        """Run the TUI"""
        self.log_message("TUI started")
        self.update_stats()
        
        if self.use_rich:
            try:
                self.run_rich_interface()
            except:
                # Fallback to simple interface
                self.run_simple_interface()
        else:
            self.run_simple_interface()

if __name__ == "__main__":
    tui = TUIHackathonMonitor()
    tui.run()
