import os
import requests
from bs4 import BeautifulSoup
import json

def download_image(image_url, output_dir='images'):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        image_path = os.path.join(output_dir, os.path.basename(image_url))
        os.makedirs(output_dir, exist_ok=True)

        with open(image_path, 'wb') as file:
            file.write(response.content)

        return image_path
    except Exception as e:
        return f"Error downloading image: {e}"

def extract_table_data(table):
    table_data = {}
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all(['th', 'td'])
        if len(cells) == 2:
            key = cells[0].get_text(strip=True).lower().replace(' ', '-')
            # Get the text within <p> tag if it exists
            value_tag = cells[1].find('p')
            if value_tag:
                value = value_tag.get_text(strip=True)
            else:
                value = cells[1].get_text(strip=True)
            table_data[key] = value
    return table_data

def scrape_product_data_and_download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the product model (title)
        product_model = soup.find('h1', class_='product_title entry-title').get_text(strip=True)

        # Extract the product description
        product_description = soup.find('div', class_='woocommerce-product-details__short-description').find('p').get_text(strip=True)

        # Extract the first table data
        table1 = soup.find('table')
        table_data1 = extract_table_data(table1)

        # Extract the second table data
        table2 = soup.find('table', class_='woocommerce-product-attributes shop_attributes')
        table_data2 = extract_table_data(table2)

        # Extract the image URL
        image_div = soup.find('div', class_='woocommerce-product-gallery__image')
        image_tag = image_div.find('img')
        image_url = image_tag['src']

        # If the image URL is relative, make it absolute
        if not image_url.startswith('http'):
            image_url = f"{url}/{image_url}"

        # Download the image
        image_path = download_image(image_url)

        # Extract the brand specifically
        brand = table_data2.get('brand', '')

        # Prepare the JSON-like dictionary
        product_data = {
            'meta_description':"",
            'meta_title':"",
            'brand': brand,
            'uid':product_model.replace(' ', '-').lower(),
            'model': product_model,
            'category':'countertops',
            'tables_data':{
                "t1":table_data1,
                "t2":table_data2
            },
            'images': [image_path],
            'details': product_description
        }

        return product_data
    except Exception as e:
        return {'url': url, 'error': str(e)}

def get_buildersInteriors_products_data(urls):
    results = [scrape_product_data_and_download_image(url) for url in urls]
    return results

# urls=[
#         "https://www.buildersinteriors.com/shop/slab/msi/toasted-almond/",
#         "https://www.buildersinteriors.com/shop/slab/msi/tundra-gray-marble/"
#     ]
# get_buildersInteriors_products_data(urls)