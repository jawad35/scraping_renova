import requests
from bs4 import BeautifulSoup
import json
import os
import threading
import openai

variant_images_data = []
slide_images_data = []

def generate_rewrite(description, api_key):
    try:
        client = openai.Client(api_key=api_key)
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please rewrite the content of every html tag '{description}'",
            max_tokens=4000,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating rewrite: {e}")
        return description

def download_image(url, folder_path, image_name):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        with open(os.path.join(folder_path, image_name), 'wb') as file:
            file.write(response.content)
        print(f"Downloaded {image_name} in {folder_path}")
    except Exception as e:
        print(f"Error downloading {image_name}: {e}")

def process_url(url, base_image_folder):
    try:
        # Scrape the data using BeautifulSoup
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the span tags with the specific attributes and class names
        price_span = soup.find('span', {'data-automation': 'price', 'class': 'lh-copy'})
        model_span = soup.find('span', {'data-automation': 'product-model-number', 'class': 'b'})
        product_title_span = soup.find('span', {'class': 'fw2 di-ns'})

        if price_span:
            price = price_span.text.strip()
        else:
            price = "Price not found"

        if model_span:
            model = model_span.text.strip()
        else:
            model = "Model not found"

        if product_title_span:
            product_title = product_title_span.text.strip()
        else:
            product_title = "Product title not found"
        # Find the <div> element with class 'lh-copy H_oFW'
        div_element = soup.find('div', class_='lh-copy H_oFW')
        # Get the HTML content of the <div> element
        if div_element:
            details_content = div_element.prettify()  # Get the prettified HTML content
        else:
            print("No <div> element found with class 'lh-copy H_oFW'")

        table_divs = soup.find_all('div', class_='w-100 w-third-ns')
        all_tables_data = {}
        table_count = 1

        for table_div in table_divs:
            nested_divs = table_div.find_all('div', class_='db-ns')

            for nested_div in nested_divs:
                table_data = {}
                tbodies = nested_div.find_all('tbody')

                for tbody in tbodies:
                    tbody_data = {}
                    rows = tbody.find_all('tr')
                    for row in rows:
                        cols = row.find_all('td')
                        if len(cols) == 2:
                            key = cols[0].get_text(strip=True)
                            value = cols[1].get_text(strip=True)
                            tbody_data[key] = value
                    if tbody_data:
                        table_data[f't{table_count}'] = tbody_data
                        table_count += 1
                if table_data:
                    all_tables_data.update(table_data)

        # Create directories for the product
        root_folder = 'products'
        main_folder = os.path.join(root_folder, base_image_folder)
        product_folder = os.path.join(main_folder, model)
        os.makedirs(product_folder, exist_ok=True)

        # Create subfolders for slide and variant images
        slide_folder = os.path.join(product_folder, 'slide')
        variant_folder = os.path.join(product_folder, 'variant')
        os.makedirs(slide_folder, exist_ok=True)
        os.makedirs(variant_folder, exist_ok=True)

        def download_images_from_divs(div_class, type):
            image_divs = soup.find_all('div', class_=div_class)
            folder = slide_folder if type == 'slide' else variant_folder
            for index, div in enumerate(image_divs):
                img_tag = div.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    img_url = img_tag['src']
                    img_name = f'{type}_image_{index+1}.jpg'
                    if type == 'variant':
                        color_div = div.find('div', style=True)
                        if color_div:
                            style = color_div.get('style')
                            color = style.split('background-color:')[1].split(';')[0].strip()
                            img_name = f'{type}_image_{index+1}_{color}.jpg'
                            variant_images_data.append({'img': f'products/{base_image_folder}/{model}/variant/{img_name}', 'color_name': color})
                    download_image(img_url, folder, img_name)
                    if type == 'slide':
                        slide_images_data.append(f'products/{base_image_folder}/{model}/slide/{img_name}')

        # Download images
        # download_images_from_divs('br2', 'variant')
        # download_images_from_divs('transform-component-module_content__FBWxo', 'slide')

        # Generate rewrite for details content
        details_content = generate_rewrite(details_content, '')

        # Save the extracted table data and other details to a JSON file
        product_data = {
            'price': price,
            'model': model,
            'product_title': product_title,
            'tables_data': all_tables_data,
            'variants': variant_images_data,
            'images': slide_images_data,
            "details_content": details_content
        }
        json_filename = os.path.join(product_folder, f'{model}_data.json')
        with open(json_filename, 'w') as json_file:
            json.dump(product_data, json_file, indent=4)
        print(f"Saved data to {json_filename}")
    
    except Exception as e:
        print(f"Error processing URL {url}: {e}")

def process_urls_concurrently(urls, base_image_folder):
    threads = []
    for url in urls:
        try:
            thread = threading.Thread(target=process_url, args=(url, base_image_folder))
            threads.append(thread)
            thread.start()
        except Exception as e:
            print(f"Error creating thread for URL {url}: {e}")

    for thread in threads:
        thread.join()

# Your list of URLs to scrape
urls = [
    "https://www.build.com/delta-9913-dst/s1136294?uid=2726482&searchId=XhFZIIn7LS"
    # Add more URLs here
]

# Base directory to save images and data
base_image_folder = 'Faucet'

# Process all URLs concurrently
process_urls_concurrently(urls, base_image_folder)
