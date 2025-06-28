# 🎯 MLH Digital Hackathon Monitor - PyQt5 GUI

A modern, cross-platform PyQt5 GUI application specifically designed for monitoring **MLH Digital Only hackathons** and automatically saving them to Excel.

## ✨ Key Features

- **🎯 MLH Digital Only Focus**: Exclusively scrapes MLH for "Digital Only" hackathons
- **🖥️ Modern PyQt5 Interface**: Professional, native-looking GUI with tabbed interface
- **📊 Interactive Data Management**: Sortable table view with export capabilities
- **🔔 Smart Notifications**: Cross-platform notifications with system tray integration
- **⚙️ Comprehensive Settings**: Easy configuration of monitoring preferences
- **📈 Real-time Monitoring**: Live status updates and progress tracking
- **💾 Excel Integration**: Automatic data export with clean MLH event URLs
- **🎨 Modern Styling**: Light/dark themes with Font Awesome icons
- **🔧 Background Operation**: System tray support for background monitoring
- **🌍 Cross-Platform**: Works on Windows, macOS, and Linux

## 🌐 Platform Compatibility

| Platform | Status | Setup Method |
|----------|--------|--------------|
| **🪟 Windows 10/11** | ✅ Fully Supported | `setup_windows.bat` |
| **🐧 Linux** | ✅ Fully Supported | `./launch_pyqt_gui.sh` |
| **🍎 macOS** | ✅ Fully Supported | `./launch_pyqt_gui.sh` |

## 🚀 Quick Start

### 🪟 **Windows Setup**
```cmd
# 1. Double-click to setup:
setup_windows.bat

# 2. Double-click to run:
launch_pyqt_gui.bat
```

### 🐧 **Linux/macOS Setup**
```bash
# 1. Run setup script
chmod +x setup_system.sh
./setup_system.sh

# 2. Run application
./launch_pyqt_gui.sh
```

#### Option 2: Manual Installation
```bash
# Install dependencies
pip install -r requirements_pyqt.txt

# Run the application
python3 hackathon_monitor_pyqt.py
```

#### Option 3: Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv_pyqt
source venv_pyqt/bin/activate  # Linux/macOS
# or
venv_pyqt\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements_pyqt.txt

# Run the application
python hackathon_monitor_pyqt.py
```

## 🖥️ GUI Interface Overview

### Monitor Tab
- **Quick Statistics**: Total hackathons, new today, monitoring status
- **Control Buttons**:
  - 🔍 **Scrape Once**: Run single scraping cycle
  - ▶️ **Start Monitoring**: Begin continuous monitoring
  - ⏹️ **Stop Monitoring**: Stop background monitoring
  - 🔔 **Test Notification**: Verify notification system
- **Activity Log**: Real-time activity feed with timestamps
- **Progress Tracking**: Visual progress indicators during operations

### Data Tab
- **Interactive Table**: View all hackathon data with sorting and filtering
- **Export Functions**:
  - 🔄 **Refresh Data**: Update table with latest data
  - 💾 **Export Excel**: Save data to custom Excel file
  - 📊 **Open Excel**: Open existing Excel file
- **Column Management**: Resizable columns with auto-sizing

### Settings Tab
- **Monitoring Configuration**:
  - Check interval (1-24 hours)
  - Enable/disable notifications
- **Platform Toggles**:
  - Devpost monitoring
  - MLH monitoring
  - Unstop monitoring
- **Appearance Options**:
  - Light/Dark theme selection
  - System tray preferences
- **System Information**: Platform and version details

### Logs Tab
- **Log Viewer**: Syntax-highlighted log display
- **Log Management**:
  - 🔄 **Refresh**: Load latest logs from file
  - 🗑️ **Clear**: Clear current log display
  - 💾 **Save**: Export logs to text file
- **Real-time Updates**: Live log streaming during operations

## ⚙️ Configuration

### Configuration Files
- **`config.ini`**: Backend monitoring configuration
- **GUI Settings**: Automatically saved PyQt5 preferences
- **Log Files**: Located in `logs/hackathon_monitor.log`

### Default Settings
```ini
[SETTINGS]
scraping_interval = 6           # Hours between checks
excel_file = hackathons_data.xlsx
notifications_enabled = true

[PLATFORMS]
devpost = true                  # Enable Devpost monitoring
mlh = true                      # Enable MLH monitoring
unstop = true                   # Enable Unstop monitoring

