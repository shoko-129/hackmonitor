#!/usr/bin/env python3
"""
Hackathon Monitor - Web Interface
Modern web-based dashboard that works on any device
"""

from flask import Flask, render_template, jsonify, request, send_file
import threading
import time
import json
import os
from pathlib import Path
from datetime import datetime
import webbrowser
from hackathon_monitor_crossplatform import HackathonMonitor, CrossPlatformNotifier

app = Flask(__name__)

class WebHackathonMonitor:
    def __init__(self):
        self.monitor = HackathonMonitor()
        self.is_monitoring = False
        self.monitoring_thread = None
        self.status = "Ready"
        self.progress = 0
        self.logs = []
        self.stats = {
            'total_hackathons': 0,
            'new_today': 0,
            'last_update': None
        }
    
    def log_message(self, message):
        """Add message to logs"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'message': message,
            'full_timestamp': datetime.now().isoformat()
        }
        self.logs.append(log_entry)
        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]
    
    def update_status(self, status, progress=None):
        """Update status and progress"""
        self.status = status
        if progress is not None:
            self.progress = progress
        self.log_message(f"Status: {status}")
    
    def start_monitoring(self):
        """Start background monitoring"""
        if self.is_monitoring:
            return False
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.update_status("Monitoring started", 50)
        return True
    
    def stop_monitoring(self):
        """Stop background monitoring"""
        self.is_monitoring = False
        self.update_status("Monitoring stopped", 0)
        return True
    
    def scrape_once(self):
        """Run single scraping cycle"""
        def run_scrape():
            try:
                self.update_status("Scraping...", 25)
                self.monitor.run_scraping_cycle()
                self.update_status("Scraping completed", 100)
                self._update_stats()
            except Exception as e:
                self.update_status(f"Scraping failed: {str(e)}", 0)
        
        threading.Thread(target=run_scrape, daemon=True).start()
        return True
    
    def _monitoring_loop(self):
        """Background monitoring loop"""
        while self.is_monitoring:
            try:
                self.update_status("Running scheduled scrape...", 75)
                self.monitor.run_scraping_cycle()
                self._update_stats()
                self.update_status("Monitoring active - waiting for next cycle", 50)
                
                # Wait for next cycle (check every minute if we should stop)
                interval_hours = float(self.monitor.config['SETTINGS']['scraping_interval'])
                wait_minutes = interval_hours * 60
                
                for _ in range(int(wait_minutes)):
                    if not self.is_monitoring:
                        break
                    time.sleep(60)
                    
            except Exception as e:
                self.log_message(f"Monitoring error: {str(e)}")
                time.sleep(300)  # Wait 5 minutes before retry
    
    def _update_stats(self):
        """Update statistics"""
        try:
            hackathons = self.monitor.excel_manager.get_existing_hackathons()
            self.stats['total_hackathons'] = len(hackathons)
            self.stats['last_update'] = datetime.now().isoformat()
            
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

# Global monitor instance
web_monitor = WebHackathonMonitor()

@app.route('/')
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')

@app.route('/api/status')
def api_status():
    """Get current status"""
    return jsonify({
        'status': web_monitor.status,
        'progress': web_monitor.progress,
        'is_monitoring': web_monitor.is_monitoring,
        'stats': web_monitor.stats
    })

@app.route('/api/logs')
def api_logs():
    """Get recent logs"""
    return jsonify({
        'logs': web_monitor.logs[-50:]  # Last 50 logs
    })

@app.route('/api/start_monitoring', methods=['POST'])
def api_start_monitoring():
    """Start monitoring"""
    success = web_monitor.start_monitoring()
    return jsonify({'success': success})

@app.route('/api/stop_monitoring', methods=['POST'])
def api_stop_monitoring():
    """Stop monitoring"""
    success = web_monitor.stop_monitoring()
    return jsonify({'success': success})

@app.route('/api/scrape_once', methods=['POST'])
def api_scrape_once():
    """Run single scrape"""
    success = web_monitor.scrape_once()
    return jsonify({'success': success})

@app.route('/api/test_notification', methods=['POST'])
def api_test_notification():
    """Test notification system"""
    try:
        notifier = CrossPlatformNotifier()
        notifier.send_notification(
            "Hackathon Monitor Test",
            "Web interface notification test successful! 🎉"
        )
        web_monitor.log_message("Test notification sent")
        return jsonify({'success': True})
    except Exception as e:
        web_monitor.log_message(f"Notification test failed: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/download_excel')
def api_download_excel():
    """Download Excel file"""
    excel_file = Path("hackathons_data.xlsx")
    if excel_file.exists():
        return send_file(excel_file, as_attachment=True)
    else:
        return jsonify({'error': 'Excel file not found'}), 404

@app.route('/api/config', methods=['GET', 'POST'])
def api_config():
    """Get or update configuration"""
    if request.method == 'GET':
        config_dict = {}
        for section in web_monitor.monitor.config.sections():
            config_dict[section] = dict(web_monitor.monitor.config[section])
        return jsonify(config_dict)
    
    elif request.method == 'POST':
        try:
            new_config = request.json
            # Update configuration
            for section, options in new_config.items():
                if not web_monitor.monitor.config.has_section(section):
                    web_monitor.monitor.config.add_section(section)
                for option, value in options.items():
                    web_monitor.monitor.config.set(section, option, str(value))
            
            # Save to file
            with open('config.ini', 'w') as f:
                web_monitor.monitor.config.write(f)
            
            web_monitor.log_message("Configuration updated")
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

def create_templates():
    """Create HTML templates"""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)
    
    # Main dashboard template
    dashboard_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎯 Hackathon Monitor</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { text-align: center; color: white; margin-bottom: 30px; }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        
        .dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { 
            background: white; 
            border-radius: 15px; 
            padding: 25px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card:hover { transform: translateY(-5px); }
        .card h3 { color: #667eea; margin-bottom: 15px; font-size: 1.3em; }
        
        .status-card { grid-column: 1 / -1; }
        .status-bar { 
            background: #f0f0f0; 
            border-radius: 10px; 
            height: 20px; 
            margin: 15px 0;
            overflow: hidden;
        }
        .status-progress { 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            height: 100%; 
            transition: width 0.3s ease;
            border-radius: 10px;
        }
        
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
        .stat { text-align: center; padding: 15px; background: #f8f9fa; border-radius: 10px; }
        .stat-number { font-size: 2em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        
        .controls { display: flex; gap: 10px; flex-wrap: wrap; }
        .btn { 
            padding: 12px 24px; 
            border: none; 
            border-radius: 8px; 
            cursor: pointer; 
            font-size: 16px;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .btn-primary { background: #667eea; color: white; }
        .btn-success { background: #28a745; color: white; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-info { background: #17a2b8; color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        
        .logs { max-height: 300px; overflow-y: auto; background: #f8f9fa; padding: 15px; border-radius: 8px; }
        .log-entry { margin-bottom: 8px; font-family: monospace; font-size: 14px; }
        .log-timestamp { color: #666; margin-right: 10px; }
        
        @media (max-width: 768px) {
            .dashboard { grid-template-columns: 1fr; }
            .controls { justify-content: center; }
            .btn { width: 100%; margin-bottom: 10px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Hackathon Monitor</h1>
            <p>Web Dashboard - Monitor hackathons from anywhere</p>
        </div>
        
        <div class="dashboard">
            <!-- Status Card -->
            <div class="card status-card">
                <h3>📊 Status</h3>
                <div id="status-text">Ready</div>
                <div class="status-bar">
                    <div class="status-progress" id="progress-bar" style="width: 0%"></div>
                </div>
                <div class="controls">
                    <button class="btn btn-primary" onclick="scrapeOnce()">🔍 Scrape Once</button>
                    <button class="btn btn-success" id="start-btn" onclick="startMonitoring()">⏰ Start Monitoring</button>
                    <button class="btn btn-danger" id="stop-btn" onclick="stopMonitoring()" disabled>⏹️ Stop Monitoring</button>
                    <button class="btn btn-info" onclick="testNotification()">🔔 Test Notification</button>
                    <a class="btn btn-info" href="/api/download_excel" target="_blank">📊 Download Excel</a>
                </div>
            </div>
            
            <!-- Statistics Card -->
            <div class="card">
                <h3>📈 Statistics</h3>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number" id="total-hackathons">0</div>
                        <div class="stat-label">Total Hackathons</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number" id="new-today">0</div>
                        <div class="stat-label">New Today</div>
                    </div>
                </div>
                <div style="margin-top: 15px; text-align: center; color: #666;">
                    Last Update: <span id="last-update">Never</span>
                </div>
            </div>
            
            <!-- Logs Card -->
            <div class="card">
                <h3>📝 Recent Logs</h3>
                <div class="logs" id="logs-container">
                    <div class="log-entry">
                        <span class="log-timestamp">--:--:--</span>
                        <span>Web dashboard started</span>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Auto-refresh data every 2 seconds
        setInterval(updateStatus, 2000);
        setInterval(updateLogs, 5000);
        
        // Initial load
        updateStatus();
        updateLogs();
        
        async function updateStatus() {
            try {
                const response = await fetch('/api/status');
                const data = await response.json();
                
                document.getElementById('status-text').textContent = data.status;
                document.getElementById('progress-bar').style.width = data.progress + '%';
                
                // Update buttons
                document.getElementById('start-btn').disabled = data.is_monitoring;
                document.getElementById('stop-btn').disabled = !data.is_monitoring;
                
                // Update stats
                document.getElementById('total-hackathons').textContent = data.stats.total_hackathons;
                document.getElementById('new-today').textContent = data.stats.new_today;
                
                if (data.stats.last_update) {
                    const date = new Date(data.stats.last_update);
                    document.getElementById('last-update').textContent = date.toLocaleString();
                }
            } catch (error) {
                console.error('Failed to update status:', error);
            }
        }
        
        async function updateLogs() {
            try {
                const response = await fetch('/api/logs');
                const data = await response.json();
                
                const container = document.getElementById('logs-container');
                container.innerHTML = '';
                
                data.logs.forEach(log => {
                    const entry = document.createElement('div');
                    entry.className = 'log-entry';
                    entry.innerHTML = `
                        <span class="log-timestamp">${log.timestamp}</span>
                        <span>${log.message}</span>
                    `;
                    container.appendChild(entry);
                });
                
                container.scrollTop = container.scrollHeight;
            } catch (error) {
                console.error('Failed to update logs:', error);
            }
        }
        
        async function scrapeOnce() {
            try {
                await fetch('/api/scrape_once', { method: 'POST' });
            } catch (error) {
                alert('Failed to start scraping');
            }
        }
        
        async function startMonitoring() {
            try {
                await fetch('/api/start_monitoring', { method: 'POST' });
            } catch (error) {
                alert('Failed to start monitoring');
            }
        }
        
        async function stopMonitoring() {
            try {
                await fetch('/api/stop_monitoring', { method: 'POST' });
            } catch (error) {
                alert('Failed to stop monitoring');
            }
        }
        
        async function testNotification() {
            try {
                const response = await fetch('/api/test_notification', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                    alert('Test notification sent!');
                } else {
                    alert('Notification test failed: ' + data.error);
                }
            } catch (error) {
                alert('Failed to test notification');
            }
        }
    </script>
</body>
</html>'''
    
    with open(templates_dir / "dashboard.html", 'w', encoding='utf-8') as f:
        f.write(dashboard_html)

def run_web_interface(host='127.0.0.1', port=5000, auto_open=True):
    """Run the web interface"""
    create_templates()
    
    print(f"🌐 Starting Hackathon Monitor Web Interface...")
    print(f"📍 URL: http://{host}:{port}")
    print(f"🎯 Access from any device on your network!")
    
    if auto_open:
        # Open browser after a short delay
        threading.Timer(1.5, lambda: webbrowser.open(f'http://{host}:{port}')).start()
    
    app.run(host=host, port=port, debug=False)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Hackathon Monitor Web Interface')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t auto-open browser')
    
    args = parser.parse_args()
    
    run_web_interface(args.host, args.port, not args.no_browser)
