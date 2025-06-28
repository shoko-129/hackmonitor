"""
Windows Notification Module
Handles sending Windows toast notifications for hackathon updates.
"""

import logging
import time
import subprocess
import os

try:
    from win10toast import ToastNotifier
    WIN10TOAST_AVAILABLE = True
except ImportError:
    WIN10TOAST_AVAILABLE = False

class WindowsNotifier:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.toaster = None

        # Try to initialize ToastNotifier with error handling
        if WIN10TOAST_AVAILABLE:
            try:
                self.toaster = ToastNotifier()
                # Test if it works
                self.toaster.classAtom  # This will fail if there's an issue
            except (AttributeError, Exception) as e:
                self.logger.warning(f"win10toast initialization failed: {e}")
                self.toaster = None

    def _send_fallback_notification(self, title, message, duration=5):
        """Fallback notification using Windows msg command"""
        try:
            # Use Windows msg command as fallback
            import getpass
            username = getpass.getuser()

            # Create a simple message box
            cmd = f'msg {username} "{title}: {message}"'
            subprocess.run(cmd, shell=True, capture_output=True)
            self.logger.info("Sent fallback notification via Windows msg")
            return True
        except Exception as e:
            self.logger.warning(f"Fallback notification failed: {e}")
            return False

    def _send_powershell_notification(self, title, message):
        """Alternative fallback using PowerShell"""
        try:
            # Use PowerShell to show a balloon tip
            ps_script = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipTitle = "{title}"
            $notification.BalloonTipText = "{message}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(5000)
            Start-Sleep -Seconds 6
            $notification.Dispose()
            '''

            subprocess.run(['powershell', '-Command', ps_script],
                         capture_output=True, text=True, timeout=10)
            self.logger.info("Sent PowerShell notification")
            return True
        except Exception as e:
            self.logger.warning(f"PowerShell notification failed: {e}")
            return False
        
    def send_hackathon_summary_notification(self, new_count, excel_path, total_count=None, new_hackathons=None):
        """Send a summary notification about new hackathons found"""
        try:
            title = "🎯 Hackathon Monitor Update"

            # Build the main message
            if total_count:
                message = f"Found {new_count} new hackathon{'s' if new_count != 1 else ''}!\nTotal: {total_count} hackathons in database"
            else:
                message = f"Found {new_count} new hackathon{'s' if new_count != 1 else ''}!"

            # Add details of new hackathons (limit to first 3 for notification space)
            if new_hackathons and len(new_hackathons) > 0:
                message += "\n\nNew hackathons:"
                for i, hackathon in enumerate(new_hackathons[:3]):
                    name = hackathon.get('name', 'Unknown')
                    platform = hackathon.get('platform', '')
                    # Truncate long names for notification
                    if len(name) > 30:
                        name = name[:27] + "..."
                    message += f"\n• {name} ({platform})"

                if len(new_hackathons) > 3:
                    message += f"\n• +{len(new_hackathons) - 3} more..."

            message += "\n\nClick to view in Excel"

            # Try multiple notification methods
            success = False

            # Method 1: win10toast (if available, but without callback due to reliability issues)
            if self.toaster and WIN10TOAST_AVAILABLE:
                try:
                    # Try to use logo for notification
                    icon_path = None
                    try:
                        from pathlib import Path
                        # Try ICO first, then PNG
                        ico_path = Path("hackathon_monitor.ico")
                        png_path = Path("logo.png")
                        if ico_path.exists():
                            icon_path = str(ico_path)
                        elif png_path.exists():
                            icon_path = str(png_path)
                    except:
                        pass

                    # Don't use callback_on_click as it's unreliable, just show the notification
                    self.toaster.show_toast(
                        title=title,
                        msg=message + "\n\n(Click notification will be handled by fallback method)",
                        duration=20,
                        icon_path=icon_path,
                        threaded=True
                    )
                    # Don't mark as success yet, let PowerShell method handle the click functionality
                    self.logger.info(f"win10toast notification sent with icon: {icon_path}")
                except Exception as e:
                    self.logger.warning(f"win10toast failed: {e}")

            # Method 2: Windows 10 Toast notification (fallback)
            if not success:
                try:
                    success = self.send_windows_toast_notification(title, message, excel_path)
                    if success:
                        self.logger.info("Sent Windows toast notification with click action")
                except Exception as e:
                    self.logger.warning(f"Windows toast notification failed: {e}")

            # Method 3: PowerShell notification with click action (fallback)
            if not success:
                try:
                    self.send_powershell_summary_notification(title, message, excel_path)
                    success = True
                    self.logger.info("Sent PowerShell notification with click action")
                except Exception as e:
                    self.logger.warning(f"PowerShell summary notification failed: {e}")

            # Method 4: Basic PowerShell notification (fallback)
            if not success:
                success = self._send_powershell_notification(title, message + "\n\n(Manually open Excel file)")

            # Method 5: Windows msg command (fallback)
            if not success:
                success = self._send_fallback_notification(title, message + "\n\n(Manually open Excel file)")

            # Method 6: Console log (final fallback)
            if not success:
                self.logger.info(f"NOTIFICATION: {title} - {message}")
                self.logger.info(f"Excel file location: {excel_path}")
                print(f"\n🔔 NOTIFICATION: {title}")
                print(f"📝 {message}")
                print(f"📊 Excel file: {excel_path}")
                print(f"💡 To open Excel manually, double-click: {excel_path}\n")

            self.logger.info(f"Sent summary notification for {new_count} hackathons")

        except Exception as e:
            self.logger.error(f"Error sending summary notification: {e}")

    def open_excel_file(self, excel_path):
        """Open the Excel file when notification is clicked"""
        try:
            import os
            os.startfile(excel_path)  # Windows-specific way to open files
            self.logger.info(f"Opened Excel file: {excel_path}")
        except Exception as e:
            self.logger.error(f"Error opening Excel file: {e}")

    def send_powershell_summary_notification(self, title, message, excel_path):
        """Send summary notification using PowerShell with click action"""
        try:
            import tempfile

            # Create a temporary batch file to open Excel
            temp_dir = tempfile.gettempdir()
            batch_file = os.path.join(temp_dir, "open_excel_hackathon.bat")

            with open(batch_file, 'w') as f:
                f.write(f'@echo off\n')
                f.write(f'start "" "{excel_path}"\n')
                f.write(f'del "%~f0"\n')  # Delete the batch file after execution

            # Escape quotes and paths for PowerShell
            title_escaped = title.replace('"', '""').replace("'", "''")
            message_escaped = message.replace('"', '""').replace("'", "''")
            batch_file_escaped = batch_file.replace('"', '""').replace("'", "''")

            # Create PowerShell script that creates a clickable notification
            ps_command = f'''
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# Create notification
$notification = New-Object System.Windows.Forms.NotifyIcon
$notification.Icon = [System.Drawing.SystemIcons]::Information
$notification.BalloonTipTitle = "{title_escaped}"
$notification.BalloonTipText = "{message_escaped}"
$notification.Visible = $true

