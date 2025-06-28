#!/usr/bin/env python3
"""
Hackathon Monitor - Modern PyQt5 GUI Version
A modern, feature-rich GUI application for monitoring hackathon platforms.
Uses the existing backend logic with a beautiful PyQt5 interface.
"""

import sys
import os
import json
import platform
import threading
import subprocess
from datetime import datetime
from pathlib import Path

# PyQt5 imports
try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QTabWidget, QLabel, QPushButton, QProgressBar, QTextEdit,
        QTableWidget, QTableWidgetItem, QHeaderView, QSplitter,
        QGroupBox, QFormLayout, QSpinBox, QCheckBox, QComboBox,
        QLineEdit, QFileDialog, QMessageBox, QSystemTrayIcon,
        QMenu, QAction, QStatusBar, QFrame, QScrollArea
    )
    from PyQt5.QtCore import (
        Qt, QThread, pyqtSignal, QTimer, QSettings, QSize
    )
    from PyQt5.QtGui import (
        QIcon, QPixmap, QFont, QPalette, QColor
    )
    PYQT_AVAILABLE = True
except ImportError:
    print("PyQt5 not available. Please install with: pip install PyQt5")
    PYQT_AVAILABLE = False

# Optional imports for enhanced styling
try:
    import qdarkstyle
    DARK_STYLE_AVAILABLE = True
except ImportError:
    DARK_STYLE_AVAILABLE = False

try:
    import qtawesome as qta
    ICONS_AVAILABLE = True
except ImportError:
    ICONS_AVAILABLE = False

# Import our backend modules
from scrapers.hackathon_scraper import HackathonScraper
from storage.excel_manager import ExcelManager
from notifications.notifier import CrossPlatformNotifier

