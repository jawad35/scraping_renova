import requests
from bs4 import BeautifulSoup
import json
import re

def get_html_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Failed to fetch page content: {response.status_code}")

def extract_specifications(html):
    soup = BeautifulSoup(html, 'html.parser')
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

def extract_name(html):
    soup = BeautifulSoup(html, 'html.parser')
    product_name = soup.find('span', class_='product-name')
    if product_name:
        return product_name.get_text(strip=True)
    else:
        return None

def extract_price(html):
    soup = BeautifulSoup(html, 'html.parser')
    price_element = soup.find('div', class_='price')
    if price_element:
        # Extracting only the numeric part from the price
        price_text = price_element.get_text(strip=True)
        price_match = re.search(r'\d+\.\d+', price_text)
        if price_match:
            return price_match.group()
        else:
            return None
    else:
        return None

def extract_brand(html):
    soup = BeautifulSoup(html, 'html.parser')
    brand_element = soup.find('span', class_='product-brand')
    if brand_element:
        return brand_element.get_text(strip=True)
    else:
        return None

def extract_model(html):
    soup = BeautifulSoup(html, 'html.parser')
    model_element = soup.find('span', class_='product-id')
    if model_element:
        return model_element.get_text(strip=True)
    else:
        return None

def save_as_json(data, filename='specifications.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    url = 'https://www.llflooring.com/p/dream-home-xd-10mm-and-pad-delaware-bay-driftwood-laminate-flooring-7.6-in.-wide-x-54.45-in.-long-10050045.html'
    try:
        html_content = get_html_content(url)
        
        name = extract_name(html_content)
        price = extract_price(html_content)
        brand = extract_brand(html_content)
        model = extract_model(html_content)
        
        specifications = extract_specifications(html_content)
        specifications['name'] = name
        specifications['price'] = price
        specifications['brand'] = brand
        specifications['model'] = model
        
        save_as_json(specifications)
        print("Specifications extracted and saved successfully.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
