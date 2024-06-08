import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession

url = "https://shawfloors.com/flooring/carpet/details/inspired-design-cc81b/ocean-villa"
session = HTMLSession()
response = session.get(url)

# Increase the timeout value (in seconds)
response.html.render(timeout=300)  # Increase the timeout to 30 seconds

# Parse the HTML content
soup = BeautifulSoup(response.html.html, 'html.parser')

# Find the main image
image_element = soup.find('img', class_='main-image')

# Check if the image element exists
if image_element:
    # Extract the source URL of the main image
    image_source = image_element.get('src')
    print("Main image source URL:", image_source)
else:
    print("Main image not found.")
