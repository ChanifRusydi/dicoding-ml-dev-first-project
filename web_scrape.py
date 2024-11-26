import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup
import os

def scrape_page(URL):
    # firefox_driver_path = "./geckodriver"
    # options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox()

    try:
        driver.get(URL)
        html = driver.page_source
        return html
        # soup = BeautifulSoup(driver.page_source, 'html.parser')
        # return soup
    except Exception as e:
        print(f'Error: {e}')
    finally:
        driver.quit()

if __name__ == '__main__':
    URL = 'tokopedia.com/doss/saramonic-blink-500-b2-tx-tx-rx-wireless-omni-lavarier-mic-new-version-f0c7b'
    # URL = "https://www.tokopedia.com/copperindonesia/review"
    
    # driver = webdriver.Firefox()
    # driver.get(URL)
    # soup = BeautifulSoup(driver.page_source, 'html.parser')
    # print(soup)

    # page = requests.get(URL)
    result = scrape_page(URL)
    print(result)
