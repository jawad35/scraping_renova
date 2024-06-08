import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

def download_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded image {filename}")

def thumb_slider_images(url):
    base_url = "http://localhost:8000/"

    # Set up Selenium WebDriver with headless options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    
    # Wait for the page to fully load
    driver.implicitly_wait(10)  # Wait up to 10 seconds for elements to be present

    # Get page source and parse with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    driver.quit()

    # Find the thumbnail slider element
    thumb_slider = soup.find('div', class_='thumb-slider')

    # Initialize a list to store the image data
    image_data = []

    # Check if thumb_slider is not None before proceeding
    if thumb_slider:
        # Extract big and small images
        for i, slide in enumerate(thumb_slider.find_all('div', class_='aSlide')):
            # Extract big image URL
            big_image_url = slide['data-url']

            # Extract small image URL
            small_image_url = slide.find('div', class_='thumb')['style']
            small_image_url = small_image_url.split("('")[1].split("')")[0]

            # Define paths to save images
            big_image_path = f'big/big_image_{i + 1}.jpg'
            small_image_path = f'small/small_image_{i + 1}.jpg'

            # Download images
            download_image(big_image_url, big_image_path)
            download_image(small_image_url, small_image_path)

            # Add image URLs and paths to the image_data list
            image_data.append({
                "bigimage": base_url + big_image_path,
                "smallimage": base_url + small_image_path
            })

        # Save the image data to a JSON file
        with open('slider-images.json', 'w') as json_file:
            json.dump(image_data, json_file, indent=4)
        print("Image data saved to slider-images.json")
    else:
        print("Thumbnail slider not found.")

# # Example usage:
# url = "https://shawfloors.com/flooring/carpet/details/inspired-design-cc81b/ocean-villa"
# thumb_slider_images(url)
