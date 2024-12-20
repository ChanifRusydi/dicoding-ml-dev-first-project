import numpy as np
import pandas as pd
import logging
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException
)
from bs4 import BeautifulSoup
import time
import json
from datetime import datetime
import csv
import os

logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s: %(message)s',
        handlers=[
            logging.FileHandler('tokopedia_scraper.log'),
            logging.StreamHandler()
        ]
    )
logger = logging.getLogger(__name__)

def write_to_csv(data):
    filename = 'tokopedia_reviews.csv'
    fieldNames = ['index','reviews']
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        if not os.path.isfile(filename) or os.stat(filename).st_size == 0:
            writer = csv.DictWriter(f, fieldnames=fieldNames)
            writer.writeheader()
        else:
            writer = csv.writer(f)
            writer.writerow(data)

def write_to_json(data):
    with open('tokopedia_reviews.json', 'a', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def setup_driver():
    # firefox_driver_path = "./geckodriver"
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--windows-size=1920x1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
    #  User agent rotation
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
    ]
    options.add_argument(f'user-agent={np.random.choice(user_agents)}')
    
    # Optional: Run headless if needed
    # options.add_argument('--headless')
    try:
        driver = webdriver.Firefox(options=options)
        
        # Additional driver configurations
        driver.implicitly_wait(10)
        return driver

    except Exception as e:
        logger.error(f"Driver setup failed: {e}")
        raise
    

def fetch_reviews(counter_start: int = 0, url: str = None, max_reviews : int = 300) -> None:
    """
    Scrape reviews from Tokopedia product page
    
    Args:
        counter_start (int): Start index, used for resuming scraping
        url (str): Tokopedia product review URL
    """
    driver = None
    reviews = {}
    data_counter = counter_start
    try:
        driver = setup_driver()
        driver.get(url)
        # Wait for review containers to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'article.css-ccpe8t'))
        )
        
        while len(reviews) < max_reviews:
            # Parse current page
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            # Find review containers
            containers = soup.find_all('article', attrs={'class': 'css-ccpe8t'})
            
            for container in containers:
                review_elem = container.find('span', attrs={'data-testid': 'lblItemUlasan'})
                
                if review_elem and review_elem.text:
                    # Add review with unique key
                    print(review_elem.text.strip())
                    reviews[data_counter] = review_elem.text.strip()
                    print("Review at", data_counter,":", reviews[data_counter])
                    write_to_csv(data=[data_counter, review_elem.text])
                    write_to_json(data={data_counter: review_elem.text.strip()})
                    data_counter += 1
                    logger.info(f"Collected review {len(reviews)}: {review_elem.text[:50]}...")
                
                # Break if max reviews reached
                if len(reviews) >= max_reviews:
                    break
            
            # Try to click next page button
            try:
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Laman berikutnya"]'))
                )
                next_button.click()
                
                # Random delay between page loads
                time.sleep(np.random.uniform(1, 3))
            
            except (TimeoutException, NoSuchElementException):
                logger.warning("No more pages or next button not found")
                break
    
    except Exception as e:
        logger.error(f"Review scraping failed: {e}")
    
    finally:
        if driver:
            driver.quit()

def soup_page(html):
    soup = BeautifulSoup(html, 'html.parser')
    return soup


if __name__ == '__main__':    
    # URL = 'https://www.tokopedia.com/doss/review'
    # URL = "https://www.tokopedia.com/copperindonesia/review"
    URL = "https://www.tokopedia.com/tw-tech/review"
    max_reviews = 3000

    reviews = {}
    df = pd.read_csv('tokopedia_reviews.csv')
    if len(df) > 0:
        last_index = df['index'].iloc[-1]
        print('Start from', last_index+1)
        last_index = int(last_index)
        fetch_reviews(counter_start=last_index+1, url=URL, max_reviews=max_reviews)
    else:
        print('Start from 0')
        fetch_reviews(url=URL, max_reviews=max_reviews)
    fetch_reviews(url=URL, max_reviews=max_reviews)

    # while data_counter < 3000:
    #     result = soup_page(html_page)    
    #     containers = result.find_all('article', attrs={'class': 'css-ccpe8t'})
    #     print(len(containers))
    #     for container in containers:
    #         review = container.find('span', attrs={'data-testid': 'lblItemUlasan'})
    #         if review is not None:
    #             data[data_counter] = review.text
    #             data_counter += 1
    #             print(review.text)
    #         else:
    #             print('No review found')
    #     time.sleep(np.random.uniform(1, 2))
    #     driver.find_element(By.CSS_SELECTOR, 'button[aria-label]="Laman berikutnya').click()
    # # print(container)



# class TokopediaReviewScraper:
#     def __init__(self, max_reviews: int = 3000, log_level: int = logging.INFO):
#         """
#         Initialize Tokopedia Review Scraper
        
