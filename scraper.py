from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import pandas as pd
import json

# Initialize the WebDriver (specify the path to your WebDriver if it's not in your PATH)
driver = webdriver.Chrome() 

# Open the webpage
driver.get('https://shawfloors.com/flooring/carpet')  # Use the base URL

# Wait for the page to load completely
time.sleep(3)  # Adjust the sleep time if necessary

try:
    # Find the element with class 'prev disabled'
    prev_element = driver.find_element(By.CSS_SELECTOR, 'a.prev.disabled')

    # Locate the parent element
    parent_element = prev_element.find_element(By.XPATH, '..')

    # Find the span element within the parent element
    span_element = parent_element.find_element(By.TAG_NAME, 'span')
    
    # Extract the text from the span element
    pagination_text = span_element.text
    # Split the text to get the value after the '/'
    total_pages = int(pagination_text.split('/')[-1].strip())
    print(f"Total pages: {total_pages}")
except Exception as e:
    print(f"An error occurred: {e}")
    driver.quit()
    raise  # Re-raise the exception to avoid further execution

# Close the driver as we no longer need it
driver.quit()

# Now use requests_html to scrape the product links
session = HTMLSession()
baseurl = "https://shawfloors.com"

productLinks = []
for x in range(1, total_pages + 1):  # Ensure to include the last page
    print(f"Scraping page {x} of {total_pages}")
    response = session.get(f'https://shawfloors.com/flooring/carpet/{x}')
    response.html.render(timeout=60)
    soup = BeautifulSoup(response.html.html, 'html.parser')
    productsList = soup.find_all('div', class_='view-details')
    
    for product in productsList:
        for link in product.find_all('a', href=True):
            productLinks.append(baseurl + link['href'])

print(productLinks)
print(f"Total product links found: {len(productLinks)}")

# Save data to JSON
with open('product_links.json', 'w') as json_file:
    json.dump(productLinks, json_file)

# Save data to Excel
df = pd.DataFrame(productLinks, columns=['Product Link'])
df.to_excel('product_links.xlsx', index=False)

print("Data saved to product_links.json and product_links.xlsx")
