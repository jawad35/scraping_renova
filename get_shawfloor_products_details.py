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


from dotenv import load_dotenv
load_dotenv()

base_url = "http://localhost:8000/"

app = FastAPI()

# proxies={
#     'http': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
#     'https': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
# }

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

def download_image(image_url, save_directory='images'):
    try:
        parsed_url = urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)
        headers = {'User-Agent': 'Mozilla/5.0'}
        # response = requests.get(image_url, headers=headers, stream=True, proxies=proxies)
        response = requests.get(image_url, headers=headers, stream=True)
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
            except:
                pass
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
    response = requests.get(url)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded image {filename}")

def get_all_product_details(url, category):
    try:
        parsed_url = urlparse(url)
        last_segment = parsed_url.path.split('/')[-1]
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except:
            pass

        product_details_container = driver.find_element(By.ID, 'full-product-details-header-desktop')
        price = product_details_container.find_element(By.CLASS_NAME, 'price-amount').text.strip()

        about_section = driver.find_element(By.ID, 'full-product-details-about')
        details_content = about_section.text.strip().split("Learn more")[0].strip()

        accordion_header_ids = ['headingOne']
        table_data = extract_table_data(driver, accordion_header_ids)
        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        details_content = rewrite_description(details_content)
        price = price_decreaser(price)
        print(table_data)
        price(meta_description_generator(table_data))
        thumb_slider = driver.find_element(By.CSS_SELECTOR, 'div.thumb-slider')
        # Initialize a list to store the image data
        variant_images_data = []
        slide_images_data = []
                # Check if thumb_slider is not None before proceeding


        processed_images = 0  # Initialize counter for processed images


        parsed_url = urlparse(url)
        path = parsed_url.path
        # Adding debug statement
        print(f"Parsed URL path: {path}")
        parts = path.split("/flooring/")
        if len(parts) > 1:
            desired_part = parts[1]
        else:
            print(f"Error: Unexpected URL structure: {path}")
            desired_part = "unknown"
        print(table_data)
        print(meta_description_generator(table_data))
        product_data = {
            'meta_description':meta_description_generator(table_data),
            # 'meta_title':meta_title_generator(table_data),
            # 'uid':uid,
            'price': price,
            # 'model': '',
            'category':category,
            'tables_data': {"t1":table_data},
            'variants': variant_images_data,
            'images': slide_images_data,
            "details": details_content
        }
        print(product_data)
        product_details = {
            "meta-title":"",
            "category": "carpets",
            "url": "/" + desired_part,
            "style": table_data.get("Style", ""),
            "color": table_data.get("Color", ""),
            "collection": table_data.get("Collection", ""),
            "construction": table_data.get("Construction", ""),
            "finish": table_data.get("Finish", ""),
            "width": table_data.get("Width", ""),
            "length": table_data.get("Length", ""),
            "plank_thickness": table_data.get("Plank Thickness", ""),
            "sq_ft_per_box": table_data.get("Sq. Ft. Per Box", ""),
            "installation_method": table_data.get("Installation Method", ""),
            "installation_grade": table_data.get("Installation Grade", ""),
            "wear_layer": table_data.get("Wear Layer", ""),
            "description": details_content,
            "variants": variant_images_data,
            "images":slide_images_data
        }
        print(product_details)
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

# Example usage:
urls = [
    # "https://shawfloors.com/flooring/carpet/details/cabana-life-(t)-e9958/walking-trail",
    # "https://shawfloors.com/flooring/carpet/details/tonal-comfort-blue-5e658/sun-kissed",
    # "https://shawfloors.com/flooring/carpet/details/essential-now-5e290/serene-still",
    # "https://shawfloors.com/flooring/hardwood/details/landmark-sliced-oak-sw747/gateway",
    "https://shawfloors.com/flooring/vinyl/details/paragon-hdnatural-bevel-3038v/oriel",
    # "https://shawfloors.com/flooring/vinyl/details/paragon-tile-plus-1022v/shale",
    # "https://shawfloors.com/flooring/vinyl/details/infinite-8-3339v/raw-sienna",
    # "https://shawfloors.com/flooring/vinyl/details/intrepid-hd-plus-2024v/distressed-pine"
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/grounded-gray",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/sunbaked",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/natural-beauty"
    # Add more URLs as needed
]
# get_shawfloor_products_data(urls, 'vinyl')