[FILTERS]
min_days_notice = 1
max_days_advance = 90
keywords = AI,ML,blockchain,web,mobile,hackathon
```

## 📊 Data Management

### Excel Output
The application automatically creates and manages Excel files with:

| Column | Description |
|--------|-------------|
| Name | Hackathon name |
| Platform | Source platform (Devpost, MLH, Unstop) |
| Link | Direct link to hackathon page |
| Start Date | Event start date |
| Tags | Relevant categories and tags |
| Scraped At | Data collection timestamp |
| Status | New/Updated status |

### Export Features
- **Custom Export**: Save data to any location
- **Automatic Backup**: Timestamped export files
- **Format Support**: Excel (.xlsx) format
- **Data Integrity**: Preserves all formatting and data

## 🔔 Notification System

### Platform Support
- **Windows**: Native Windows 10/11 toast notifications
- **macOS**: Native notification center integration
- **Linux**: notify-send and desktop notifications

### Notification Features
- **New Hackathon Alerts**: Immediate notifications for new events
- **Summary Reports**: Periodic monitoring status updates
- **System Tray Integration**: Notifications from background operation
- **Customizable**: Enable/disable in settings

## 🛠️ Advanced Features

### System Tray Integration
- **Background Operation**: Continue monitoring when window is closed
- **Quick Access**: Right-click menu for common actions
- **Status Indicators**: Visual monitoring status in system tray

### Multi-threading
- **Non-blocking UI**: Scraping operations don't freeze the interface
- **Background Monitoring**: Continuous operation without UI interference
- **Progress Tracking**: Real-time updates during long operations

### Error Handling
- **Graceful Degradation**: Continues operation when optional features fail
- **User Feedback**: Clear error messages and recovery suggestions
- **Logging**: Comprehensive error logging for troubleshooting

## 🐛 Troubleshooting

### Common Issues

#### PyQt5 Installation Issues
```bash
# Try alternative installation
pip install PyQt5-Qt5 PyQt5-sip PyQt5

# Or use conda
conda install pyqt
```

#### Missing System Dependencies (Linux)
```bash
sudo apt install python3-dev python3-pip
sudo apt install qt5-default libqt5widgets5
sudo apt install libnotify-bin
```

#### Notification Issues
```bash
# Linux: Test notifications
notify-send "Test" "Notification working"

# Install notification daemon if needed
sudo apt install notification-daemon
```

### Testing Installation
```bash
# Run the test suite
python3 test_pyqt_gui.py
```

### Debug Mode
Check the Logs tab in the GUI or view `logs/hackathon_monitor.log` for detailed information.

## 📁 Project Structure

```
hackathon-monitor-pyqt/
├── hackathon_monitor_pyqt.py      # Main PyQt5 GUI application
├── hackathon_monitor_crossplatform.py  # Backend monitoring logic
├── requirements_pyqt.txt          # PyQt5 dependencies
├── setup_pyqt_gui.py             # Automated setup script
├── test_pyqt_gui.py              # Test suite
├── PYQT_SETUP_GUIDE.md           # Detailed setup guide
├── config.ini                    # Configuration file
├── logo.png                      # Application icon
├── scrapers/                     # Web scraping modules
│   ├── __init__.py
│   └── hackathon_scraper.py
├── storage/                      # Data management
│   ├── __init__.py
│   └── excel_manager.py
├── notifications/                # Notification system
│   ├── __init__.py
│   └── notifier.py
└── logs/                        # Log files (created at runtime)
    └── hackathon_monitor.log
```

## 🔄 Updates and Maintenance

### Updating Dependencies
```bash
# Activate virtual environment (if used)
source venv_pyqt/bin/activate

# Update packages
pip install --upgrade -r requirements_pyqt.txt
```

### Backup Data
```bash
# Backup Excel data
cp hackathons_data.xlsx backup_$(date +%Y%m%d).xlsx

# Backup configuration
cp config.ini config_backup.ini
```

## 📞 Support

### Getting Help
1. **Check Logs**: Use the Logs tab to identify issues
2. **Test Components**: Use the "Test Notification" button
3. **Verify Settings**: Check configuration in Settings tab
4. **Read Documentation**: Refer to `PYQT_SETUP_GUIDE.md`

### Reporting Issues
Include the following information:
- Operating system and version
- Python version (`python --version`)
- PyQt5 version (`pip show PyQt5`)
- Error messages from logs
- Steps to reproduce the issue

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PyQt5**: For the excellent GUI framework
- **Hackathon Platforms**: For providing accessible data
- **Open Source Community**: For the amazing libraries used
- **Contributors**: Everyone who helps improve this project

---

**🎯 Never miss a hackathon opportunity again!**

*Built with ❤️ using Python and PyQt5*