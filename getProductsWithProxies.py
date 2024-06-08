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
import random
from dotenv import load_dotenv
load_dotenv()

# Define proxies
proxies = {
   
}

# Initialize FastAPI app
app = FastAPI()

def check_proxy(proxy_url):
    try:
        response = requests.get("https://www.example.com", proxies={"http": proxy_url, "https": proxy_url}, timeout=10)
        if response.status_code == 200:
            print("Proxy is working properly.")
            return True
        else:
            print(f"Proxy test failed with status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error testing proxy: {e}")
        return False


def generate_rewrite(description):
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

def decrease_price(price):
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_SECRET"))
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please decrease price by 1-5 cents less than the original '{price}'",
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
        response = requests.get(image_url, headers=headers, stream=True, proxies=proxies)
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
                time.sleep(random.uniform(2, 4))  # Random sleep between 2 and 4 seconds
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
    response = requests.get(url, proxies=proxies)
    with open(filename, 'wb') as file:
        file.write(response.content)
    print(f"Downloaded image {filename}")

def get_all_product_details(url):
    try:
        parsed_url = urlparse(url)
        last_segment = parsed_url.path.split('/')[-1]
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        # Set up the proxy settings
        chrome_options.add_argument(f'--proxy-server={proxies["http"]}')

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)

        # Add delay to allow page to load
        time.sleep(5)
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except:
            pass

        product_details_container = driver.find_element(By.ID, 'full-product-details-header-desktop')
        # selling_style_name = product_details_container.find_element(By.CLASS_NAME, 'selling-style-name').text.strip()
        selling_color_name = product_details_container.find_element(By.CLASS_NAME, 'selling-color-name').text.strip()
        price = product_details_container.find_element(By.CLASS_NAME, 'price-amount').text.strip()

        about_section = driver.find_element(By.ID, 'full-product-details-about')
        about_text = about_section.text.strip().split("Learn more")[0].strip()

        accordion_header_ids = ['headingOne']
        table_data = extract_table_data(driver, accordion_header_ids)

        swatch_items = driver.find_elements(By.CLASS_NAME, 'swatch-item')
        about_text = generate_rewrite(about_text)
        price = decrease_price(price)
        thumb_slider = driver.find_element(By.CSS_SELECTOR, 'div.thumb-slider')

        image_data = []
        slide_data = []

        processed_images = 0

        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ').strip()
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                image_name = download_image(background_image_url)
                
                if image_name:
                    processed_images += 1
                    image_url = f"/images/{image_name}"
                    image_data.append({"color_name": color_name, "image_url": image_url})
                time.sleep(random.uniform(1, 3))  # Random sleep between 1 and 3 seconds after processing each swatch item
            except Exception as e:
                print(f"Error processing swatch item: {e}")

        print(f"Total images processed: {processed_images}")
        if thumb_slider:
            big_images = driver.find_elements(By.CSS_SELECTOR, '.thumb-slider .aSlide:not([tabindex="-1"])')
            for i, slide in enumerate(big_images):
                big_image_url = slide.get_attribute('data-url')
                big_image_path = f'slides/slide_image_{last_segment}_{i}.jpg'
                download_slider_image(big_image_url, big_image_path)
                slide_data.append(big_image_path)
                time.sleep(random.uniform(1, 3))  # Random sleep between 1 and 3 seconds after downloading each slider image

            with open('slider-images.json', 'w') as json_file:
                json.dump(image_data, json_file, indent=4)
            print("Image data saved to slider-images.json")
        else:
            print("Thumbnail slider not found.")

        path = parsed_url.path
        desired_part = path.split("/flooring/carpet/details/")[1]

        product_details = {
            # "style_title": selling_style_name,
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
            "variants": image_data,
            "images": slide_data
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

def process_url(url, results_queue):
    try:
        product_details = get_all_product_details(url)
        if product_details:
            print(f"Product details scraped successfully for URL: {url}")
            results_queue.put(product_details)
        else:
            print(f"Failed to scrape product details for URL: {url}")
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

def scrape_urls(urls):
    if not check_proxy(proxies['http']):
        print("Proxy is not working properly. Please check your proxy settings.")
        return        
    threads = []
    results_queue = queue.Queue()

    for url in urls:
        thread = threading.Thread(target=process_url, args=(url, results_queue))
        threads.append(thread)
        thread.start()
        time.sleep(random.uniform(1, 5))  # Random sleep between 1 and 5 seconds before starting each thread

    for thread in threads:
        thread.join()

    results = []
    while not results_queue.empty():
        results.append(results_queue.get())

    return results

# Example usage:
urls = [
    "https://shawfloors.com/flooring/carpet/details/nature-within-5e278/washed-linen",
    "https://shawfloors.com/flooring/carpet/details/essential-now-5e290/serene-still",
    # Add more URLs as needed
]
scrape_urls(urls)
