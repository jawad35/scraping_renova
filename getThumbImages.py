import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import threading
import uuid
import time

def download_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded image {filename}")

def process_url(url):
    base_url = "http://localhost:8000/"

    # Set up Selenium WebDriver with headless options
    chrome_options = Options()
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    # Wait for the page to fully load
    # driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to be present

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find the thumbnail slider element
    thumb_slider = soup.find('div', class_='thumb-slider')

    # Initialize a list to store the image data
    image_data = []

    # Check if thumb_slider is not None before proceeding
    if thumb_slider:
        # Extract big images
        for i, slide in enumerate(thumb_slider.find_all('div', class_='aSlide')):
            # Extract big image URL
            big_image_url = slide['data-url']

            # Generate unique filename
            unique_id = uuid.uuid4().hex  # Generate a random UUID
            timestamp = int(time.time())   # Current timestamp
            big_image_path = f'big/big_image_{unique_id}_{timestamp}.jpg'

            # Download image
            download_image(big_image_url, big_image_path)

            # Add image URL and path to the image_data list
            image_data.append({
                "bigimage": base_url + big_image_path,
            })

        # Save the image data to a JSON file
        with open('slider-images.json', 'w') as json_file:
            json.dump(image_data, json_file, indent=4)
        print("Image data saved to slider-images.json")
    else:
        print("Thumbnail slider not found.")

def scrape_urls(urls):
    threads = []
    for url in urls:
        thread = threading.Thread(target=process_url, args=(url,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

# Example usage:
urls = [
    "https://shawfloors.com/flooring/carpet/details/cabana-life-(t)-e9958/walking-trail",
    "https://shawfloors.com/flooring/carpet/details/creating-memories-ea823/quiet-time",
    "https://shawfloors.com/flooring/carpet/details/vintage-revival-cc77b/turmeric",
    "https://shawfloors.com/flooring/carpet/details/lavish-living-cc80b/waters-edge",
    "https://shawfloors.com/flooring/carpet/details/rustique-vibe-ccs72/purity",
    "https://shawfloors.com/flooring/carpet/details/rustique-vibe-ccs72/glacier-ice"
]
scrape_urls(urls)
