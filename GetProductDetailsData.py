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
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

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

def get_all_product_details(url):
    try:
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
        image_data = []
        about_text = generate_rewrite(about_text)
        price = decrease_price(price)

        for item in swatch_items:
            try:
                color_name = item.find_element(By.CLASS_NAME, 'item-color-name').get_attribute('innerHTML').replace('<br>', ' ').strip()
                background_image_style = item.find_element(By.CLASS_NAME, 'swatchThumb').get_attribute('style')
                background_image_url = background_image_style.split('url(')[-1].split(');')[0].strip('\'"')
                image_name = download_image(background_image_url)
                print(image_name)
                if image_name:
                    image_url = f"http://localhost:8000/images/{image_name}"
                    image_data.append({"color_name": color_name, "image_url": image_url})
            except Exception as e:
                print(f"Error processing swatch item: {e}")

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
    # "https://shawfloors.com/flooring/carpet/details/cabana-life-(t)-e9958/walking-trail",
    "https://shawfloors.com/flooring/carpet/details/tonal-comfort-blue-5e658/sun-kissed",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/grounded-gray",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/sunbaked",
    # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/natural-beauty"
    # Add more URLs as needed
]
scrape_urls(urls)
