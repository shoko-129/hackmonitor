# 🎯 Hackathon Monitor - Modern Cross-Platform Solution

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Cross-Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](https://github.com/Shiva-129/hackathon-monitor)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A modern, cross-platform application that monitors popular hackathon platforms and sends notifications about new events. Choose from multiple interfaces: Web, Desktop App, Terminal, or Command Line.

## ✨ Key Features

- 🚀 **Auto-Startup**: Automatically starts when Windows boots (optional)
- 🔍 **Background Monitoring**: Continuously scans DevPost, MLH, and Unstop platforms
- 🔔 **Smart Notifications**: Windows notifications with **click-to-open Excel** functionality
- 📊 **Excel Integration**: Automatically saves all hackathon data to organized spreadsheets
- 🖥️ **Modern GUI**: Intuitive graphical interface with real-time progress tracking
- ⏰ **Flexible Scheduling**: One-time scans or continuous 6-hour monitoring
- �️ **Robust Scraping**: Chrome WebDriver-based scraping with error handling
- 🎛️ **Easy Management**: Simple start/stop controls and configuration options

## 🌐 Supported Platforms

| Platform | Website | Features | Status |
|----------|---------|----------|--------|
| **DevPost** | [devpost.com/hackathons](https://devpost.com/hackathons) | Main hackathons page scraping | ✅ Active |
| **MLH** | [mlh.io](https://mlh.io) | Major League Hacking events | ✅ Active |
| **Unstop** | [unstop.com](https://unstop.com) | Competitions and hackathons | ✅ Active |

## � Quick Start

### Prerequisites
- **Windows 10/11**
- **Python 3.8+**
- **Chrome Browser** (for web scraping)

### Installation

#### **Option 1: One-Click Installer (Recommended)**

1. **Download**: [`HackathonMonitor_v1.0.0_Installer.exe`](dist/HackathonMonitor_v1.0.0_Installer.exe) (11.2 MB)
2. **Run**: Double-click the downloaded file
3. **Enable Auto-Startup**: ✅ Check "Start automatically when Windows boots" (Recommended)
4. **Install**: Follow the installer prompts
5. **Automatic Operation**: Application starts on boot and monitors in background

#### **Option 2: Manual Installation**

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/Shiva-129/hackathon-monitor.git
   cd hackathon-monitor-main
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # Universal launcher (choose interface)
   python hackathon_monitor_launcher.py

   # Web interface (recommended)
   python hackathon_monitor_web.py

   # Command line interface
   python hackathon_monitor_cli.py scrape
   ```

4. **Create desktop shortcuts** (optional):
   ```bash
   # Create shortcuts for easy access
   python create_shortcuts.py

   # Creates desktop shortcuts for:
   # - Web Interface
   # - Universal Launcher
   # - CLI Interface
   ```

## �️ Using the Application

### GUI Interface

The **Hackathon Monitor GUI** provides an easy-to-use interface:

1. **Launch the GUI**: `python hackathon_monitor_gui.py`
2. **Choose your monitoring mode**:
   - **🔍 Scrape Once**: Single scan of all platforms
   - **⏰ Start 6-Hour Monitoring**: Continuous monitoring every 6 hours
3. **Monitor progress**: Real-time status updates and logs
4. **Access data**: Click **📊 Open Excel** to view collected hackathons
5. **Test notifications**: Use **🔔 Test Notification** to verify setup

### Key GUI Features

- **Real-time Progress**: See scraping progress with platform-specific updates
- **Live Logs**: Monitor application activity in the log window
- **Easy Controls**: Start/stop monitoring with simple buttons
- **Status Indicators**: Visual feedback on application state
- **Quick Access**: Direct buttons to open Excel and test notifications

### Command Line Usage

For advanced users or automation:

```bash
# Run a single scraping cycle
python hackathon_monitor.py

# Run with specific configuration
python hackathon_monitor.py --config custom_config.ini

# Test notifications
python manage_service.py test
```

## ⚙️ Configuration

The application uses `config.ini` for customization. Here are the key settings:

```ini
[SETTINGS]
# Excel file location
excel_file = hackathons_data.xlsx

# Enable/disable notifications
notifications_enabled = true

[PLATFORMS]
# Enable/disable specific platforms
devpost = true
mlh = true
unstop = true
```

### Platform Configuration

- **DevPost**: Scrapes the main hackathons page (devpost.com/hackathons)
- **MLH**: Monitors Major League Hacking events
- **Unstop**: Tracks competitions and hackathons

You can enable/disable any platform by setting its value to `true` or `false` in the config file.

## 📊 Data Storage & Notifications

### Excel Integration

All hackathon data is automatically saved to `hackathons_data.xlsx` with these columns:

| Column | Description |
|--------|-------------|
| **Name** | Hackathon title |
| **Platform** | Source platform (DevPost, MLH, Unstop) |
| **URL** | Direct link to hackathon page |
| **Deadline** | Registration/submission deadline |
| **Tags** | Categories and technologies |
| **Scraped At** | When the data was collected |

### Smart Notifications

- **🔔 Instant Alerts**: Get notified immediately when new hackathons are found
- **📱 Click-to-Open**: Click notifications to automatically open the Excel file
- **📋 Detailed Info**: Notifications show hackathon names and total counts
- **🔄 Multiple Methods**: Uses Windows Toast, PowerShell, and fallback notifications

## 🛠️ Advanced Usage

### Windows Service (Optional)

For background operation, you can install as a Windows service:

```bash
# Install service (requires admin privileges)
python manage_service.py install

# Start/stop service
python manage_service.py start
python manage_service.py stop

# Remove service
python manage_service.py remove
```

## 📁 Project Structure

```
hackathon-monitor-main/
├── hackathon_monitor.py         # Main monitoring script
├── hackathon_monitor_gui.py     # GUI application
├── config.ini                  # Configuration settings
├── requirements.txt            # Python dependencies
├── installer.py               # Installation utilities
├── manage_service.py          # Service management
├── hackathons_data.xlsx       # Generated data file
├── notifications/             # Notification system
│   ├── __init__.py
│   └── notifier.py           # Windows notifications with click-to-open
├── scrapers/                 # Web scraping modules
│   ├── __init__.py
│   └── hackathon_scraper.py  # Platform scrapers
├── storage/                  # Data management
│   ├── __init__.py
│   └── excel_manager.py      # Excel file operations
└── service/                  # Windows service support
    ├── __init__.py
    └── windows_service.py
```

## 🔧 Troubleshooting

### Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| **Notifications not appearing** | Check Windows notification settings; try test notification |
| **Excel file won't open** | Ensure Excel is installed and .xlsx files are associated |
| **Chrome driver errors** | Chrome browser must be installed; driver auto-downloads |
| **Scraping failures** | Check internet connection; some sites may be temporarily down |
| **Permission errors** | Run as administrator for service installation |

### Testing Your Setup

```bash
# Test notifications (should show a test notification)
python manage_service.py test

# Test Excel opening (should open the data file)
python -c "import os; os.startfile('hackathons_data.xlsx')"

# Test single scraping cycle
python hackathon_monitor_gui.py
# Then click "🔍 Scrape Once" button
```

### Debug Information

- **Logs**: Check console output in GUI for real-time debugging
- **Excel File**: Verify `hackathons_data.xlsx` is created and populated
- **Config**: Ensure `config.ini` has correct platform settings
- **Dependencies**: Run `pip list` to verify all packages are installed

## 🚀 Tips for Best Results

1. **First Run**: Use "🔍 Scrape Once" to test and populate initial data
2. **Notifications**: Test notifications before starting continuous monitoring
3. **Excel**: Keep the Excel file closed during scraping to avoid conflicts
4. **Chrome**: Ensure Chrome browser is updated to latest version
5. **Internet**: Stable internet connection improves scraping reliability

## 📝 License

This project is open source and available under the MIT License. Feel free to modify and distribute.

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional hackathon platforms
- Enhanced notification features
- Better error handling
- UI/UX improvements

## 📞 Support

If you encounter issues:
1. **Check the GUI logs** for error messages
2. **Verify your configuration** in `config.ini`
3. **Test individual components** using the troubleshooting commands above
4. **Ensure all dependencies** are properly installed

---

**Happy Hackathon Hunting! 🎯**
