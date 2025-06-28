#!/usr/bin/env python3
"""
Hackathon Monitor - Command Line Interface (CLI)
Simple, powerful command-line interface for automation and scripting
"""

import argparse
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from hackathon_monitor_crossplatform import HackathonMonitor, CrossPlatformNotifier

class CLIHackathonMonitor:
    def __init__(self):
        self.monitor = HackathonMonitor()
        self.notifier = CrossPlatformNotifier()
    
    def scrape_once(self, verbose=False, output_format='text'):
        """Run single scraping cycle"""
        if verbose:
            print("🔍 Starting single scraping cycle...")
        
        try:
            # Get existing hackathons count
            existing = self.monitor.excel_manager.get_existing_hackathons()
            old_count = len(existing)
            
            # Run scraping
            self.monitor.run_scraping_cycle()
            
            # Get new count
            new_hackathons = self.monitor.excel_manager.get_existing_hackathons()
            new_count = len(new_hackathons)
            found_new = new_count - old_count
            
            # Output results
            if output_format == 'json':
                result = {
                    'success': True,
                    'total_hackathons': new_count,
                    'new_hackathons': found_new,
                    'timestamp': datetime.now().isoformat()
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"✅ Scraping completed!")
                print(f"📊 Total hackathons: {new_count}")
                print(f"🆕 New hackathons found: {found_new}")
                if found_new > 0:
                    print(f"💾 Data saved to: hackathons_data.xlsx")
            
            return True
            
        except Exception as e:
            if output_format == 'json':
                result = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Scraping failed: {e}")
            return False
    
    def start_monitoring(self, interval=None, verbose=False):
        """Start continuous monitoring"""
        if interval:
            # Update config with new interval
            self.monitor.config.set('SETTINGS', 'scraping_interval', str(interval))
            with open('config.ini', 'w') as f:
                self.monitor.config.write(f)
        
        interval_hours = float(self.monitor.config['SETTINGS']['scraping_interval'])
        
        if verbose:
            print(f"⏰ Starting monitoring (every {interval_hours} hours)")
            print("Press Ctrl+C to stop")
        
        try:
            self.monitor.start_monitoring()
        except KeyboardInterrupt:
            if verbose:
                print("\n⏹️ Monitoring stopped by user")
    
    def show_stats(self, output_format='text'):
        """Show statistics"""
        try:
            hackathons = self.monitor.excel_manager.get_existing_hackathons()
            total = len(hackathons)
            
            # Count by platform
            platforms = {}
            today_count = 0
            today = datetime.now().date()
            
            for h in hackathons:
                platform = h.get('platform', 'Unknown')
                platforms[platform] = platforms.get(platform, 0) + 1
                
                try:
                    scraped_date = datetime.fromisoformat(h.get('scraped_at', '')).date()
                    if scraped_date == today:
                        today_count += 1
                except:
                    pass
            
            if output_format == 'json':
                result = {
                    'total_hackathons': total,
                    'new_today': today_count,
                    'platforms': platforms,
                    'excel_file': str(Path('hackathons_data.xlsx').absolute()),
                    'timestamp': datetime.now().isoformat()
                }
                print(json.dumps(result, indent=2))
            else:
                print("📊 Hackathon Monitor Statistics")
                print("=" * 35)
                print(f"Total Hackathons: {total}")
                print(f"New Today: {today_count}")
                print(f"Excel File: {Path('hackathons_data.xlsx').absolute()}")
                print()
                print("By Platform:")
                for platform, count in platforms.items():
                    print(f"  {platform}: {count}")
            
            return True
            
        except Exception as e:
            if output_format == 'json':
                result = {'success': False, 'error': str(e)}
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Failed to get statistics: {e}")
            return False
    
    def test_notification(self, message=None):
        """Test notification system"""
        try:
            test_message = message or "CLI notification test successful! 🎉"
            self.notifier.send_notification("Hackathon Monitor Test", test_message)
            print("✅ Test notification sent!")
            return True
        except Exception as e:
            print(f"❌ Notification test failed: {e}")
            return False
    
    def export_data(self, format='csv', output_file=None):
        """Export data in different formats"""
        try:
            hackathons = self.monitor.excel_manager.get_existing_hackathons()
            
            if not hackathons:
                print("❌ No data to export. Run scraping first.")
                return False
            
            if format == 'json':
                output_file = output_file or 'hackathons_export.json'
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(hackathons, f, indent=2, ensure_ascii=False)
            
            elif format == 'csv':
                import csv
                output_file = output_file or 'hackathons_export.csv'
                
                if hackathons:
                    with open(output_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=hackathons[0].keys())
                        writer.writeheader()
                        writer.writerows(hackathons)
            
            elif format == 'txt':
                output_file = output_file or 'hackathons_export.txt'
                with open(output_file, 'w', encoding='utf-8') as f:
                    for i, h in enumerate(hackathons, 1):
                        f.write(f"{i}. {h.get('name', 'Unknown')}\n")
                        f.write(f"   Platform: {h.get('platform', 'Unknown')}\n")
                        f.write(f"   Link: {h.get('link', 'N/A')}\n")
                        f.write(f"   Date: {h.get('start_date', 'N/A')}\n")
                        f.write(f"   Tags: {h.get('tags', 'N/A')}\n")
                        f.write(f"   Scraped: {h.get('scraped_at', 'N/A')}\n")
                        f.write("\n")
            
            print(f"✅ Data exported to: {output_file}")
            print(f"📊 Exported {len(hackathons)} hackathons")
            return True
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return False
    
    def show_config(self):
        """Show current configuration"""
        print("⚙️ Current Configuration")
        print("=" * 25)
        
        for section_name in self.monitor.config.sections():
            print(f"\n[{section_name}]")
            for key, value in self.monitor.config[section_name].items():
                print(f"  {key} = {value}")
    
    def update_config(self, section, key, value):
        """Update configuration"""
        try:
            if not self.monitor.config.has_section(section):
                self.monitor.config.add_section(section)
            
            self.monitor.config.set(section, key, value)
            
            with open('config.ini', 'w') as f:
                self.monitor.config.write(f)
            
            print(f"✅ Updated {section}.{key} = {value}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update config: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(
        description='🎯 Hackathon Monitor - Command Line Interface',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s scrape                          # Run single scraping cycle
  %(prog)s scrape --json                   # Output results as JSON
  %(prog)s monitor --interval 4            # Monitor every 4 hours
  %(prog)s stats                           # Show statistics
  %(prog)s export --format csv             # Export data as CSV
  %(prog)s test-notification               # Test notifications
  %(prog)s config --show                   # Show configuration
  %(prog)s config --set SETTINGS interval 8  # Update config
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Run single scraping cycle')
    scrape_parser.add_argument('--json', action='store_true', help='Output as JSON')
    scrape_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Monitor command
    monitor_parser = subparsers.add_parser('monitor', help='Start continuous monitoring')
    monitor_parser.add_argument('--interval', type=float, help='Monitoring interval in hours')
    monitor_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    stats_parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    # Export command
    export_parser = subparsers.add_parser('export', help='Export data')
    export_parser.add_argument('--format', choices=['json', 'csv', 'txt'], default='csv', help='Export format')
    export_parser.add_argument('--output', help='Output file name')
    
    # Test notification command
    test_parser = subparsers.add_parser('test-notification', help='Test notification system')
    test_parser.add_argument('--message', help='Custom test message')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Configuration management')
    config_group = config_parser.add_mutually_exclusive_group(required=True)
    config_group.add_argument('--show', action='store_true', help='Show current configuration')
    config_group.add_argument('--set', nargs=3, metavar=('SECTION', 'KEY', 'VALUE'), help='Set configuration value')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = CLIHackathonMonitor()
    
    try:
        if args.command == 'scrape':
            output_format = 'json' if args.json else 'text'
            success = cli.scrape_once(verbose=args.verbose, output_format=output_format)
            sys.exit(0 if success else 1)
        
        elif args.command == 'monitor':
            cli.start_monitoring(interval=args.interval, verbose=args.verbose)
        
        elif args.command == 'stats':
            output_format = 'json' if args.json else 'text'
            success = cli.show_stats(output_format=output_format)
            sys.exit(0 if success else 1)
        
        elif args.command == 'export':
            success = cli.export_data(format=args.format, output_file=args.output)
            sys.exit(0 if success else 1)
        
        elif args.command == 'test-notification':
            success = cli.test_notification(message=args.message)
            sys.exit(0 if success else 1)
        
        elif args.command == 'config':
            if args.show:
                cli.show_config()
            elif args.set:
                section, key, value = args.set
                success = cli.update_config(section, key, value)
                sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
