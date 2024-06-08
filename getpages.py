import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

url = "https://shawfloors.com/flooring/carpet"
session = HTMLSession()
response = session.get(url)

# Increase the timeout value (in seconds)
response.html.render(timeout=300)  # Increase the timeout to 30 seconds

# Parse the HTML content
soup = BeautifulSoup(response.html.html, 'html.parser')

# Find all <p> elements with class "selling-color-name"
products = soup.find_all('div', class_='view-details')

# description_div = soup.find('div', class_='description')

# Extract the value of the data-shaw-id attribute
# data_shaw_id = description_div['data-shaw-id']

# Split the attribute value at the underscore character
# data_before_underscore = data_shaw_id.split('_')[0]

# Iterate over the found elements and print their text
for product in products:
    print(product.find('a'))
