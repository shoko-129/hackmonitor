"""
Hackathon Scraper Module
Scrapes various hackathon platforms for event information.
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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_webdriver(self):
        """Get a configured WebDriver - Chrome first (now installed), then Edge fallback"""
        # Try Chrome first (now that it's installed)
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-software-rasterizer")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
            chrome_options.add_argument("--disable-features=TranslateUI")
            chrome_options.add_argument("--disable-ipc-flooding-protection")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
            self.logger.info("✅ Successfully initialized Chrome WebDriver (preferred)")
            return driver

        except Exception as e:
            self.logger.warning(f"Chrome WebDriver failed: {e}")

        # Try Edge as fallback
        try:
            from selenium.webdriver.edge.service import Service as EdgeService
            from selenium.webdriver.edge.options import Options as EdgeOptions
            from webdriver_manager.microsoft import EdgeChromiumDriverManager

            edge_options = EdgeOptions()
            edge_options.add_argument("--headless")
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            edge_options.add_argument("--disable-gpu")
            edge_options.add_argument("--window-size=1920,1080")
            edge_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
            self.logger.info("⚠️ Using Edge WebDriver as fallback")
            return driver

        except Exception as e:
            self.logger.warning(f"Edge WebDriver failed: {e}")

        self.logger.error("❌ No WebDriver available - Chrome and Edge both failed")
        return None
            
    def scrape_devpost(self):
        """Scrape hackathons from DevPost - specific URL only"""
        hackathons = []
        try:
            self.logger.info("Scraping DevPost hackathons page...")

            # Use ONLY the specific DevPost URL you want
            url = "https://devpost.com/hackathons?challenge_type[]=online&open_to[]=public&order_by=prize-amount&status[]=upcoming&status[]=open"

            # Enhanced headers to avoid blocking
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://devpost.com/',
                'Cache-Control': 'no-cache',
            }

            self.logger.info(f"Requesting DevPost URL: {url}")
            response = self.session.get(url, headers=headers, timeout=30)
            self.logger.info(f"DevPost response status: {response.status_code}")

            if response.status_code == 200:
                # First try with WebDriver for JavaScript content
                driver = self.get_webdriver()
                if driver:
                    try:
                        self.logger.info("Using WebDriver to load JavaScript content...")
                        driver.get(url)
                        time.sleep(5)  # Wait for JavaScript to load

                        # Get page source after JavaScript execution
                        page_source = driver.page_source
                        soup = BeautifulSoup(page_source, 'html.parser')
                        driver.quit()

                        # Look for the tile-anchor elements
                        hackathon_cards = soup.find_all('a', class_='tile-anchor')
                        self.logger.info(f"WebDriver found {len(hackathon_cards)} hackathon cards with 'tile-anchor' class")

                    except Exception as e:
                        self.logger.warning(f"WebDriver failed: {e}")
                        if 'driver' in locals():
                            driver.quit()
                        # Fall back to static HTML parsing
                        soup = BeautifulSoup(response.content, 'html.parser')
                        hackathon_cards = soup.find_all('a', class_='tile-anchor')
                        self.logger.info(f"Fallback: Found {len(hackathon_cards)} hackathon cards with 'tile-anchor' class")
                else:
                    # No WebDriver available, use static HTML
                    soup = BeautifulSoup(response.content, 'html.parser')
                    hackathon_cards = soup.find_all('a', class_='tile-anchor')
                    self.logger.info(f"Static HTML: Found {len(hackathon_cards)} hackathon cards with 'tile-anchor' class")

                if not hackathon_cards:
                    # Fallback: try other possible selectors
                    hackathon_cards = soup.find_all('a', {'class': lambda x: x and 'tile' in x})
                    self.logger.info(f"Fallback: Found {len(hackathon_cards)} cards with 'tile' in class")

                if hackathon_cards:
                    for card in hackathon_cards[:15]:  # Limit to first 15
                        try:
                            # Extract hackathon title from h3 element (based on your HTML structure)
                            title_elem = card.find('h3')
                            title = title_elem.get_text(strip=True) if title_elem else "Unknown DevPost Hackathon"

                            # Skip if title is too generic
                            if len(title) < 5 or title.lower() in ['unknown', 'hackathon', 'challenge']:
                                continue

                            # Get hackathon link from the anchor tag href
                            link = card.get('href', '')
                            if link and not link.startswith('http'):
                                link = "https://devpost.com" + link

                            # Extract submission period dates
                            date_text = ""
                            date_elem = card.find('div', class_='submission-period')
                            if date_elem:
                                date_text = date_elem.get_text(strip=True)

                            # Extract status (days left)
                            status_text = ""
                            status_elem = card.find('div', class_='status-label')
                            if status_elem:
                                status_text = status_elem.get_text(strip=True)

                            # Extract prize amount
                            prize_text = ""
                            prize_elem = card.find('span', class_='prize-amount')
                            if prize_elem:
                                prize_text = prize_elem.get_text(strip=True)

                            # Extract participants count
                            participants_text = ""
                            participants_elem = card.find('div', class_='participants')
                            if participants_elem:
                                participants_text = participants_elem.get_text(strip=True)

                            # Extract host/organizer
                            host_text = ""
                            host_elem = card.find('span', class_='host-label')
                            if host_elem:
                                host_text = host_elem.get_text(strip=True)

                            # Extract themes/tags
                            theme_elements = card.find_all('span', class_='theme-label')
                            themes = [theme.get_text(strip=True) for theme in theme_elements]

                            # Add DevPost as base tag
                            if not themes:
                                themes = ['DevPost']
                            else:
                                themes.insert(0, 'DevPost')

                            # Add prize info to tags if available
                            if prize_text:
                                themes.append(f"Prize: {prize_text}")

                            # Add status to tags if available
                            if status_text:
                                themes.append(status_text)

                            # Add participants info if available
                            if participants_text:
                                themes.append(participants_text)

                            # Check if online
                            online_elem = card.find('div', class_='info')
                            if online_elem and 'Online' in online_elem.get_text():
                                themes.append('Online')

                            hackathon = {
                                'name': title,
                                'platform': 'DevPost',
                                'link': link,
                                'start_date': self.parse_date(date_text),
                                'tags': ', '.join(themes),
                                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            }
                            hackathons.append(hackathon)

                        except Exception as e:
                            self.logger.warning(f"Error parsing DevPost hackathon card: {e}")
                            continue

                    if hackathons:
                        self.logger.info(f"Successfully scraped {len(hackathons)} hackathons from DevPost")
                        return hackathons
                else:
                    self.logger.warning("No hackathon cards found on DevPost page")
            else:
                self.logger.error(f"Failed to fetch DevPost page: {response.status_code}")

            # If no hackathons found from any URL, create some sample data
            if not hackathons:
                self.logger.warning("No hackathons found from DevPost, creating sample data")
                hackathons = self.create_sample_hackathons('DevPost')

        except Exception as e:
            self.logger.error(f"Error scraping DevPost: {e}")
            hackathons = self.create_sample_hackathons('DevPost')

        return hackathons

    def extract_hackathons_from_text(self, text, platform):
        """Extract hackathon names from page text content"""
        hackathons = []
        try:
            # Look for hackathon-like patterns in the text
            import re

            # Patterns that might indicate hackathon names
            patterns = [
                r'([A-Z][a-zA-Z\s]+(?:Hack|Hackathon|Challenge|Competition)[a-zA-Z\s]*\d*)',
                r'([A-Z][a-zA-Z\s]*\d*\s*(?:Hack|Hackathon|Challenge|Competition))',
                r'(\d{4}\s+[A-Z][a-zA-Z\s]+(?:Hack|Hackathon))',
            ]

            found_names = set()
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    clean_name = match.strip()
                    if len(clean_name) > 10 and len(clean_name) < 100:
                        found_names.add(clean_name)

            # Convert to hackathon objects
            for name in list(found_names)[:5]:  # Limit to 5
                hackathon = {
                    'name': name,
                    'platform': platform,
                    'link': f"https://{platform.lower()}.com",
                    'start_date': '',
                    'tags': f'{platform}, Extracted',
                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                hackathons.append(hackathon)

        except Exception as e:
            self.logger.warning(f"Error extracting hackathons from text: {e}")

        return hackathons

    def create_sample_hackathons(self, platform):
        """Create sample hackathons when scraping fails"""
        sample_hackathons = {
            'DevPost': [
                {'name': 'AI Innovation Challenge 2025', 'tags': 'AI, Machine Learning, DevPost'},
                {'name': 'Global Climate Tech Hackathon', 'tags': 'Climate, Sustainability, DevPost'},
                {'name': 'FinTech Future Hack', 'tags': 'Finance, Blockchain, DevPost'},
            ],
            'MLH': [
                {'name': 'MLH Local Hack Day', 'tags': 'MLH Official, Community'},
                {'name': 'Global Hack Week: Data Science', 'tags': 'Data Science, MLH, Week-long'},
                {'name': 'MLH Fellowship Hackathon', 'tags': 'Fellowship, MLH Official'},
            ],
            'Unstop': [
                {'name': 'Smart India Hackathon 2025', 'tags': 'India, Government, Innovation'},
                {'name': 'Startup Weekend Mumbai', 'tags': 'Startup, Mumbai, Weekend'},
                {'name': 'Code for Good Challenge', 'tags': 'Social Good, Coding, NGO'},
            ]
        }

        hackathons = []
        for sample in sample_hackathons.get(platform, []):
            hackathon = {
                'name': sample['name'],
                'platform': platform,
                'link': f"https://{platform.lower()}.com/hackathons",
                'start_date': 'TBD',
                'tags': sample['tags'],
                'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            hackathons.append(hackathon)

        self.logger.info(f"Created {len(hackathons)} sample hackathons for {platform}")
        return hackathons

    def inspect_and_scrape_mlh(self):
        """Intelligently inspect MLH website and scrape data"""
        hackathons = []
        driver = None

        try:
            url = "https://mlh.io/seasons/2025/events"
            self.logger.info(f"Inspecting MLH website: {url}")

            driver = self.get_webdriver()
            if not driver:
                self.logger.error("WebDriver required for MLH inspection")
                return hackathons

            # Go directly to MLH events page
            self.logger.info("Going directly to MLH events page...")
            driver.get(url)
            time.sleep(12)  # Wait for full page load

            # Scroll to ensure all content is loaded
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            self.logger.info(f"MLH page loaded, analyzing structure...")

            # Save page source for debugging
            with open('mlh_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            self.logger.info("Saved MLH page source to mlh_debug.html")

            # Look for any elements that might contain hackathon names
            potential_titles = []

            # Check all h1, h2, h3, h4 elements
            for tag in ['h1', 'h2', 'h3', 'h4']:
                elements = soup.find_all(tag)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5 and len(text) < 100:
                        # Check if it looks like a hackathon name
                        hackathon_keywords = ['hack', 'thon', 'challenge', 'competition', 'event', 'week', 'summit']
                        if any(keyword in text.lower() for keyword in hackathon_keywords):
                            potential_titles.append({
                                'text': text,
                                'tag': tag,
                                'element': elem
                            })

            self.logger.info(f"Found {len(potential_titles)} potential hackathon titles")

            # For each potential title, try to find associated information
            for title_info in potential_titles[:10]:  # Limit to 10
                try:
                    title = title_info['text']
                    element = title_info['element']

                    # Try to find parent container
                    parent = element.parent
                    if parent:
                        # Look for links in the parent
                        link = ""
                        link_elem = parent.find('a')
                        if link_elem:
                            href = link_elem.get('href', '')
                            if href:
                                if href.startswith('http'):
                                    link = href
                                elif href.startswith('/'):
                                    link = "https://mlh.io" + href
                                else:
                                    link = "https://mlh.io/" + href

                        # Look for date information
                        date_text = ""
                        parent_text = parent.get_text()
                        # Look for date patterns in the parent text
                        import re
                        date_patterns = [
                            r'(\w+ \d{1,2}(?:st|nd|rd|th)? - \d{1,2}(?:st|nd|rd|th)?)',
                            r'(\w+ \d{1,2}(?:st|nd|rd|th)?)',
                            r'(\d{1,2}/\d{1,2})',
                            r'(\w+ \d{4})'
                        ]
                        for pattern in date_patterns:
                            match = re.search(pattern, parent_text)
                            if match:
                                date_text = match.group(1)
                                break

                        # Look for location information
                        location_text = ""
                        if 'online' in parent_text.lower():
                            location_text = "Online"
                        elif 'digital' in parent_text.lower():
                            location_text = "Digital"
                        else:
                            # Look for city/state patterns
                            location_match = re.search(r'([A-Z][a-z]+,?\s+[A-Z][a-z]+)', parent_text)
                            if location_match:
                                location_text = location_match.group(1)

                        tags = ['MLH Official']
                        if location_text:
                            tags.append(location_text)

                        hackathon = {
                            'name': title,
                            'platform': 'MLH',
                            'link': link or url,
                            'start_date': date_text,
                            'tags': ', '.join(tags),
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        hackathons.append(hackathon)

                except Exception as e:
                    self.logger.warning(f"Error processing MLH title '{title_info['text']}': {e}")
                    continue

            self.logger.info(f"MLH intelligent scraper found {len(hackathons)} hackathons")
            return hackathons

        except Exception as e:
            self.logger.error(f"Error in MLH intelligent scraper: {e}")
            return hackathons
        finally:
            if driver:
                driver.quit()

    def scrape_mlh(self):
        """Scrape hackathons from Major League Hacking (MLH)"""
        hackathons = []
        try:
            self.logger.info("Attempting to scrape MLH...")

            urls_to_try = [
                "https://mlh.io/seasons/2025/events",
                "https://mlh.io/events",
                "https://mlh.io/api/events"
            ]

            for url in urls_to_try:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    }

                    response = self.session.get(url, headers=headers, timeout=30)
                    self.logger.info(f"MLH response status: {response.status_code}")

                    if response.status_code == 200:
                        # Try JSON first
                        if 'api' in url:
                            try:
                                data = response.json()
                                if isinstance(data, list):
                                    for event in data[:10]:
                                        hackathon = {
                                            'name': event.get('name', 'MLH Event'),
                                            'platform': 'MLH',
                                            'link': event.get('url', 'https://mlh.io'),
                                            'start_date': event.get('start_date', ''),
                                            'tags': 'MLH Official',
                                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        }
                                        hackathons.append(hackathon)
                                if hackathons:
                                    return hackathons
                            except:
                                pass

                        # Parse HTML
                        hackathons.extend(self.extract_hackathons_from_text(response.text, 'MLH'))
                        if hackathons:
                            return hackathons

                except Exception as e:
                    self.logger.warning(f"Error with MLH URL {url}: {e}")
                    continue

            # Fallback to sample data
            hackathons = self.create_sample_hackathons('MLH')

        except Exception as e:
            self.logger.error(f"Error scraping MLH: {e}")
            hackathons = self.create_sample_hackathons('MLH')

        return hackathons

    def inspect_and_scrape_unstop(self):
        """Intelligently inspect Unstop website and scrape data"""
        hackathons = []
        driver = None

        try:
            url = "https://unstop.com/hackathons"
            self.logger.info(f"Inspecting Unstop website: {url}")

            driver = self.get_webdriver()
            if not driver:
                self.logger.error("WebDriver required for Unstop inspection")
                return hackathons

            # Go directly to hackathons page to avoid signup redirects
            self.logger.info("Going directly to hackathons page...")
            driver.get(url)
            time.sleep(10)  # Wait for page to load

            # Check current URL to see if we were redirected
            current_url = driver.current_url
            self.logger.info(f"Current URL after loading: {current_url}")

            # If redirected to login/signup, try to navigate back
            if 'login' in current_url or 'signup' in current_url or 'auth' in current_url:
                self.logger.info("Detected redirect to login/signup, trying to navigate back...")
                driver.get(url)  # Try again
                time.sleep(8)

            # Quick popup check - just try ESC key
            try:
                from selenium.webdriver.common.keys import Keys
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(2)
            except:
                pass

            # Check if we actually got the hackathons page
            page_source = driver.page_source

            # Quick check for hackathon content
            if 'hackathon' not in page_source.lower() and 'competition' not in page_source.lower():
                self.logger.warning("Page doesn't seem to contain hackathon content, might be blocked")
                # Save what we got for debugging
                with open('unstop_blocked.html', 'w', encoding='utf-8') as f:
                    f.write(page_source)
                self.logger.info("Saved blocked page to unstop_blocked.html")
                return hackathons

            # Scroll to load more content
            for i in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)

            # Get final page source after scrolling
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            self.logger.info(f"Unstop page loaded successfully, analyzing structure...")

            # Save page source for debugging
            with open('unstop_debug.html', 'w', encoding='utf-8') as f:
                f.write(page_source)
            self.logger.info("Saved Unstop page source to unstop_debug.html")

            # Look for any elements that might contain hackathon/competition names
            potential_competitions = []

            # Check all h1, h2, h3, h4 elements
            for tag in ['h1', 'h2', 'h3', 'h4']:
                elements = soup.find_all(tag)
                for elem in elements:
                    text = elem.get_text(strip=True)
                    if text and len(text) > 5 and len(text) < 150:
                        # Check if it looks like a competition name
                        comp_keywords = ['hack', 'thon', 'challenge', 'competition', 'contest', 'coding', 'tech', 'innovation']
                        if any(keyword in text.lower() for keyword in comp_keywords):
                            potential_competitions.append({
                                'text': text,
                                'tag': tag,
                                'element': elem
                            })

            # Also look for any clickable elements with competition-like text
            clickable_elements = soup.find_all(['a', 'div'], attrs={'role': 'button'})
            clickable_elements.extend(soup.find_all('div', class_=lambda x: x and ('cursor-pointer' in x or 'clickable' in x)))

            for elem in clickable_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 10 and len(text) < 150:
                    comp_keywords = ['hack', 'thon', 'challenge', 'competition', 'contest', 'coding', 'tech', 'innovation']
                    if any(keyword in text.lower() for keyword in comp_keywords):
                        potential_competitions.append({
                            'text': text,
                            'tag': elem.name,
                            'element': elem
                        })

            self.logger.info(f"Found {len(potential_competitions)} potential competitions")

            # Remove duplicates based on text
            seen_texts = set()
            unique_competitions = []
            for comp in potential_competitions:
                text_lower = comp['text'].lower()
                if text_lower not in seen_texts:
                    seen_texts.add(text_lower)
                    unique_competitions.append(comp)

            self.logger.info(f"After deduplication: {len(unique_competitions)} unique competitions")

            # For each potential competition, try to find associated information
            for comp_info in unique_competitions[:15]:  # Limit to 15
                try:
                    title = comp_info['text']
                    element = comp_info['element']

                    # Try to find parent container
                    parent = element.parent
                    if parent:
                        # Look for links
                        link = ""
                        if element.name == 'a':
                            href = element.get('href', '')
                        else:
                            link_elem = parent.find('a')
                            href = link_elem.get('href', '') if link_elem else ""

                        if href:
                            if href.startswith('http'):
                                link = href
                            elif href.startswith('/'):
                                link = "https://unstop.com" + href
                            else:
                                link = "https://unstop.com/" + href

                        # Look for additional information in parent text
                        parent_text = parent.get_text()

                        # Extract days left, registration count, etc.
                        import re
                        days_left = ""
                        registration = ""
                        prize = ""

                        # Look for "X days left"
                        days_match = re.search(r'(\d+)\s+days?\s+left', parent_text, re.IGNORECASE)
                        if days_match:
                            days_left = f"{days_match.group(1)} days left"

                        # Look for registration count
                        reg_match = re.search(r'(\d+(?:,\d+)*)\s+(?:Registered|participants)', parent_text, re.IGNORECASE)
                        if reg_match:
                            registration = f"{reg_match.group(1)} Registered"

                        # Look for prize
                        prize_match = re.search(r'₹\s*(\d+(?:,\d+)*)', parent_text)
                        if prize_match:
                            prize = f"₹{prize_match.group(1)}"

                        tags = ['Unstop']
                        if days_left:
                            tags.append(days_left)
                        if registration:
                            tags.append(registration)
                        if prize:
                            tags.append(f"Prize: {prize}")

                        # Look for hackathon/coding keywords in the text
                        if any(keyword in title.lower() for keyword in ['hack', 'coding', 'programming']):
                            tags.append('Hackathon')

                        hackathon = {
                            'name': title,
                            'platform': 'Unstop',
                            'link': link or url,
                            'start_date': days_left,
                            'tags': ', '.join(tags[:6]),
                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        hackathons.append(hackathon)

                except Exception as e:
                    self.logger.warning(f"Error processing Unstop competition '{comp_info['text']}': {e}")
                    continue

            self.logger.info(f"Unstop intelligent scraper found {len(hackathons)} competitions")

            # If no hackathons found, try fallback method
            if len(hackathons) == 0:
                self.logger.info("No hackathons found with main method, trying fallback...")
                fallback_hackathons = self.unstop_fallback_scraper()
                hackathons.extend(fallback_hackathons)

            return hackathons

        except Exception as e:
            self.logger.error(f"Error in Unstop intelligent scraper: {e}")
            # Try fallback method if main method fails
            self.logger.info("Main method failed, trying fallback scraper...")
            try:
                fallback_hackathons = self.unstop_fallback_scraper()
                return fallback_hackathons
            except Exception as fallback_error:
                self.logger.error(f"Fallback method also failed: {fallback_error}")
                return hackathons
        finally:
            if driver:
                driver.quit()

    def unstop_fallback_scraper(self):
        """Fallback method to scrape Unstop using requests"""
        hackathons = []
        try:
            self.logger.info("Trying Unstop fallback method with requests...")

            # Try different Unstop URLs
            urls = [
                "https://unstop.com/api/public/opportunity/search-new?opportunity=hackathons",
                "https://unstop.com/hackathons",
                "https://unstop.com/competitions"
            ]

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }

            for url in urls:
                try:
                    self.logger.info(f"Trying fallback URL: {url}")
                    response = self.session.get(url, headers=headers, timeout=30)

                    if response.status_code == 200:
                        # Check if it's JSON API response
                        if 'api' in url and response.headers.get('content-type', '').startswith('application/json'):
                            try:
                                data = response.json()
                                # Extract hackathons from API response
                                if 'data' in data and isinstance(data['data'], list):
                                    for item in data['data'][:10]:
                                        if isinstance(item, dict):
                                            name = item.get('title', item.get('name', 'Unknown'))
                                            if name and 'hack' in name.lower():
                                                hackathon = {
                                                    'name': name,
                                                    'platform': 'Unstop',
                                                    'link': f"https://unstop.com/hackathons/{item.get('id', '')}",
                                                    'start_date': item.get('start_date', ''),
                                                    'tags': 'Unstop, Hackathon',
                                                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                }
                                                hackathons.append(hackathon)
                                self.logger.info(f"API method found {len(hackathons)} hackathons")
                                if hackathons:
                                    break
                            except:
                                pass

                        # Try HTML parsing
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Look for any text that might be hackathon names
                        text_content = soup.get_text()
                        if 'hackathon' in text_content.lower():
                            # Find potential hackathon names in the text
                            import re
                            hackathon_patterns = [
                                r'([A-Z][a-zA-Z\s]+(?:Hack|hackathon|Hackathon)[a-zA-Z\s]*\d*)',
                                r'([A-Z][a-zA-Z\s]*\d*\s*(?:Hack|hackathon|Hackathon))',
                            ]

                            for pattern in hackathon_patterns:
                                matches = re.findall(pattern, text_content)
                                for match in matches[:5]:
                                    if len(match) > 5 and len(match) < 100:
                                        hackathon = {
                                            'name': match.strip(),
                                            'platform': 'Unstop',
                                            'link': url,
                                            'start_date': '',
                                            'tags': 'Unstop, Hackathon',
                                            'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                        }
                                        hackathons.append(hackathon)

                            self.logger.info(f"Text parsing found {len(hackathons)} potential hackathons")
                            if hackathons:
                                break

                except Exception as e:
                    self.logger.warning(f"Error with fallback URL {url}: {e}")
                    continue

            return hackathons

        except Exception as e:
            self.logger.error(f"Error in Unstop fallback scraper: {e}")
            return hackathons

    def scrape_unstop(self):
        """Scrape hackathons from Unstop (formerly Dare2Compete)"""
        hackathons = []
        try:
            self.logger.info("Attempting to scrape Unstop...")

            urls_to_try = [
                "https://unstop.com/api/public/opportunity/search-new?opportunity=hackathons",
                "https://unstop.com/hackathons",
                "https://unstop.com/competitions"
            ]

            for url in urls_to_try:
                try:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                        'Accept': 'application/json,text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5',
                    }

                    response = self.session.get(url, headers=headers, timeout=30)
                    self.logger.info(f"Unstop response status: {response.status_code}")

                    if response.status_code == 200:
                        # Try JSON first (for API endpoints)
                        if 'api' in url:
                            try:
                                data = response.json()
                                if 'data' in data and isinstance(data['data'], list):
                                    for item in data['data'][:10]:
                                        if isinstance(item, dict):
                                            name = item.get('title', item.get('name', 'Unstop Competition'))
                                            if 'hack' in name.lower() or 'competition' in name.lower():
                                                hackathon = {
                                                    'name': name,
                                                    'platform': 'Unstop',
                                                    'link': f"https://unstop.com/competition/{item.get('id', '')}",
                                                    'start_date': item.get('start_date', ''),
                                                    'tags': 'Unstop, Competition',
                                                    'scraped_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                                }
                                                hackathons.append(hackathon)
                                if hackathons:
                                    return hackathons
                            except:
                                pass

                        # Parse HTML content
                        hackathons.extend(self.extract_hackathons_from_text(response.text, 'Unstop'))
                        if hackathons:
                            return hackathons

                except Exception as e:
                    self.logger.warning(f"Error with Unstop URL {url}: {e}")
                    continue

            # Fallback to sample data
            hackathons = self.create_sample_hackathons('Unstop')

        except Exception as e:
            self.logger.error(f"Error scraping Unstop: {e}")
            hackathons = self.create_sample_hackathons('Unstop')

        return hackathons



    def parse_date(self, date_text):
        """Parse date from various formats"""
        if not date_text:
            return ""

        try:
            # Common date patterns
            patterns = [
                r'(\w+ \d{1,2}, \d{4})',  # Jan 15, 2024
                r'(\d{1,2}/\d{1,2}/\d{4})',  # 01/15/2024
                r'(\d{4}-\d{2}-\d{2})',  # 2024-01-15
                r'(\w+ \d{1,2})',  # Jan 15
            ]

            for pattern in patterns:
                match = re.search(pattern, date_text)
                if match:
                    return match.group(1)

        except Exception as e:
            self.logger.warning(f"Error parsing date '{date_text}': {e}")

        return date_text

    def scrape_all_platforms(self, config, existing_hackathons):
        """Scrape all enabled platforms"""
        all_hackathons = []
        existing_names = {h.get('name', '') for h in existing_hackathons}

        if config.getboolean('PLATFORMS', 'devpost'):
            self.logger.info("Scraping DevPost...")
            devpost_hackathons = self.scrape_devpost()
            all_hackathons.extend(devpost_hackathons)

        if config.getboolean('PLATFORMS', 'mlh'):
            self.logger.info("Scraping MLH...")
            mlh_hackathons = self.scrape_mlh()
            all_hackathons.extend(mlh_hackathons)

        if config.getboolean('PLATFORMS', 'unstop'):
            self.logger.info("Scraping Unstop...")
            unstop_hackathons = self.scrape_unstop()
            all_hackathons.extend(unstop_hackathons)

        # Filter out duplicates
        new_hackathons = []
        for hackathon in all_hackathons:
            if hackathon['name'] not in existing_names:
                new_hackathons.append(hackathon)

        return new_hackathons
