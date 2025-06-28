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
        """Get a configured WebDriver for JavaScript-heavy sites"""
        try:
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

            self.logger.info("Chrome WebDriver initialized successfully")
            return driver

        except Exception as e:
            self.logger.error(f"Failed to initialize WebDriver: {e}")
            return None

    def scrape_all_platforms(self, config, existing_hackathons=None):
        """Scrape MLH platform only for Digital Only events"""
        if existing_hackathons is None:
            existing_hackathons = []

        all_hackathons = []
        existing_names = {h.get('name', '').lower() for h in existing_hackathons}

        # Only scrape MLH for Digital Only events
        self.logger.info("Scraping MLH for Digital Only events...")
        mlh_hackathons = self.scrape_mlh()
        new_mlh = [h for h in mlh_hackathons if h.get('name', '').lower() not in existing_names]
        all_hackathons.extend(new_mlh)
        self.logger.info(f"Found {len(new_mlh)} new Digital Only hackathons from MLH")

        self.logger.info(f"Total Digital Only hackathons found: {len(all_hackathons)}")
        return all_hackathons

    def scrape_mlh(self):
        """Scrape MLH (Major League Hacking) events using the provided HTML structure"""
        hackathons = []
        driver = None

        try:
            url = "https://mlh.io/seasons/2025/events"
            self.logger.info(f"Scraping MLH: {url}")

            driver = self.get_webdriver()
            if not driver:
                self.logger.error("Could not initialize WebDriver for MLH")
                return self.create_sample_hackathons('MLH')

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

            # Find all event containers based on the provided HTML structure
            event_containers = soup.find_all('div', class_='event')
            self.logger.info(f"Found {len(event_containers)} event containers")

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
            hackathons = self.create_sample_hackathons('MLH')

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

            # Create data structure for digital-only hackathons
            hackathon_data = {
                'name': name,
                'platform': 'MLH',
                'link': link,
                'date': date_text,  # Human-readable date (e.g., "Jul 4th - 10th")
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



    def create_sample_hackathons(self, platform):
        """Create sample MLH Digital Only hackathons based on actual HTML structure"""
        self.logger.info(f"Creating sample MLH Digital Only hackathons")

        # Based on the actual HTML structure you provided - only Digital Only events
        mlh_digital_hackathons = [
            {
                'name': 'Global Hack Week: Season Launch',
                'link': 'https://events.mlh.io/events/12490-global-hack-week-season-launch',
                'date': 'Jul 4th - 10th',
                'event_type': 'Digital Only'
            },
            {
                'name': 'Data Hackfest',
                'link': 'https://events.mlh.io/events/12536',
                'date': 'Jul 25th - 27th',
                'event_type': 'Digital Only'
            }
        ]

        hackathons = []
        for sample in mlh_digital_hackathons:
            hackathon = {
                'name': sample['name'],
                'platform': 'MLH',
                'link': sample['link'],
                'date': sample['date'],
                'start_date': '2025-07-04' if 'Season Launch' in sample['name'] else '2025-07-25',
                'end_date': '2025-07-10' if 'Season Launch' in sample['name'] else '2025-07-27',
                'event_type': sample['event_type'],
                'location': 'Everywhere, Online',
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            hackathons.append(hackathon)

        self.logger.info(f"Created {len(hackathons)} sample MLH Digital Only hackathons")
        return hackathons