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
from dotenv import load_dotenv
load_dotenv()

base_url = "http://localhost:8000/"

app = FastAPI()

proxies={
    'http': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
    'https': 'http://jawad024:ZsvM_sKT=UN7zxg@pr.oxylabs.io:7777',
}

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

def get_all_product_details(url):
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
        selling_style_name = product_details_container.find_element(By.CLASS_NAME, 'selling-style-name').text.strip()
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


        # Initialize a list to store the image data
        image_data = []
        slide_data = []
                # Check if thumb_slider is not None before proceeding


        processed_images = 0  # Initialize counter for processed images

        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ').strip()
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                image_name = download_image(background_image_url)
                
                if image_name:
                    processed_images += 1  # Increment counter for successfully processed image
                    image_url = f"/images/{image_name}"
                    image_data.append({"color_name": color_name, "image_url": image_url})
            except Exception as e:
                print(f"Error processing swatch item: {e}")

        print(f"Total images processed: {processed_images}")
        if thumb_slider:
            # Extract big images
            big_images = driver.find_elements(By.CSS_SELECTOR, '.thumb-slider .aSlide:not([tabindex="-1"])')
            print(big_images)
            for i, slide in enumerate(big_images):
                # Extract big image URL
                big_image_url = slide.get_attribute('data-url')

                big_image_path = f'slides/slide_image_{last_segment}_{i}.jpg'

                # Download image
                download_slider_image(big_image_url, big_image_path)

                # Add image URL and path to the image_data list
                slide_data.append(big_image_path)

            # Save the image data to a JSON file
            with open('slider-images.json', 'w') as json_file:
                json.dump(image_data, json_file, indent=4)
            print("Image data saved to slider-images.json")
        else:
            print("Thumbnail slider not found.")

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
        
        product_details = {
            "meta-title":"",
            "style_title": selling_style_name,
            "color_title": selling_color_name,
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
            "description": about_text,
            "variants": image_data,
            "images":slide_data
        }

        with open("product-details.json", "a") as json_file:
            json.dump(product_details, json_file, indent=4)
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

def vinyl_scrape_urls(urls):

    threads = []
    results_queue = queue.Queue()

    for url in urls:
        thread = threading.Thread(target=process_url, args=(url, results_queue))
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
    "https://shawfloors.com/flooring/vinyl/details/paragon-tile-plus-1022v/shale",
    "https://shawfloors.com/flooring/vinyl/details/infinite-8-3339v/raw-sienna",
    "https://shawfloors.com/flooring/vinyl/details/intrepid-hd-plus-2024v/distressed-pine"
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/grounded-gray",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/sunbaked",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/natural-beauty"
    # Add more URLs as needed
]
# vinyl_scrape_urls(urls)
