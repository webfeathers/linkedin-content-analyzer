import os
import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import re

class LinkedInScraper:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.driver = None
        self.setup_driver()
        # Common advertisement indicators
        self.ad_indicators = [
            "sponsored", "advertisement", "promoted", "download now", "get the full report",
            "sign up", "register now", "limited time", "special offer", "free trial",
            "contact us", "book a demo", "schedule a call", "learn more", "click here",
            "check out", "try now", "get started", "join us", "subscribe",
            "our product", "our service", "our solution", "our platform", "our tool",
            "we help", "we provide", "we offer", "we deliver", "we create",
            "gofund.me", "bit.ly", "hubs.la", "lnkd.in", "t.co"
        ]

    def setup_driver(self):
        """Set up the Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-notifications")
        # Uncomment the line below if you want to run in headless mode
        # chrome_options.add_argument("--headless")
        
        # Use system ChromeDriver
        service = Service('/opt/homebrew/bin/chromedriver')
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def login(self):
        """Log in to LinkedIn."""
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(5)  # Increased wait time for page load

            # Enter email
            email_field = self.driver.find_element(By.ID, "username")
            email_field.send_keys(self.email)
            time.sleep(1)

            # Enter password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(self.password)
            time.sleep(1)

            # Click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
            login_button.click()

            # Wait for feed to load with increased timeout
            try:
                WebDriverWait(self.driver, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2"))
                )
                return True
            except Exception as e:
                print("\nLinkedIn may be asking for security verification.")
                print("Please complete any security challenges in the browser window.")
                print("The script will continue once you've completed the verification.")
                
                # Wait for manual intervention
                input("Press Enter after completing the security verification...")
                
                # Check if we're now on the feed
                try:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "feed-shared-update-v2"))
                    )
                    return True
                except:
                    return False
                    
        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False

    def scroll_feed(self, scroll_count=5):
        """Scroll through the feed to load more posts."""
        for _ in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for content to load

    def extract_post_data(self, post_element):
        """Extract relevant data from a post element."""
        try:
            soup = BeautifulSoup(post_element.get_attribute('outerHTML'), 'html.parser')
            
            # Extract post text
            post_text = soup.find('div', {'class': 'feed-shared-update-v2__description'})
            post_text = post_text.get_text().strip() if post_text else ""

            # Extract engagement metrics
            engagement = {
                'likes': 0,
                'comments': 0,
                'shares': 0
            }
            
            engagement_elements = soup.find_all('span', {'class': 'social-details-social-counts__reactions-count'})
            if engagement_elements:
                # Remove commas and convert to integer
                likes_text = engagement_elements[0].get_text().strip() or "0"
                engagement['likes'] = int(likes_text.replace(',', ''))

            return {
                'text': post_text,
                'engagement': engagement,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    def is_advertisement(self, text):
        """Check if a post is likely an advertisement."""
        if not text:
            return True
            
        text_lower = text.lower()
        
        # Check for common ad indicators
        for indicator in self.ad_indicators:
            if indicator in text_lower:
                return True
                
        # Check for promotional language patterns
        promotional_patterns = [
            r'\b(?:download|get|sign up|register|book|schedule|try|join|subscribe)\b.*\b(?:now|today|free|demo|call)\b',
            r'\b(?:our|we|us)\b.*\b(?:product|service|solution|platform|tool|help|provide|offer|deliver|create)\b',
            r'\b(?:limited time|special offer|free trial|exclusive|discount|deal)\b',
            r'\b(?:click|check|learn|find|discover)\b.*\b(?:more|out|here|now)\b'
        ]
        
        for pattern in promotional_patterns:
            if re.search(pattern, text_lower):
                return True
                
        return False

    def scrape_feed(self, num_posts=200):
        """Scrape posts from the LinkedIn feed."""
        if not self.login():
            return []

        posts_data = []
        organic_posts = 0
        scroll_count = 0
        
        # Keep scrolling until we have enough organic posts or reach max attempts
        while organic_posts < num_posts and scroll_count < 30:  # Max 30 scrolls
            self.scroll_feed(scroll_count=1)
            scroll_count += 1
            
            # Find all posts
            post_elements = self.driver.find_elements(By.CLASS_NAME, "feed-shared-update-v2")
            
            for post in post_elements:
                if organic_posts >= num_posts:
                    break
                    
                post_data = self.extract_post_data(post)
                if post_data and not self.is_advertisement(post_data['text']):
                    posts_data.append(post_data)
                    organic_posts += 1
                time.sleep(0.5)  # Small delay between posts

        return posts_data

    def save_data(self, data, filename=None):
        """Save scraped data to a JSON file."""
        if filename is None:
            filename = f"data/raw/linkedin_feed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def close(self):
        """Close the browser."""
        if self.driver:
            self.driver.quit()

def main():
    scraper = LinkedInScraper()
    try:
        print("Starting LinkedIn feed scraping...")
        posts_data = scraper.scrape_feed(num_posts=200)
        scraper.save_data(posts_data)
        print(f"Successfully scraped {len(posts_data)} posts")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        scraper.close()

if __name__ == "__main__":
    main() 