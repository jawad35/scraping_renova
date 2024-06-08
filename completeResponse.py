import os
import requests
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import pandas as pd
from fastapi import FastAPI
from selenium.webdriver.chrome.options import Options
from openai import OpenAI
import threading
from bs4 import BeautifulSoup
import uuid
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dotenv import load_dotenv
load_dotenv()

base_url = "http://localhost:8000/"

app = FastAPI()

def generate_rewrite(description):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please generate or rewrite the given description for meta description within 60 to 150 characters using all parameters and remove all dirty or useless data: '{description}'",
            max_tokens=100,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating rewrite: {e}")
        return description

def decrease_price(price, api_key):
    try:
        client = OpenAI(api_key=api_key)
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please decrease the price by 1-5 cents less than the original: '{price}'",
            max_tokens=100,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error decreasing price: {e}")
        return price

def download_image(image_url, save_directory='images'):
    try:
        parsed_url = urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        headers = {'User-Agent': 'Mozilla/5.0'}
        
        # Set up session with retries
        session = requests.Session()
        retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retries))
        
        response = session.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            image_path = os.path.join(save_directory, image_name)
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return image_name
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def extract_table_data(driver, accordion_header_ids):
    try:
        data = {}
        for header_id in accordion_header_ids:
            try:
                header = driver.find_element(By.ID, header_id)
                header.click()
                time.sleep(1)
            except Exception as e:
                print(f"Error clicking header {header_id}: {e}")
                continue
            table = driver.find_element(By.CSS_SELECTOR, '#full-product-details-specs .specs .table.table-striped')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    data[key] = value
        return data
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return {}

def download_slider_image(url, filename):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded image {filename}")
        else:
            print(f"Failed to download image. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading slider image: {e}")

def get_all_product_details(url):
    try:
        chrome_options = Options()
        # chrome_options.add_argument("--headless")  # Uncomment to run headless
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except Exception as e:
            print(f"Error accepting cookies: {e}")

        product_details_container = driver.find_element(By.ID, 'full-product-details-header-desktop')
        selling_style_name = product_details_container.find_element(By.CLASS_NAME, 'selling-style-name').text.strip()
        selling_color_name = product_details_container.find_element(By.CLASS_NAME, 'selling-color-name').text.strip()
        price = product_details_container.find_element(By.CLASS_NAME, 'price-amount').text.strip()

        about_section = driver.find_element(By.ID, 'full-product-details-about')
        about_text = about_section.text.strip().split("Learn more")[0].strip()

        accordion_header_ids = ['headingOne']
        table_data = extract_table_data(driver, accordion_header_ids)

        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        image_data = []

        about_text = generate_rewrite(about_text)
        price = decrease_price(price)

        # Get page source and parse with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the thumbnail slider element
        thumb_slider = soup.find('div', class_='thumb-slider')

        driver.quit()

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
                print(f"Error processing swatch item: {e}")

        if thumb_slider:
            for i, slide in enumerate(thumb_slider.find_all('div', class_='aSlide')):
                big_image_url = slide['data-url']
                unique_id = uuid.uuid4().hex
                timestamp = int(time.time())
                big_image_path = f'images/big_image_{unique_id}_{timestamp}.jpg'
                download_slider_image(big_image_url, big_image_path)
                image_data.append({
                    "bigimage": f"{base_url}{big_image_path}",
                })

        parsed_url = urlparse(url)
        path = parsed_url.path
        desired_part = path.split("/flooring/carpet/details/")[1]

        product_details = {
            "style_title": selling_style_name,
            "color_title": selling_color_name,
            "category": "carpets",
            "url": "/" + desired_part,
            "style": table_data.get("Style", ""),
            "color": table_data.get("Color", ""),
            "collection": table_data.get("Collection", ""),
            "fiber": table_data.get("Fiber", ""),
            "fiber_brand": table_data.get("Fiber Brand", ""),
            "width": table_data.get("Width", ""),
            "style_type": table_data.get("Style Type", ""),
            "face_weight": table_data.get("Face Weight", ""),
            "stain_treatment": table_data.get("Stain Treatment", ""),
            "backing": table_data.get("Backing", ""),
            "usa": table_data.get("Made in the USA", "").upper() == "YES",
            "country_of_origin": table_data.get("Country of Origin", ""),
            "description": about_text,
            "images": image_data,
        }

        with open("product-details.json", "a") as json_file:
            json.dump(product_details, json_file, indent=4)
        
        df = pd.DataFrame([product_details])
        df.to_excel("product-details.xlsx", index=False)
        
        return product_details
    except Exception as e:
        print(f"Error scraping product details: {e}")
        return None
    finally:
        driver.quit()

def process_url(url):
    try:
        product_details = get_all_product_details(url)
        if product_details:
            print(f"Product details scraped successfully for URL: {url}")
        else:
            print(f"Failed to scrape product details for URL: {url}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

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
    "https://shawfloors.com/flooring/carpet/details/tonal-comfort-blue-5e658/sun-kissed",
    # Add more URLs as needed
]
scrape_urls(urls)
