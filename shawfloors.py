import asyncio
import aiohttp
import ssl
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Disable SSL certificate verification
ssl_context = ssl.SSLContext()
ssl_context.verify_mode = ssl.CERT_NONE

async def fetch(url, session):
    async with session.get(url, ssl=ssl_context) as response:
        return await response.text()

async def fetch_all(urls):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in urls:
            tasks.append(fetch(url, session))
        return await asyncio.gather(*tasks)

def extract_hrefs(html, class_name):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', {'class': class_name})
    return [link.get('href') for link in links]

def get_product_links(base_url, start_page, end_page, class_name):
    urls = [f"{base_url}/{i}" for i in range(start_page, end_page+1)]
    print(urls)
    html_pages = asyncio.run(fetch_all(urls))
    all_hrefs = []
    for html in html_pages:
        all_hrefs.extend(extract_hrefs(html, class_name))
    # Prepend base_url to relative links
    complete_links = [urljoin(base_url, href) for href in all_hrefs]
    return complete_links

# Example usage
base_url = 'https://shawfloors.com/flooring/carpet'  # Updated base URL
start_page = 1
end_page = 3  # Set the end page number
class_name = 'detail-link'  # Set the dynamic class name here

product_links = get_product_links(base_url, start_page, end_page, class_name)

# Save as JSON file
output_filename = "product-links.json"
with open(output_filename, "w") as json_file:
    json.dump(product_links, json_file)

print("Total URLs extracted:", len(product_links))
print("Data saved to", output_filename)
