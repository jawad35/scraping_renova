import os
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Function to download an image
def download_image(image_url, save_directory='images'):
    try:
        # Parse the URL to get the image name
        parsed_url = urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)

        # Ensure the save directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Set the headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Send a GET request to the image URL
        response = requests.get(image_url, headers=headers, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            image_path = os.path.join(save_directory, image_name)
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Image successfully downloaded: {image_path}")
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Initialize the WebDriver (specify the path to your WebDriver if it's not in your PATH)
driver = webdriver.Chrome()

# Open the webpage
driver.get('https://shawfloors.com/flooring/carpet/details/nature-within-5e278/washed-linen')  # Replace with your actual webpage URL

# Wait for the page to load completely
time.sleep(3)  # Adjust the sleep time if necessary

# Function to click on accordion headers by their IDs
def click_accordion_header(header_id):
    try:
        header = driver.find_element(By.ID, header_id)
        header.click()
        time.sleep(1)  # Pause to allow the section to expand
    except Exception as e:
        print(f"Could not click header {header_id}: {e}")

# Click the specific accordion header to open it
click_accordion_header('headingThree')

# Example of extracting key-value pairs from the table within the opened section
def extract_color_info():
    try:
        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        color_info = []

        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ').strip()
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                color_info.append((color_name, background_image_url))
            except Exception as e:
                print(f"Could not extract data from an item: {e}")

        return color_info
    except Exception as e:
        print(f"Could not extract color info: {e}")
        return []

# Extract the color information
color_data = extract_color_info()

# Download each image to a category folder
category_folder = 'carpet_colors'
for color_name, image_url in color_data:
    print(f"Downloading {color_name} from {image_url}")
    download_image(image_url, save_directory=category_folder)

# Optionally, wait before closing the driver

# Close the driver
driver.quit()