# Add click event handler that runs the batch file
$notification.add_BalloonTipClicked({{
    try {{
        Start-Process -FilePath "{batch_file_escaped}" -WindowStyle Hidden
    }} catch {{
        # Fallback: try opening Excel directly
        Start-Process -FilePath "{excel_path.replace('"', '""').replace("'", "''")}"
    }}
}})

# Show notification for 15 seconds
$notification.ShowBalloonTip(15000)

# Keep script alive to handle clicks, then cleanup
Start-Sleep -Seconds 20
$notification.Dispose()
            '''

            # Run PowerShell command in background
            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-Command", ps_command],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )

            self.logger.info("PowerShell notification with batch file click action sent")

        except Exception as e:
            raise Exception(f"PowerShell summary notification failed: {e}")

    def send_windows_toast_notification(self, title, message, excel_path):
        """Send Windows 10 toast notification using plyer (alternative method)"""
        try:
            # Try using Windows 10 toast notifications via PowerShell with better approach
            ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$template = @"
<toast activationType="protocol" launch="{excel_path.replace('"', '&quot;')}">
    <visual>
        <binding template="ToastGeneric">
            <text>{title.replace('"', '&quot;')}</text>
            <text>{message.replace('"', '&quot;')}</text>
        </binding>
    </visual>
    <actions>
        <action content="Open Excel" arguments="{excel_path.replace('"', '&quot;')}" activationType="protocol"/>
    </actions>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = New-Object Windows.UI.Notifications.ToastNotification $xml
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Hackathon Monitor").Show($toast)
            '''

            subprocess.Popen(
                ["powershell", "-WindowStyle", "Hidden", "-Command", ps_script],
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
            )
            self.logger.info("Windows toast notification sent")
            return True

        except Exception as e:
            self.logger.warning(f"Windows toast notification failed: {e}")
            return False

    def send_hackathon_notification(self, hackathon):
        """Send a Windows toast notification for a new hackathon"""
        try:
            title = f"New Hackathon: {hackathon.get('name', 'Unknown')}"

            # Create message body
            message_parts = []

            platform = hackathon.get('platform', '')
            if platform:
                message_parts.append(f"Platform: {platform}")

            start_date = hackathon.get('start_date', '')
            if start_date:
                message_parts.append(f"Starts: {start_date}")

            tags = hackathon.get('tags', '')
            if tags:
                message_parts.append(f"Tags: {tags}")

            message = "\n".join(message_parts)

            # Try multiple notification methods
            success = False

            # Method 1: win10toast (if available and working)
            if self.toaster and WIN10TOAST_AVAILABLE:
                try:
                    self.toaster.show_toast(
                        title=title,
                        msg=message,
                        duration=10,
                        icon_path=None,
                        threaded=True
                    )
                    success = True
                except Exception as e:
                    self.logger.warning(f"win10toast failed: {e}")

            # Method 2: PowerShell notification (fallback)
            if not success:
                try:
                    self.send_powershell_notification(title, message)
                    success = True
                except Exception as e:
                    self.logger.warning(f"PowerShell notification failed: {e}")

            # Method 3: Console log (final fallback)
            if not success:
                self.logger.info(f"NOTIFICATION: {title} - {message}")

            self.logger.info(f"Sent notification for hackathon: {hackathon.get('name', 'Unknown')}")

        except Exception as e:
            self.logger.error(f"Error sending notification: {e}")

    def send_powershell_notification(self, title, message):
        """Send notification using PowerShell (more reliable)"""
        try:
            # Escape quotes in the message
            title = title.replace('"', "'")
            message = message.replace('"', "'")

            # PowerShell command to show notification
            ps_command = f'''
            Add-Type -AssemblyName System.Windows.Forms
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Information
            $notification.BalloonTipTitle = "{title}"
            $notification.BalloonTipText = "{message}"
            $notification.Visible = $true
            $notification.ShowBalloonTip(10000)
            Start-Sleep -Seconds 1
            $notification.Dispose()
            '''

            subprocess.run(
                ["powershell", "-Command", ps_command],
                capture_output=True,
                timeout=10
            )

        except Exception as e:
            raise Exception(f"PowerShell notification failed: {e}")
            
    def send_summary_notification(self, count):
        """Send a summary notification about new hackathons found"""
        try:
            if count == 0:
                return
                
            title = "Hackathon Monitor Update"
            message = f"Found {count} new hackathon{'s' if count != 1 else ''}"
            
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=5,
                threaded=True
            )
            
            self.logger.info(f"Sent summary notification for {count} hackathons")
            
        except Exception as e:
            self.logger.error(f"Error sending summary notification: {e}")
            
    def send_error_notification(self, error_message):
        """Send an error notification"""
        try:
            title = "Hackathon Monitor Error"
            message = f"Error occurred: {error_message}"
            
            self.toaster.show_toast(
                title=title,
                msg=message,
                duration=8,
                threaded=True
            )
            
            self.logger.info("Sent error notification")
            
        except Exception as e:
            self.logger.error(f"Error sending error notification: {e}")
            
    def test_notification(self):
        """Send a test notification to verify the system works"""
        try:
            # Test the summary notification with fake data
            import os
            test_excel_path = os.path.join(os.getcwd(), "hackathons_data.xlsx")

            # Create fake hackathons for testing
            test_hackathons = [
                {'name': 'AI Innovation Challenge 2025', 'platform': 'DevPost'},
                {'name': 'Global Hack Week: Data Science', 'platform': 'MLH'},
                {'name': 'Startup Hackathon Mumbai', 'platform': 'Unstop'}
            ]

            self.send_hackathon_summary_notification(
                3, test_excel_path, 25, test_hackathons
            )

            self.logger.info("Sent test notification")
            return True

        except Exception as e:
            self.logger.error(f"Error sending test notification: {e}")
            return False

    def send_simple_notification(self, title, message, duration=30):
        """Send a simple notification with fallback for compatibility"""
        success = False

        # Method 1: Try win10toast if available
        if self.toaster and WIN10TOAST_AVAILABLE:
            try:
                self.toaster.show_toast(
                    title=title,
                    msg=message,
                    duration=duration,
                    icon_path=None,
                    threaded=True
                )
                success = True
            except (TypeError, AttributeError) as e:
                self.logger.warning(f"win10toast simple notification failed: {e}")

        # Method 2: PowerShell fallback
        if not success:
            success = self._send_powershell_notification(title, message)

        # Method 3: Windows msg fallback
        if not success:
            success = self._send_fallback_notification(title, message)

        # Method 4: Console fallback
        if not success:
            print(f"\n🔔 {title}")
            print(f"📝 {message}\n")
            self.logger.info(f"Console notification: {title} - {message}")
            success = True

        if success:
            self.logger.info(f"Sent simple notification: {title}")

        return success

# Create alias for backward compatibility
Notifier = WindowsNotifier