class ModernHackathonMonitorGUI(QMainWindow):
    """Modern PyQt5 GUI for Hackathon Monitor"""
    
    def __init__(self):
        super().__init__()
        
        # Load configuration first
        import configparser
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        # Initialize backend
        self.scraper = HackathonScraper()
        excel_file = self.config.get('SETTINGS', 'excel_file', fallback='hackathons_data.xlsx')
        self.excel_manager = ExcelManager(excel_file)
        self.notifier = CrossPlatformNotifier()
        
        # GUI state
        self.is_monitoring = False
        self.monitoring_thread = None
        
        # Settings
        self.settings = QSettings('HackathonMonitor', 'PyQtGUI')
        
        # Setup UI
        self.init_ui()
        self.setup_system_tray()
        self.load_settings()
        
        # Setup timers
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_display)
        self.status_timer.start(1000)  # Update every second
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle(f"Hackathon Monitor - Modern GUI ({platform.system()})")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Set application icon
        self.set_app_icon()
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Create header
        self.create_header(main_layout)
        
        # Create main content area with tabs
        self.create_main_content(main_layout)
        
        # Create status bar
        self.create_status_bar()
        
        # Apply modern styling
        self.apply_modern_style()
        
    def set_app_icon(self):
        """Set application icon"""
        try:
            logo_path = Path("logo.png")
            if logo_path.exists():
                icon = QIcon(str(logo_path))
                self.setWindowIcon(icon)
            elif ICONS_AVAILABLE:
                # Use font awesome icon as fallback
                icon = qta.icon('fa5s.search', color='#2196F3')
                self.setWindowIcon(icon)
        except Exception as e:
            print(f"Could not set app icon: {e}")
    
    def create_header(self, parent_layout):
        """Create the application header"""
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setMaximumHeight(80)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Logo and title
        title_layout = QVBoxLayout()
        
        title_label = QLabel("🎯 Hackathon Monitor")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2196F3; margin: 5px;")
        
        subtitle_label = QLabel(f"Modern GUI • {platform.system()} • Python {platform.python_version()}")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #666; margin: 2px;")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 20))
        self.status_indicator.setStyleSheet("color: #4CAF50; margin: 10px;")
        self.status_indicator.setToolTip("System Status: Ready")
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addWidget(self.status_indicator)
        
        parent_layout.addWidget(header_frame)
    
    def create_main_content(self, parent_layout):
        """Create the main content area with tabs"""
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        
        # Create tabs
        self.create_monitor_tab()
        self.create_data_tab()
        self.create_settings_tab()
        self.create_logs_tab()
        
        parent_layout.addWidget(self.tab_widget)
    
    def create_monitor_tab(self):
        """Create the main monitoring tab"""
        monitor_widget = QWidget()
        layout = QVBoxLayout(monitor_widget)
        
        # Quick stats section
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QHBoxLayout(stats_group)
        
        self.total_hackathons_label = QLabel("Total: 0")
        self.new_today_label = QLabel("New Today: 0")
        self.monitoring_status_label = QLabel("Status: Ready")
        
        for label in [self.total_hackathons_label, self.new_today_label, self.monitoring_status_label]:
            label.setFont(QFont("Arial", 11))
            label.setStyleSheet("padding: 10px; background: #f5f5f5; border-radius: 5px; margin: 2px;")
            stats_layout.addWidget(label)
        
        layout.addWidget(stats_group)
        
        # Control buttons section
        controls_group = QGroupBox("Monitoring Controls")
        controls_layout = QVBoxLayout(controls_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Create buttons with icons if available
        if ICONS_AVAILABLE:
            self.scrape_once_btn = QPushButton(qta.icon('fa5s.search'), " Scrape Once")
            self.start_monitor_btn = QPushButton(qta.icon('fa5s.play'), " Start Monitoring")
            self.stop_monitor_btn = QPushButton(qta.icon('fa5s.stop'), " Stop Monitoring")
            self.test_notification_btn = QPushButton(qta.icon('fa5s.bell'), " Test Notification")
        else:
            self.scrape_once_btn = QPushButton("🔍 Scrape Once")
            self.start_monitor_btn = QPushButton("▶️ Start Monitoring")
            self.stop_monitor_btn = QPushButton("⏹️ Stop Monitoring")
            self.test_notification_btn = QPushButton("🔔 Test Notification")
        
        # Configure buttons
        self.stop_monitor_btn.setEnabled(False)
        
        # Connect button signals
        self.scrape_once_btn.clicked.connect(self.scrape_once)
        self.start_monitor_btn.clicked.connect(self.start_monitoring)
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        self.test_notification_btn.clicked.connect(self.test_notification)
        
        # Add buttons to layout
        for btn in [self.scrape_once_btn, self.start_monitor_btn, 
                   self.stop_monitor_btn, self.test_notification_btn]:
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
            button_layout.addWidget(btn)
        
        controls_layout.addLayout(button_layout)
        layout.addWidget(controls_group)
        
        # Recent activity section
        activity_group = QGroupBox("Recent Activity")
        activity_layout = QVBoxLayout(activity_group)
        
        self.activity_text = QTextEdit()
        self.activity_text.setMaximumHeight(200)
        self.activity_text.setReadOnly(True)
        self.activity_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
            }
        """)
        
        activity_layout.addWidget(self.activity_text)
        layout.addWidget(activity_group)
        
        # Add initial message
        self.log_activity("🎯 Hackathon Monitor initialized and ready!")
        
        self.tab_widget.addTab(monitor_widget, "Monitor")

    def create_data_tab(self):
        """Create the data visualization tab"""
        data_widget = QWidget()
        layout = QVBoxLayout(data_widget)

        # Controls section
        controls_group = QGroupBox("Data Controls")
        controls_layout = QHBoxLayout(controls_group)

        if ICONS_AVAILABLE:
            refresh_btn = QPushButton(qta.icon('fa5s.sync'), " Refresh Data")
            export_btn = QPushButton(qta.icon('fa5s.download'), " Export Excel")
            open_excel_btn = QPushButton(qta.icon('fa5s.table'), " Open Excel")
        else:
            refresh_btn = QPushButton("🔄 Refresh Data")
            export_btn = QPushButton("💾 Export Excel")
            open_excel_btn = QPushButton("📊 Open Excel")

        refresh_btn.clicked.connect(self.refresh_data_table)
        export_btn.clicked.connect(self.export_data)
        open_excel_btn.clicked.connect(self.open_excel_file)

        for btn in [refresh_btn, export_btn, open_excel_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            controls_layout.addWidget(btn)

        controls_layout.addStretch()
        layout.addWidget(controls_group)

        # Data table
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.data_table.setSortingEnabled(True)

        # Set table headers
        headers = ['Name', 'Platform', 'Start Date', 'Tags', 'Scraped At', 'Status']
        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)

        # Configure table appearance
        header = self.data_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Name column stretches
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

        layout.addWidget(self.data_table)

        # Load initial data
        self.refresh_data_table()

        self.tab_widget.addTab(data_widget, "Data")

    def create_settings_tab(self):
        """Create the settings configuration tab"""
        settings_widget = QWidget()
        layout = QVBoxLayout(settings_widget)

        # Create scroll area for settings
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Monitoring settings
        monitoring_group = QGroupBox("Monitoring Settings")
        monitoring_layout = QFormLayout(monitoring_group)

        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 24)
        self.interval_spinbox.setValue(6)
        self.interval_spinbox.setSuffix(" hours")

        self.notifications_checkbox = QCheckBox()
        self.notifications_checkbox.setChecked(True)

        monitoring_layout.addRow("Check Interval:", self.interval_spinbox)
        monitoring_layout.addRow("Enable Notifications:", self.notifications_checkbox)

        scroll_layout.addWidget(monitoring_group)

        # Platform settings
        platform_group = QGroupBox("Platform Settings")
        platform_layout = QFormLayout(platform_group)

        self.devpost_checkbox = QCheckBox()
        self.devpost_checkbox.setChecked(True)
        self.mlh_checkbox = QCheckBox()
        self.mlh_checkbox.setChecked(True)
        self.unstop_checkbox = QCheckBox()
        self.unstop_checkbox.setChecked(True)

        platform_layout.addRow("Enable Devpost:", self.devpost_checkbox)
        platform_layout.addRow("Enable MLH:", self.mlh_checkbox)
        platform_layout.addRow("Enable Unstop:", self.unstop_checkbox)

        scroll_layout.addWidget(platform_group)

        # Appearance settings
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QFormLayout(appearance_group)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])

        self.minimize_to_tray_checkbox = QCheckBox()
        self.minimize_to_tray_checkbox.setChecked(True)

        appearance_layout.addRow("Theme:", self.theme_combo)
        appearance_layout.addRow("Minimize to Tray:", self.minimize_to_tray_checkbox)

        scroll_layout.addWidget(appearance_group)

        # System information
        system_group = QGroupBox("System Information")
        system_layout = QFormLayout(system_group)

        system_layout.addRow("Operating System:", QLabel(platform.system()))
        system_layout.addRow("Architecture:", QLabel(platform.machine()))
        system_layout.addRow("Python Version:", QLabel(platform.python_version()))

        scroll_layout.addWidget(system_group)

        # Save button
        save_btn = QPushButton("💾 Save Settings")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        save_btn.clicked.connect(self.save_application_settings)

        scroll_layout.addWidget(save_btn)
        scroll_layout.addStretch()

        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        self.tab_widget.addTab(settings_widget, "Settings")

    def create_logs_tab(self):
        """Create the logs viewing tab"""
        logs_widget = QWidget()
        layout = QVBoxLayout(logs_widget)

        # Log controls
        controls_group = QGroupBox("Log Controls")
        controls_layout = QHBoxLayout(controls_group)

        if ICONS_AVAILABLE:
            refresh_logs_btn = QPushButton(qta.icon('fa5s.sync'), " Refresh")
            clear_logs_btn = QPushButton(qta.icon('fa5s.trash'), " Clear")
            save_logs_btn = QPushButton(qta.icon('fa5s.save'), " Save")
        else:
            refresh_logs_btn = QPushButton("🔄 Refresh")
            clear_logs_btn = QPushButton("🗑️ Clear")
            save_logs_btn = QPushButton("💾 Save")

        refresh_logs_btn.clicked.connect(self.refresh_logs)
        clear_logs_btn.clicked.connect(self.clear_logs)
        save_logs_btn.clicked.connect(self.save_logs)

        for btn in [refresh_logs_btn, clear_logs_btn, save_logs_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF9800;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #F57C00;
                }
            """)
            controls_layout.addWidget(btn)

        controls_layout.addStretch()
        layout.addWidget(controls_group)

        # Log display
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #555555;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
                font-size: 12px;
            }
        """)

        layout.addWidget(self.log_text)

        # Load initial logs
        self.refresh_logs()

        self.tab_widget.addTab(logs_widget, "Logs")
    
    def apply_modern_style(self):
        """Apply modern styling to the application"""
        if DARK_STYLE_AVAILABLE:
            # Option to use dark style
            use_dark = self.settings.value('use_dark_theme', False, type=bool)
            if use_dark:
                self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
                return
        
        # Custom light theme
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2196F3;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    
    def log_activity(self, message):
        """Add a message to the activity log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.activity_text.append(formatted_message)

        # Auto-scroll to bottom
        cursor = self.activity_text.textCursor()
        cursor.movePosition(cursor.End)
        self.activity_text.setTextCursor(cursor)

    def create_status_bar(self):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Add permanent widgets to status bar
        self.status_label = QLabel("Ready")
        self.platform_label = QLabel(f"{platform.system()}")
        self.time_label = QLabel(datetime.now().strftime("%H:%M:%S"))

        self.status_bar.addWidget(self.status_label)
        self.status_bar.addPermanentWidget(self.platform_label)
        self.status_bar.addPermanentWidget(self.time_label)

    def setup_system_tray(self):
        """Setup system tray icon"""
        try:
            if QSystemTrayIcon.isSystemTrayAvailable():
                self.tray_icon = QSystemTrayIcon(self)

                # Set tray icon
                if Path("logo.png").exists():
                    self.tray_icon.setIcon(QIcon("logo.png"))
                else:
                    self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_ComputerIcon))

                # Create tray menu
                tray_menu = QMenu()

                show_action = QAction("Show", self)
                show_action.triggered.connect(self.show)

                quit_action = QAction("Quit", self)
                quit_action.triggered.connect(self.close)

                tray_menu.addAction(show_action)
                tray_menu.addSeparator()
                tray_menu.addAction(quit_action)

                self.tray_icon.setContextMenu(tray_menu)
                self.tray_icon.show()

                # Connect double-click to show window
                self.tray_icon.activated.connect(self.tray_icon_activated)

        except Exception as e:
            print(f"System tray setup failed: {e}")

    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()
            self.raise_()
            self.activateWindow()

    def update_status_display(self):
        """Update status display elements"""
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

        # Update monitoring status
        if self.is_monitoring:
            self.status_indicator.setStyleSheet("color: #FF9800; margin: 10px;")
            self.status_indicator.setToolTip("System Status: Monitoring Active")
            self.monitoring_status_label.setText("Status: Monitoring")
        else:
            self.status_indicator.setStyleSheet("color: #4CAF50; margin: 10px;")
            self.status_indicator.setToolTip("System Status: Ready")
            self.monitoring_status_label.setText("Status: Ready")

    def load_settings(self):
        """Load application settings"""
        try:
            # Restore window geometry
            geometry = self.settings.value('geometry')
            if geometry:
                self.restoreGeometry(geometry)

            # Load other settings
            self.log_activity("Settings loaded successfully")
        except Exception as e:
            self.log_activity(f"Failed to load settings: {e}")

    def save_settings(self):
        """Save application settings"""
        try:
            # Save window geometry
            self.settings.setValue('geometry', self.saveGeometry())

            self.log_activity("Settings saved successfully")
        except Exception as e:
            self.log_activity(f"Failed to save settings: {e}")

    def scrape_once(self):
        """Run a single scraping cycle"""
        self.log_activity("Starting MLH Digital Only scraping cycle...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Disable button during operation
        self.scrape_once_btn.setEnabled(False)

        # Run scraping in separate thread
        self.scraping_thread = ScrapingThread(self.scraper, self.excel_manager, self.config)
        self.scraping_thread.finished.connect(self.on_scraping_finished)
        self.scraping_thread.progress.connect(self.log_activity)
        self.scraping_thread.start()

    def on_scraping_finished(self, success, message):
        """Handle scraping completion"""
        self.progress_bar.setVisible(False)
        self.scrape_once_btn.setEnabled(True)

        if success:
            self.log_activity(f"✅ {message}")
            self.update_hackathon_stats()
        else:
            self.log_activity(f"❌ {message}")

    def start_monitoring(self):
        """Start continuous monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.start_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.setEnabled(True)

        self.log_activity("🔄 Starting continuous monitoring...")

        # Start monitoring thread
        self.monitoring_thread = MonitoringThread(self.scraper, self.excel_manager, self.config)
        self.monitoring_thread.progress.connect(self.log_activity)
        self.monitoring_thread.start()

    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if not self.is_monitoring:
            return

        self.is_monitoring = False
        self.start_monitor_btn.setEnabled(True)
        self.stop_monitor_btn.setEnabled(False)

        self.log_activity("⏹️ Stopping monitoring...")

        if self.monitoring_thread:
            self.monitoring_thread.stop()

    def test_notification(self):
        """Test the notification system"""
        self.log_activity("Testing notification system...")

        try:
            self.notifier.send_notification(
                "Hackathon Monitor Test",
                f"Notification system working on {platform.system()}! 🎉"
            )
            self.log_activity("✅ Test notification sent!")
        except Exception as e:
            self.log_activity(f"❌ Notification test failed: {e}")

    def update_hackathon_stats(self):
        """Update hackathon statistics display"""
        try:
            existing_hackathons = self.excel_manager.get_existing_hackathons()
            total_count = len(existing_hackathons)

            # Count today's hackathons
            today = datetime.now().strftime('%Y-%m-%d')
            new_today = sum(1 for h in existing_hackathons
                          if h.get('scraped_at', '').startswith(today))

            self.total_hackathons_label.setText(f"Total: {total_count}")
            self.new_today_label.setText(f"New Today: {new_today}")

        except Exception as e:
            self.log_activity(f"Failed to update stats: {e}")

    def refresh_data_table(self):
        """Refresh the data table with current hackathons"""
        try:
            hackathons = self.excel_manager.get_existing_hackathons()

            self.data_table.setRowCount(len(hackathons))

            for row, hackathon in enumerate(hackathons):
                self.data_table.setItem(row, 0, QTableWidgetItem(hackathon.get('name', '')))
                self.data_table.setItem(row, 1, QTableWidgetItem(hackathon.get('platform', '')))
                self.data_table.setItem(row, 2, QTableWidgetItem(hackathon.get('start_date', '')))
                self.data_table.setItem(row, 3, QTableWidgetItem(hackathon.get('tags', '')))
                self.data_table.setItem(row, 4, QTableWidgetItem(hackathon.get('scraped_at', '')))
                self.data_table.setItem(row, 5, QTableWidgetItem(hackathon.get('status', 'New')))

            self.log_activity(f"Data table refreshed with {len(hackathons)} hackathons")

        except Exception as e:
            self.log_activity(f"Failed to refresh data table: {e}")

    def export_data(self):
        """Export data to a new Excel file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Export Hackathons Data",
                f"hackathons_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                "Excel Files (*.xlsx);;All Files (*)"
            )

            if file_path:
                # Copy the current Excel file to the new location
                import shutil
                excel_file = Path(self.config.get('SETTINGS', 'excel_file', fallback='hackathons_data.xlsx'))
                if excel_file.exists():
                    shutil.copy2(excel_file, file_path)
                    self.log_activity(f"Data exported to: {file_path}")
                    QMessageBox.information(self, "Export Complete", f"Data exported successfully to:\n{file_path}")
                else:
                    QMessageBox.warning(self, "Export Failed", "No data file found to export.")

        except Exception as e:
            self.log_activity(f"Export failed: {e}")
            QMessageBox.critical(self, "Export Error", f"Failed to export data:\n{str(e)}")

    def open_excel_file(self):
        """Open the Excel file with the default application"""
        try:
            excel_file = Path(self.config.get('SETTINGS', 'excel_file', fallback='hackathons_data.xlsx'))

            if not excel_file.exists():
                QMessageBox.warning(self, "File Not Found",
                                  "Excel file not found. Run scraping first to create it.")
                return

            # Open file with default application
            if platform.system() == "Windows":
                os.startfile(excel_file)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", excel_file])
            else:  # Linux
                subprocess.run(["xdg-open", excel_file])

            self.log_activity(f"Opened Excel file: {excel_file}")

        except Exception as e:
            self.log_activity(f"Failed to open Excel file: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open Excel file:\n{str(e)}")

    def save_application_settings(self):
        """Save application settings"""
        try:
            # Save GUI settings
            self.settings.setValue('monitoring_interval', self.interval_spinbox.value())
            self.settings.setValue('notifications_enabled', self.notifications_checkbox.isChecked())
            self.settings.setValue('devpost_enabled', self.devpost_checkbox.isChecked())
            self.settings.setValue('mlh_enabled', self.mlh_checkbox.isChecked())
            self.settings.setValue('unstop_enabled', self.unstop_checkbox.isChecked())
            self.settings.setValue('use_dark_theme', self.theme_combo.currentText() == "Dark")
            self.settings.setValue('minimize_to_tray', self.minimize_to_tray_checkbox.isChecked())

            # Update backend config
            self.config.set('SETTINGS', 'scraping_interval', str(self.interval_spinbox.value()))
            self.config.set('SETTINGS', 'notifications_enabled',
                                  str(self.notifications_checkbox.isChecked()).lower())
            self.config.set('PLATFORMS', 'devpost', str(self.devpost_checkbox.isChecked()).lower())
            self.config.set('PLATFORMS', 'mlh', str(self.mlh_checkbox.isChecked()).lower())
            self.config.set('PLATFORMS', 'unstop', str(self.unstop_checkbox.isChecked()).lower())

            # Save config file
            with open('config.ini', 'w') as configfile:
                self.config.write(configfile)

            self.log_activity("Settings saved successfully!")
            QMessageBox.information(self, "Settings Saved", "Settings have been saved successfully!")

        except Exception as e:
            self.log_activity(f"Failed to save settings: {e}")
            QMessageBox.critical(self, "Settings Error", f"Failed to save settings:\n{str(e)}")

    def refresh_logs(self):
        """Refresh logs from the log file"""
        try:
            log_file = Path("logs/hackathon_monitor.log")
            if log_file.exists():
                with open(log_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log_text.setPlainText(content)

                # Scroll to bottom
                cursor = self.log_text.textCursor()
                cursor.movePosition(cursor.End)
                self.log_text.setTextCursor(cursor)

                self.log_activity("Logs refreshed from file")
            else:
                self.log_text.setPlainText("No log file found.")

        except Exception as e:
            self.log_activity(f"Failed to refresh logs: {e}")
            self.log_text.setPlainText(f"Error reading log file: {str(e)}")

    def clear_logs(self):
        """Clear the log display"""
        self.log_text.clear()
        self.log_activity("Log display cleared")

    def save_logs(self):
        """Save logs to a file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Save Logs",
                f"hackathon_monitor_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                "Text Files (*.txt);;All Files (*)"
            )

            if file_path:
                content = self.log_text.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                self.log_activity(f"Logs saved to: {file_path}")
                QMessageBox.information(self, "Logs Saved", f"Logs saved successfully to:\n{file_path}")

        except Exception as e:
            self.log_activity(f"Failed to save logs: {e}")
            QMessageBox.critical(self, "Save Error", f"Failed to save logs:\n{str(e)}")

    def closeEvent(self, event):
        """Handle application close event"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            # Hide to system tray instead of closing
            self.hide()
            event.ignore()
        else:
            # Save settings and close
            self.save_settings()
            if self.is_monitoring and self.monitoring_thread:
                self.monitoring_thread.stop()
            event.accept()


class ScrapingThread(QThread):
    """Worker thread for single scraping operations"""
    finished = pyqtSignal(bool, str)  # success, message
    progress = pyqtSignal(str)  # progress message

    def __init__(self, scraper, excel_manager, config):
        super().__init__()
        self.scraper = scraper
        self.excel_manager = excel_manager
        self.config = config

    def run(self):
        """Run the scraping operation"""
        try:
            self.progress.emit("Getting existing hackathons...")
            existing_hackathons = self.excel_manager.get_existing_hackathons()
            existing_count = len(existing_hackathons)

            self.progress.emit("Running MLH Digital Only scraping...")
            new_hackathons = self.scraper.scrape_all_platforms(self.config, existing_hackathons)

            if new_hackathons:
                self.progress.emit("Saving new hackathons to Excel...")
                self.excel_manager.save_hackathons(new_hackathons)

            self.progress.emit("Checking for new hackathons...")
            total_hackathons = self.excel_manager.get_existing_hackathons()
            new_count = len(total_hackathons)
            found_new = len(new_hackathons)

            if found_new > 0:
                message = f"Scraping completed! Found {found_new} new Digital Only hackathons (Total: {new_count})"
            else:
                message = f"Scraping completed! No new Digital Only hackathons found (Total: {new_count})"

            self.finished.emit(True, message)

        except Exception as e:
            self.finished.emit(False, f"Scraping failed: {str(e)}")


class MonitoringThread(QThread):
    """Worker thread for continuous monitoring"""
    progress = pyqtSignal(str)  # progress message

    def __init__(self, scraper, excel_manager, config):
        super().__init__()
        self.scraper = scraper
        self.excel_manager = excel_manager
        self.config = config
        self.running = True

    def run(self):
        """Run continuous monitoring"""
        try:
            self.progress.emit("Continuous monitoring started...")

            # Use scheduling for monitoring
            import schedule
            import time

            # Clear any existing jobs
            schedule.clear()

            # Schedule monitoring based on config
            interval = int(self.config.get('SETTINGS', 'scraping_interval', fallback=6))
            schedule.every(interval).hours.do(self.run_scheduled_scrape)

            self.progress.emit(f"Monitoring scheduled every {interval} hours")

            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        except Exception as e:
            self.progress.emit(f"Monitoring error: {str(e)}")

    def run_scheduled_scrape(self):
        """Run a scheduled scraping cycle"""
        try:
            self.progress.emit("Running scheduled MLH Digital Only scraping...")
            existing_hackathons = self.excel_manager.get_existing_hackathons()
            new_hackathons = self.scraper.scrape_all_platforms(self.config, existing_hackathons)

            if new_hackathons:
                self.excel_manager.save_hackathons(new_hackathons)
                self.progress.emit(f"Scheduled scraping completed - Found {len(new_hackathons)} new hackathons")
            else:
                self.progress.emit("Scheduled scraping completed - No new hackathons found")
        except Exception as e:
            self.progress.emit(f"Scheduled scraping failed: {str(e)}")

    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.progress.emit("Monitoring stopped")
        self.quit()
        self.wait()


def main():
    """Main application entry point"""
    if not PYQT_AVAILABLE:
        print("PyQt5 is required but not installed.")
        print("Please install with: pip install PyQt5")
        sys.exit(1)

    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Hackathon Monitor")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("HackathonMonitor")

    # Set application icon
    try:
        if Path("logo.png").exists():
            app.setWindowIcon(QIcon("logo.png"))
    except:
        pass

    # Create and show main window
    window = ModernHackathonMonitorGUI()
    window.show()

    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
