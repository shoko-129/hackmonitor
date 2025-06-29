"""
Hackathon Scraper Module
Scrapes various hackathon platforms for event information.
Updated to properly parse MLH website structure.
"""

import requests
import logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re

class HackathonScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def get_webdriver(self):
        """Get a configured Chrome WebDriver"""
        try:
            self.logger.info("🔍 Initializing Chrome WebDriver...")

            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")

            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )

            # Execute script to remove webdriver property
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            self.logger.info("✅ Chrome WebDriver initialized successfully")
            return driver

        except Exception as e:
            self.logger.error(f"❌ Chrome WebDriver initialization failed: {e}")
            self.logger.error("❌ Chrome browser is not installed or not accessible")
            self.logger.error("📥 Please install Google Chrome browser to enable web scraping")
            self.logger.error("🔗 Download from: https://www.google.com/chrome/")
            raise Exception("Chrome browser not installed. Please install Google Chrome to use web scraping features.")



    def check_chrome_availability(self):
        """Check if Chrome is available for web scraping"""
        try:
            self.get_webdriver()
            return True
        except Exception as e:
            self.logger.error("❌ Chrome browser is not installed or accessible")
            self.logger.error("📥 Please install Google Chrome to enable web scraping")
            self.logger.error("🔗 Download from: https://www.google.com/chrome/")
            return False

    def scrape_all_platforms(self, config, existing_hackathons=None):
        """Scrape MLH and Devpost platforms for upcoming hackathons"""
        if existing_hackathons is None:
            existing_hackathons = []

        # Check Chrome availability first
        if not self.check_chrome_availability():
            self.logger.error("❌ Cannot perform web scraping without Chrome browser")
            self.logger.error("📋 Returning empty results - please install Chrome to get hackathon data")
            return []

        all_hackathons = []
        existing_names = {h.get('name', '').lower() for h in existing_hackathons}

        # Scrape MLH for Digital Only events
        self.logger.info("Scraping MLH for Digital Only events...")
        mlh_hackathons = self.scrape_mlh()
        new_mlh = [h for h in mlh_hackathons if h.get('name', '').lower() not in existing_names]
        all_hackathons.extend(new_mlh)
        self.logger.info(f"Found {len(new_mlh)} new Digital Only hackathons from MLH")

        # Scrape Devpost for upcoming online hackathons
        self.logger.info("Scraping Devpost for upcoming online hackathons...")
        devpost_hackathons = self.scrape_devpost()
        new_devpost = [h for h in devpost_hackathons if h.get('name', '').lower() not in existing_names]
        all_hackathons.extend(new_devpost)
        self.logger.info(f"Found {len(new_devpost)} new upcoming hackathons from Devpost")

        # Scrape Unstop for upcoming unpaid hackathons
        self.logger.info("Scraping Unstop for upcoming unpaid hackathons...")
        unstop_hackathons = self.scrape_unstop()
        new_unstop = [h for h in unstop_hackathons if h.get('name', '').lower() not in existing_names]
        all_hackathons.extend(new_unstop)
        self.logger.info(f"Found {len(new_unstop)} new upcoming hackathons from Unstop")

        self.logger.info(f"Total upcoming hackathons found: {len(all_hackathons)}")
        return all_hackathons

    def scrape_mlh(self):
        """Scrape MLH (Major League Hacking) events using the provided HTML structure"""
        hackathons = []
        driver = None

        try:
            url = "https://mlh.io/seasons/2025/events"
            self.logger.info(f"Scraping MLH: {url}")

            try:
                driver = self.get_webdriver()
            except Exception as e:
                self.logger.error("❌ Cannot scrape MLH: Chrome browser not installed")
                return []

            driver.get(url)
            time.sleep(5)  # Wait for page to load

            # Wait for events to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "event"))
                )
            except:
                self.logger.warning("Events not found, page might not have loaded properly")

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the "Upcoming Events" section only
            upcoming_section = None
            all_rows = soup.find_all('div', class_='row')

            for row in all_rows:
                h3_element = row.find('h3', class_='text-center')
                if h3_element and 'Upcoming Events' in h3_element.get_text():
                    upcoming_section = row
                    break

            if upcoming_section:
                # Find event containers only in the upcoming section
                event_containers = upcoming_section.find_all('div', class_='event')
                self.logger.info(f"Found {len(event_containers)} upcoming event containers")
            else:
                # Fallback: look for all events but filter by date later
                event_containers = soup.find_all('div', class_='event')
                self.logger.warning(f"Could not find 'Upcoming Events' section, found {len(event_containers)} total events")

            for event_container in event_containers:
                try:
                    hackathon_data = self.parse_mlh_event(event_container)
                    if hackathon_data:
                        hackathons.append(hackathon_data)
                        self.logger.debug(f"Parsed hackathon: {hackathon_data['name']}")
                except Exception as e:
                    self.logger.warning(f"Error parsing MLH event: {e}")
                    continue

            self.logger.info(f"Successfully scraped {len(hackathons)} hackathons from MLH")

        except Exception as e:
            self.logger.error(f"Error scraping MLH: {e}")
            if "Chrome browser not installed" in str(e):
                hackathons = []
            else:
                hackathons = []

        finally:
            if driver:
                driver.quit()

        return hackathons

    def parse_mlh_event(self, event_container):
        """Parse individual MLH event from the actual HTML structure"""
        try:
            # Extract event name from h3.event-name
            name_element = event_container.find('h3', class_='event-name')
            name = name_element.get_text(strip=True) if name_element else "Unknown Event"

            # Extract event link from a.event-link href
            link_element = event_container.find('a', class_='event-link')
            raw_link = link_element.get('href', '') if link_element else ''

            # Clean the link - remove query parameters to get clean MLH event URL
            if raw_link:
                # Remove query parameters (everything after ?)
                clean_link = raw_link.split('?')[0]
                link = clean_link
            else:
                link = ''

            # Extract event date from p.event-date
            date_element = event_container.find('p', class_='event-date')
            date_text = date_element.get_text(strip=True) if date_element else ''

            # Extract event type from div.event-hybrid-notes span
            hybrid_notes_div = event_container.find('div', class_='event-hybrid-notes')
            if hybrid_notes_div:
                span_element = hybrid_notes_div.find('span')
                event_type = span_element.get_text(strip=True) if span_element else 'Type TBD'
            else:
                event_type = 'Type TBD'

            # FILTER: Only include "Digital Only" events
            if 'Digital Only' not in event_type:
                self.logger.debug(f"Skipping non-digital event: {name} ({event_type})")
                return None

            # Parse start and end dates from meta tags for additional data
            start_date_meta = event_container.find('meta', {'itemprop': 'startDate'})
            end_date_meta = event_container.find('meta', {'itemprop': 'endDate'})

            start_date = start_date_meta.get('content', '') if start_date_meta else ''
            end_date = end_date_meta.get('content', '') if end_date_meta else ''

            # FILTER: Only include upcoming events (not past events)
            if start_date:
                try:
                    from datetime import datetime
                    event_start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    current_time = datetime.now(event_start.tzinfo) if event_start.tzinfo else datetime.now()

                    if event_start < current_time:
                        self.logger.debug(f"Skipping past event: {name} (started {start_date})")
                        return None
                except Exception as e:
                    self.logger.warning(f"Could not parse date for {name}: {e}")
                    # If we can't parse the date, include it to be safe

            # Extract location for reference
            location_elements = event_container.find('div', class_='event-location')
            location_parts = []
            if location_elements:
                city_element = location_elements.find('span', {'itemprop': 'city'})
                state_element = location_elements.find('span', {'itemprop': 'state'})

                if city_element:
                    location_parts.append(city_element.get_text(strip=True))
                if state_element:
                    location_parts.append(state_element.get_text(strip=True))

            location = ', '.join(location_parts) if location_parts else 'Online'

            # Calculate days left for MLH events
            days_left = ''
            if start_date:
                try:
                    event_start = datetime.fromisoformat(start_date)
                    current_time = datetime.now()
                    days_diff = (event_start.date() - current_time.date()).days
                    if days_diff > 0:
                        days_left = f"{days_diff} days left"
                    elif days_diff == 0:
                        days_left = "Today"
                    else:
                        days_left = "Started"
                except:
                    days_left = "Date TBD"

            # Create data structure for digital-only hackathons
            hackathon_data = {
                'name': name,
                'platform': 'MLH',
                'link': link,
                'date': date_text,  # Human-readable date (e.g., "Jul 4th - 10th")
                'days_left': days_left,  # Calculated days left
                'start_date': start_date,  # ISO format for sorting
                'end_date': end_date,
                'event_type': event_type,  # "Digital Only"
                'location': location,
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            self.logger.info(f"Found digital hackathon: {name} - {date_text} - {link}")
            return hackathon_data

        except Exception as e:
            self.logger.error(f"Error parsing MLH event: {e}")
            return None

    def scrape_devpost(self):
        """Scrape Devpost for upcoming online hackathons"""
        hackathons = []
        driver = None

        try:
            url = "https://devpost.com/hackathons?challenge_type[]=online&open_to[]=public&order_by=prize-amount&status[]=upcoming&status[]=open"
            self.logger.info(f"Scraping Devpost: {url}")

            try:
                driver = self.get_webdriver()
            except Exception as e:
                self.logger.error("❌ Cannot scrape Devpost: Chrome browser not installed")
                return []

            driver.get(url)
            time.sleep(5)  # Wait for page to load

            # Wait for hackathon tiles to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "hackathon-tile"))
                )
            except:
                self.logger.warning("Hackathon tiles not found, page might not have loaded properly")

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all hackathon tiles
            hackathon_tiles = soup.find_all('div', class_='hackathon-tile')
            self.logger.info(f"Found {len(hackathon_tiles)} hackathon tiles")

            for tile in hackathon_tiles:
                try:
                    hackathon_data = self.parse_devpost_hackathon(tile)
                    if hackathon_data:
                        hackathons.append(hackathon_data)
                        self.logger.debug(f"Parsed Devpost hackathon: {hackathon_data['name']}")
                except Exception as e:
                    self.logger.warning(f"Error parsing Devpost hackathon: {e}")
                    continue

            self.logger.info(f"Successfully scraped {len(hackathons)} hackathons from Devpost")

        except Exception as e:
            self.logger.error(f"Error scraping Devpost: {e}")
            return []

        finally:
            if driver:
                driver.quit()

        return hackathons

    def parse_devpost_hackathon(self, tile):
        """Parse individual Devpost hackathon tile"""
        try:
            # Extract hackathon name from h3
            name_element = tile.find('h3')
            name = name_element.get_text(strip=True) if name_element else 'Unknown Hackathon'

            # Extract link from tile-anchor - get the href attribute
            link_element = tile.find('a', class_='tile-anchor')
            link = ''
            if link_element:
                href = link_element.get('href', '')
                if href:
                    # The href already contains the full URL
                    link = href
                    self.logger.debug(f"Found link: {link}")

            # Extract days left from status-label
            status_element = tile.find('div', class_='status-label')
            days_left = status_element.get_text(strip=True) if status_element else 'Unknown'

            # Extract actual submission dates from submission-period
            submission_period = ''
            submission_element = tile.find('div', class_='submission-period')
            if submission_element:
                submission_period = submission_element.get_text(strip=True)
                self.logger.debug(f"Found submission period: {submission_period}")

            # Use submission period as the main date, fallback to days left
            date_info = submission_period if submission_period else days_left

            # Extract tags from theme-label spans with better cleaning
            tags = []
            theme_labels = tile.find_all('span', class_='theme-label')
            for label in theme_labels:
                # Get all text and clean it properly
                tag_text = label.get_text(strip=True)
                # Remove common icon text patterns
                tag_text = re.sub(r'^\s*(far|fas|fa-\w+)\s+', '', tag_text)  # Remove FontAwesome classes
                tag_text = re.sub(r'^\s*check[^a-zA-Z]*', '', tag_text, flags=re.IGNORECASE)  # Remove "check" text
                tag_text = re.sub(r'^\s*\w{1,2}\s+', '', tag_text)  # Remove short icon text

                # Clean up and validate
                tag_text = tag_text.strip()
                if tag_text and len(tag_text) > 2 and not tag_text.isdigit():
                    tags.append(tag_text)

            # Extract prize amount if available
            prize_element = tile.find('span', class_='prize-amount')
            prize = ''
            if prize_element:
                prize_text = prize_element.get_text(strip=True)
                prize = f"${prize_text} in prizes"

            # Extract location (should be "Online" for our filter)
            location_element = tile.find('div', class_='info')
            location = 'Online'
            if location_element:
                location_span = location_element.find('span')
                if location_span:
                    location = location_span.get_text(strip=True)

            # Only include online hackathons
            if 'online' not in location.lower():
                self.logger.debug(f"Skipping non-online hackathon: {name} ({location})")
                return None

            # Create hackathon data structure
            hackathon_data = {
                'name': name,
                'platform': 'Devpost',
                'link': link,
                'date': date_info,  # Submission period or days left
                'days_left': days_left,
                'submission_period': submission_period,
                'tags': ', '.join(tags) if tags else 'No tags',
                'prize': prize,
                'location': location,
                'event_type': 'Online',
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            self.logger.info(f"Found online hackathon: {name} - {days_left} - {link}")
            return hackathon_data

        except Exception as e:
            self.logger.error(f"Error parsing Devpost hackathon: {e}")
            return None



    def scrape_unstop(self):
        """Scrape Unstop for upcoming unpaid hackathons"""
        hackathons = []
        driver = None

        try:
            url = "https://unstop.com/hackathons?payment=unpaid&oppstatus=open"
            self.logger.info(f"Scraping Unstop: {url}")

            try:
                driver = self.get_webdriver()
            except Exception as e:
                self.logger.error("❌ Cannot scrape Unstop: Chrome browser not installed")
                return []

            driver.get(url)
            time.sleep(5)  # Wait for page to load

            # Wait for hackathon listings to load
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "app-competition-listing"))
                )
            except:
                self.logger.warning("Unstop listings not found, page might not have loaded properly")

            # Get page source and parse with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find all hackathon listings
            hackathon_listings = soup.find_all('app-competition-listing')
            self.logger.info(f"Found {len(hackathon_listings)} Unstop hackathon listings")

            for listing in hackathon_listings:
                try:
                    hackathon_data = self.parse_unstop_hackathon(listing)
                    if hackathon_data:
                        hackathons.append(hackathon_data)
                        self.logger.debug(f"Parsed Unstop hackathon: {hackathon_data['name']}")
                except Exception as e:
                    self.logger.warning(f"Error parsing Unstop hackathon: {e}")
                    continue

            self.logger.info(f"Successfully scraped {len(hackathons)} hackathons from Unstop")

        except Exception as e:
            self.logger.error(f"Error scraping Unstop: {e}")
            return []

        finally:
            if driver:
                driver.quit()

        return hackathons

    def parse_unstop_hackathon(self, listing):
        """Parse individual Unstop hackathon listing"""
        try:
            # Extract hackathon name from h2.double-wrap
            name_element = listing.find('h2', class_='double-wrap')
            name = name_element.get_text(strip=True) if name_element else 'Unknown Hackathon'

            # Extract link from the clickable div with id
            link = ''
            clickable_div = listing.find('div', class_='cursor-pointer')
            if clickable_div:
                # Extract the ID to construct the link
                div_id = clickable_div.get('id', '')
                if div_id:
                    # Extract the opportunity ID from the div id (e.g., "i_1506226_1" -> "1506226")
                    import re
                    match = re.search(r'i_(\d+)_', div_id)
                    if match:
                        opp_id = match.group(1)
                        link = f"https://unstop.com/hackathons/{opp_id}"
                        self.logger.debug(f"Constructed Unstop link: {link}")

            # Extract prize amount from the prize section
            prize = ''
            prize_element = listing.find('div', class_='seperate_box align-center prize')
            if prize_element:
                # Get the text and clean it up
                prize_text = prize_element.get_text(strip=True)
                # Remove emoji and format nicely
                prize_text = re.sub(r'🏆', '', prize_text).strip()
                # Clean up rupee symbol formatting
                prize_text = re.sub(r'₹', '', prize_text).strip()
                if prize_text and prize_text != '':
                    prize = f"₹{prize_text}"

            # Extract days left from sections with schedule icon
            days_left = ''
            # Look for sections containing schedule icon and "days left"
            all_sections = listing.find_all('div', class_='seperate_box align-center')
            for section in all_sections:
                # Check if this section has a schedule icon
                schedule_icon = section.find('img', {'alt': 'schedule'}) or section.find('un-icon')
                if schedule_icon:
                    section_text = section.get_text(strip=True)
                    # Look for various time patterns
                    if any(pattern in section_text.lower() for pattern in ['days left', 'day left', 'hours left', 'hour left']):
                        # Clean up extra whitespace
                        days_left = re.sub(r'\s+', ' ', section_text.strip())
                        self.logger.debug(f"Found days left: {days_left}")
                        break
                    # Also check for numeric patterns followed by time units
                    import re
                    time_pattern = re.search(r'(\d+)\s*(days?|hours?|minutes?|weeks?|months?)\s*(left|remaining)', section_text.lower())
                    if time_pattern:
                        # Clean up extra whitespace
                        days_left = re.sub(r'\s+', ' ', section_text.strip())
                        self.logger.debug(f"Found time pattern: {days_left}")
                        break

            # If no days left found in sections, try a broader search
            if not days_left:
                # Look for any text containing "days left" pattern
                all_text = listing.get_text()
                time_matches = re.findall(r'\d+\s*days?\s*left', all_text, re.IGNORECASE)
                if time_matches:
                    # Clean up the first match
                    days_left = re.sub(r'\s+', ' ', time_matches[0].strip())
                    self.logger.debug(f"Found days left in broader search: {days_left}")

            # Create hackathon data structure
            hackathon_data = {
                'name': name,
                'platform': 'Unstop',
                'link': link,
                'date': days_left,  # "X days left" format
                'days_left': days_left,
                'prize': prize,
                'location': 'Online',
                'event_type': 'Hackathon',
                'tags': 'Hackathon',  # Basic tag
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            self.logger.info(f"Found Unstop hackathon: {name} - {days_left} - {prize}")
            return hackathon_data

        except Exception as e:
            self.logger.error(f"Error parsing Unstop hackathon: {e}")
            return None



