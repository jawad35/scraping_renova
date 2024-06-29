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
import queue
from utils.meta_description_generator import meta_description_generator
from utils.meta_title_generator import meta_title_generator
from utils.price_decreaser import price_decreaser
from utils.rewriter import rewriter

from dotenv import load_dotenv
load_dotenv()

base_url = "http://localhost:8000/"

app = FastAPI()

def rewrite_description(description):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please generate or rewrite given description for meta description within 60 to 150 characters using all parameters and please remove all dirty or useless data '{description}'",
            max_tokens=100,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating rewrite: {e}")
        return description

def download_image(image_url, save_directory):
    try:
        parsed_url = urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code == 200:
            image_path = os.path.join(save_directory, image_name)
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            return image_path
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
            except:
                pass
            table = driver.find_element(By.CSS_SELECTOR, '#full-product-details-specs .specs .table.table-striped')
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) == 2:
                    key = cells[0].text.strip().replace(" ","-").lower()
                    value = cells[1].text.strip()
                    data[key] = value
        return data
    except Exception as e:
        print(f"Error extracting table data: {e}")
        return {}

def download_slider_image(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded image {filename}")

def get_text_after_segment(url, segment):
    parts = url.split('/')
    try:
        return '/'.join(parts[parts.index(segment) + 1:])
    except ValueError:
        return None
    
def get_all_product_details(url, category):
    try:
        last_segment = get_text_after_segment(url, 'details').replace(" ", '-').lower()
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except:
            pass
        product_details_container = driver.find_element(By.ID, 'full-product-details-header-desktop')
        about_section = driver.find_element(By.ID, 'full-product-details-about')
        details_content = about_section.text.strip().split("Learn more")[0].strip()
        accordion_header_ids = ['headingOne']
        table_data = extract_table_data(driver, accordion_header_ids)
        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        details_content = rewrite_description(details_content)
        price = product_details_container.find_element(By.CLASS_NAME, 'price-amount').text.strip()
        price = price_decreaser(f'${price}')
        thumb_slider = driver.find_element(By.CSS_SELECTOR, 'div.thumb-slider')

        # Directory setup
        main_directory = "products"
        category_directory = os.path.join(main_directory, category)
        product_directory = os.path.join(category_directory, last_segment.replace("/", "-").replace(" ", "").lower())
        variant_directory = os.path.join(product_directory, "variants")
        slide_directory = os.path.join(product_directory, "slides")

        os.makedirs(variant_directory, exist_ok=True)
        os.makedirs(slide_directory, exist_ok=True)

        # Initialize a list to store the image data
        image_data = []
        slide_data = []
        filtering = []

        processed_images = 0  # Initialize counter for processed images

        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ').strip()
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                image_path = download_image(background_image_url, variant_directory)
                print(image_path)
                if image_path:
                    processed_images += 1  # Increment counter for successfully processed image
                    
                    if color_name.replace(" ", '-').lower() == '':
                        filtering.append()
                    # print(color_name.replace(" ", '-').lower())
                    image_data.append({"color_name": color_name.replace(" ", '-').lower(), "image_url": image_path})
            except Exception as e:
                print(f"Error processing swatch item: {e}")
        if thumb_slider:
            # Extract big images
            big_images = driver.find_elements(By.CSS_SELECTOR, '.thumb-slider .aSlide:not([tabindex="-1"])')
            for i, slide in enumerate(big_images):
                # Extract big image URL
                big_image_url = slide.get_attribute('data-url')
                big_image_path = os.path.join(slide_directory, f'slide_image_{i}.jpg')
                # Download image
                download_slider_image(big_image_url, big_image_path)
                print(os.path.relpath(big_image_path, start=main_directory), '90')
                # Add image URL and path to the image_data list
                slide_data.append(big_image_path)
            # Save the image data to a JSON file
            with open('slider-images.json', 'w') as json_file:
                json.dump(image_data, json_file, indent=4)
            print("Image data saved to slider-images.json")
        else:
            print("Thumbnail slider not found.")
        parsed_url = urlparse(url)
        path_components = parsed_url.path.split('/')
        product_id = path_components[-2].replace('-', ' ')  # Replace hyphens with spaces
        product_name = path_components[-1].replace('-', ' ')  # Replace hyphens with spaces
        title = f'{product_name} {product_id}' 
        pro_url = f'{product_id.replace(" ", "-").lower()}-{product_name.replace(" ", "-").lower()}-{table_data.get('width').replace(" ", '')}-{table_data.get('collection').replace(" ", "-").lower()}' 
        product_details = {
            'meta_description':meta_description_generator({"t1": table_data}),
            'meta_title':meta_title_generator(title),
            'url':pro_url,
            'uid': product_id.replace(" ", "-").lower(),
            'filtering': f'{product_name.replace(" ", "-").lower()}-{table_data.get("color").split(' ')[0].lower()}',
            'price': price,
            'brand': 'shawfloors',
            'model':product_id.replace(" ", "-").lower(),
            'category': category.lower(),
            'specifications': {"t1": table_data},
            'variants': image_data,
            'images': slide_data,
            "details": {"p":rewriter(details_content)}
        }
        with open("product-details.json", "a") as json_file:
            json.dump(product_details, json_file, indent=4)
        
        return product_details
    except Exception as e:
        print(f"Error scraping product details: {e}")
        return None
    finally:
        driver.quit()

def process_url(url, results_queue, category):
    try:
        product_details = get_all_product_details(url, category)
        if product_details:
            print(f"Product details scraped successfully for URL: {url}")
            results_queue.put(product_details)
        else:
            print(f"Failed to scrape product details for URL: {url}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

def get_shawfloor_products_data(urls, category):
    threads = []
    results_queue = queue.Queue()

    for url in urls:
        thread = threading.Thread(target=process_url, args=(url, results_queue, category))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())
    return results

# # Example usage:
# urls = [
#     "https://shawfloors.com/flooring/carpet/details/vintage-revival-cc77b/turmeric",
#     # Add more URLs as needed
# ]
# get_shawfloor_products_data(urls, 'vinyl')
