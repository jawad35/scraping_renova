from bs4 import BeautifulSoup
from requests_html import HTMLSession

url = "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/grounded-gray"
session = HTMLSession()
response = session.get(url)

# Increase the timeout value (in seconds)
response.html.render(timeout=300)  # Increase the timeout to 30 seconds

# Parse the HTML content
soup = BeautifulSoup(response.html.html, 'html.parser')

# Find the swatch item
swatch_item = soup.find('div', class_='grid-swatch-link swatch-item')

if swatch_item:
    # Extract color name
    color_name = swatch_item.find('div', class_='item-color-name').text.strip()

    # Extract background image URL
    style_attribute = swatch_item.find('div', class_='center-cropped swatchThumb')['style']
    background_image_url = style_attribute.split("('")[1].split("')")[0]

    print("Color Name:", color_name)
    print("Background Image URL:", background_image_url)
else:
    print("Swatch item not found.")