#         Args:
#             max_reviews (int): Maximum number of reviews to collect
#             log_level (int): Logging level
#         """
#         # Configure logging
#         logging.basicConfig(
#             level=log_level,
#             format='%(asctime)s - %(levelname)s: %(message)s',
#             handlers=[
#                 logging.FileHandler('tokopedia_scraper.log'),
#                 logging.StreamHandler()
#             ]
#         )
#         self.logger = logging.getLogger(__name__)
        
#         # Scraper configuration
#         self.max_reviews = max_reviews
#         self.reviews = {}

#     def setup_driver(self) -> webdriver.Firefox:
#         """
#         Configure and return Firefox WebDriver
        
#         Returns:
#             webdriver.Firefox: Configured Firefox WebDriver
#         """
#         try:
#             options = Options()
            
#             # Performance and stealth options
#             options.add_argument('--disable-gpu')
#             options.add_argument('--disable-dev-shm-usage')
#             options.add_argument('--window-size=1920x1080')
            
#             # User agent rotation
#             user_agents = [
#                 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#                 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
#             ]
#             options.add_argument(f'user-agent={np.random.choice(user_agents)}')
            
#             # Optional: Run headless if needed
#             # options.add_argument('--headless')
            
#             driver = webdriver.Firefox(options=options)
            
#             # Additional driver configurations
#             driver.implicitly_wait(10)
#             return driver
        
#         except Exception as e:
#             self.logger.error(f"Driver setup failed: {e}")
#             raise

#     def fetch_reviews(self, url: str) -> None:
#         """
#         Scrape reviews from Tokopedia product page
        
#         Args:
#             url (str): Tokopedia product review URL
#         """
#         driver = None
#         try:
#             driver = self.setup_driver()
#             driver.get(url)
            
#             # Wait for review containers to load
#             WebDriverWait(driver, 20).until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, 'article.css-ccpe8t'))
#             )
            
#             while len(self.reviews) < self.max_reviews:
#                 # Parse current page
#                 html = driver.page_source
#                 soup = BeautifulSoup(html, 'html.parser')
                
#                 # Find review containers
#                 containers = soup.find_all('article', attrs={'class': 'css-ccpe8t'})
                
#                 for container in containers:
#                     review_elem = container.find('span', attrs={'data-testid': 'lblItemUlasan'})
                    
#                     if review_elem and review_elem.text:
#                         # Add review with unique key
#                         self.reviews[len(self.reviews)] = review_elem.text.strip()
                        
#                         self.logger.info(f"Collected review {len(self.reviews)}: {review_elem.text[:50]}...")
                    
#                     # Break if max reviews reached
#                     if len(self.reviews) >= self.max_reviews:
#                         break
                
#                 # Try to click next page button
#                 try:
#                     next_button = WebDriverWait(driver, 10).until(
#                         EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Laman berikutnya"]'))
#                     )
#                     next_button.click()
                    
#                     # Random delay between page loads
#                     time.sleep(np.random.uniform(1, 3))
                
#                 except (TimeoutException, NoSuchElementException):
#                     self.logger.warning("No more pages or next button not found")
#                     break
        
#         except Exception as e:
#             self.logger.error(f"Review scraping failed: {e}")
        
#         finally:
#             if driver:
#                 driver.quit()

#     def save_reviews(self, base_filename: str = 'tokopedia_reviews') -> None:
#         """
#         Save collected reviews to multiple formats
        
#         Args:
#             base_filename (str): Base filename for output files
#         """
#         # Timestamp for unique filenames
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         # Save JSON
#         try:
#             json_filename = f'{base_filename}_{timestamp}.json'
#             with open(json_filename, 'a', encoding='utf-8') as f:
#                 json.dump(self.review_details, f, ensure_ascii=False, indent=2)
            
#             self.logger.info(f"Saved {len(self.review_details)} reviews to {json_filename}")
        
#         except Exception as e:
#             self.logger.error(f"Failed to save JSON reviews: {e}")
        
#         # Save as CSV
#         try:
#             csv_filename = f'{base_filename}_{timestamp}.csv'
#             with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
#                 # Use DictWriter for flexible CSV export
#                 fieldnames = ['id', 'product', 'review_text', 'timestamp', 'url']
#                 writer = csv.DictWriter(f, fieldnames=fieldnames)
                
#                 # Write header
#                 writer.writeheader()
                
#                 # Write review details
#                 writer.writerows(self.review_details)
            
#             self.logger.info(f"Saved {len(self.review_details)} reviews to {csv_filename}")
        
#         except Exception as e:
#             self.logger.error(f"Failed to save CSV reviews: {e}")

# def main():
#     # Tokopedia product review URLs
#     urls = [
#         'https://www.tokopedia.com/doss/review',
#         # Add more URLs as needed
#     ]
    
#     scraper = TokopediaReviewScraper(max_reviews=5000)
    
#     for url in urls:
#         try:
#             scraper.fetch_reviews(url)
#         except Exception as e:
#             print(f"Error scraping {url}: {e}")
    
#     # Save reviews in both JSON and CSV
#     scraper.save_reviews()

# if __name__ == '__main__':
#     main()
 