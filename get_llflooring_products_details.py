import aiohttp
import asyncio
import os
import json
from bs4 import BeautifulSoup
import re
from aiohttp import TCPConnector

async def fetch(session, url):
    async with session.get(url, ssl=False) as response:
        if response.status == 200:
            return await response.text()
        else:
            raise Exception(f"Failed to fetch page content: {response.status}")

def extract_specifications(soup):
    product_specifications = soup.find('div', class_='product-specifications')
    if not product_specifications:
        raise Exception("Product specifications div not found")

    spec_data = {}
    table_count = 1

    for section in product_specifications.find_all('div', class_='spec-section'):
        header = section.find('p', class_='spec-head').get_text(strip=True)
        table_key = f"t{table_count}"
        table_count += 1

        spec_dict = {}
        for item in section.find_all('li'):
            key = item.find('div', class_='spec-name').contents[0].strip().replace(' ', '-').lower()
            value_div = item.find('div', class_='spec-details')
            value = ', '.join([span.get_text(strip=True) for span in value_div.find_all('span')])
            spec_dict[key] = value

        spec_data[table_key] = spec_dict

    return spec_data

def extract_name(soup):
    product_name = soup.find('span', class_='product-name')
    return product_name.get_text(strip=True) if product_name else None

def extract_price(soup):
    price_element = soup.find('div', class_='price')
    if not price_element:
        price_element = soup.find('div', class_='price price-sale')
    
    if price_element:
        # Extract the first numeric price value
        price_text = price_element.get_text(strip=True)
        price_match = re.search(r'\$\d+\.\d+', price_text)
        if price_match:
            return price_match.group().replace('$', '')
    return None

def extract_brand(soup):
    brand_element = soup.find('span', class_='product-brand')
    return brand_element.get_text(strip=True) if brand_element else None

def extract_model(soup):
    model_element = soup.find('span', class_='product-id')
    return model_element.get_text(strip=True) if model_element else None

def extract_product_details(soup):
    product_details = soup.find('div', class_='description-and-detail')
    if not product_details:
        raise Exception("Product details section 'description-and-detail' not found")

    details_data = {}
    process_element(product_details, details_data)
    return details_data

def process_element(element, data, tag_counts=None):
    if tag_counts is None:
        tag_counts = {}

    if element.name == 'p' or element.name == 'ul' or element.name == 'li' or element.name == 'div' or element.name == 'h2' or element.name == 'h3' or element.name == 'h4' or element.name == 'span' or element.name == 'a':
        tag_name = element.name
        if tag_name not in tag_counts:
            tag_counts[tag_name] = 1
        else:
            tag_counts[tag_name] += 1

        numbered_tag_name = f"{tag_name}{tag_counts[tag_name]}"
        if numbered_tag_name not in data:
            data[numbered_tag_name] = []
        
        data[numbered_tag_name].append(element.get_text(strip=True))
        
        for child in element.children:
            if child.name is not None:
                process_element(child, data, tag_counts)
    return data

async def download_images(session, soup, model):
    zoom_slider = soup.find('div', class_='product-image-zoom-slider')
    image_data = []

    if zoom_slider:
        product_images = zoom_slider.find_all('div', class_='product-image')
        os.makedirs('llflooringSlides', exist_ok=True)

        for index, product_image in enumerate(product_images):
            img_tag = product_image.find('img')
            if img_tag and 'data-imgurl' in img_tag.attrs:
                img_url = img_tag['data-imgurl']

                async with session.get(img_url, ssl=False) as img_response:
                    if img_response.status == 200:
                        img_name = f"{model}_image_{index}.jpg"
                        img_path = os.path.join('llflooringSlides', img_name)

                        with open(img_path, 'wb') as f:
                            f.write(await img_response.read())

                        image_data.append(
                            img_url
                        )
                    else:
                        print(f"Failed to download image {img_url}")

    return image_data

async def process_url(session, url):
    html_content = await fetch(session, url)
    soup = BeautifulSoup(html_content, 'html.parser')

    name = extract_name(soup)
    price = extract_price(soup)
    brand = extract_brand(soup)
    model = extract_model(soup)
    specifications = extract_specifications(soup)
    details = extract_product_details(soup)
    images = await download_images(session, soup, model)

    data = {
        "url": url,
        "name": name,
        "price": float(price),
        "brand": brand,
        "model": model,
        "specifications": specifications,
        "details": details,
        "images": images
    }
    return data

async def get_llflooring_products_data(urls):
    connector = TCPConnector(ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [process_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results

# List of URLs to process
# urls = [
#     "https://www.llflooring.com/p/dream-home-xd-10mm-and-pad-delaware-bay-driftwood-laminate-flooring-7.6-in.-wide-x-54.45-in.-long-10050045.html",
#     "https://www.llflooring.com/p/dream-home-8mm-mountain-trail-oak-wpad-waterproof-laminate-flooring-8.03-in.-wide-x-48-in.-long-10054225.html",
#     # Add more URLs here
# ]

# # Run the main function and save the results
# if __name__ == '__main__':
#     results = asyncio.run(main(urls))
#     with open('scraped_data.json', 'w', encoding='utf-8') as f:
#         json.dump(results, f, ensure_ascii=False, indent=4)
#     print("Scraping completed and data saved to scraped_data.json")
