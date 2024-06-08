import os
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from fastapi import FastAPI
from selenium.webdriver.chrome.options import Options

app = FastAPI()

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
            return image_name
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to scrape table data from a webpage
def extract_table_data(url, accordion_header_ids, driver):
    try:
        extracted_data = {"description": {}}

        # Function to click on accordion headers by their IDs
        def click_accordion_header(header_id):
            try:
                header = driver.find_element(By.ID, header_id)
                header.click()
                time.sleep(1)  # Pause to allow the section to expand
            except Exception as e:
                print(f"Could not click header {header_id}: {e}")

        # Click each accordion header and extract data
        for header_id in accordion_header_ids:
            click_accordion_header(header_id)
            table = driver.find_element(By.CSS_SELECTOR, '#full-product-details-specs .specs .table.table-striped')

            # Extract key-value pairs from the table
            data = {}
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    data[key] = value

            extracted_data["description"][header_id] = data

        return extracted_data
    except Exception as e:
        print(f"An error occurred while extracting table data: {e}")
        return None

# Function to scrape and save product details
def scrape_and_save_product_details(url):
    try:
        # Set up Chrome options for headless browsing
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Initialize the WebDriver with headless Chrome
        driver = webdriver.Chrome(options=chrome_options)
        
        # Open the webpage
        driver.get(url)

        # Wait for the cookie consent button to be clickable and then dismiss it
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except:
            pass  # If the element is not clickable or not found, do nothing

        # Allow time for dynamic content to load
        time.sleep(5)  # Adjust the sleep time as needed

        # Find the product details container
        product_details_container = driver.find_element(By.ID, 'full-product-details-header-desktop')

        # Extract selling style name
        selling_style_name_elem = product_details_container.find_element(By.CLASS_NAME, 'selling-style-name')
        selling_style_name = selling_style_name_elem.text.strip() if selling_style_name_elem else None

        # Extract selling color name and number
        selling_color_name_elem = product_details_container.find_element(By.CLASS_NAME, 'selling-color-name')
        selling_color_name = selling_color_name_elem.text.strip() if selling_color_name_elem else None

        # Extract price
        price_elem = product_details_container.find_element(By.CLASS_NAME, 'price-amount')
        price = price_elem.text.strip() if price_elem else None

        # Extract financing availability link
        financing_available_elem = product_details_container.find_element(By.XPATH, '//a[contains(@href,"product-info/financing")]')
        financing_available_link = financing_available_elem.get_attribute('href') if financing_available_elem else None

        # Find the product details about section
        about_section = driver.find_element(By.ID, 'full-product-details-about')
        about_text = about_section.text.strip() if about_section else None

        # Filter out the "Learn more" text from the about_text
        if about_text and "Learn more" in about_text:
            about_text = about_text.split("Learn more")[0].strip()

        # Scrape and save table data
        accordion_header_ids = ['headingOne']
        table_data = extract_table_data(url, accordion_header_ids, driver)

        # Download images and collect their URLs along with color names
        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        image_data = []
        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ').strip()
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                image_name = download_image(background_image_url)
                if image_name:
                    image_url = f"http://localhost:8000/images/{image_name}"
                    image_data.append({"color_name": color_name, "image_url": image_url})
            except Exception as e:
                print(f"Could not download image: {e}")

        # Combine scraped data
        product_details = {
            "selling_style_name": selling_style_name,
            "selling_color_name": selling_color_name,
            "price": price,
            "financing_available_link": financing_available_link,
            "about_text": about_text,
            "table_data": table_data,
            "image_data": image_data
        }

        # Save the combined data to a JSON file
        with open("product-details.json", "w") as json_file:
            json.dump(product_details, json_file, indent=4)
            print("Product details saved to product-details.json")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Close the WebDriver
        # Close the WebDriver
        driver.quit()

# Example URL
url = "https://shawfloors.com/flooring/carpet/details/vastly-5e324/nature-walk"

# Scrape and save product details
scrape_and_save_product_details(url)
