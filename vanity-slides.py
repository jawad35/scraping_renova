import os
import requests
from bs4 import BeautifulSoup

# URL of the page
url = "https://www.build.com/kohler-k-6489/s562806?uid=1740930&searchId=ZvXfD3GDiX"

# Fetch the HTML content from the URL
response = requests.get(url)
html_content = response.text

# Parse the HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Find all div elements with class name "lh-solid"
lh_solid_divs = soup.find_all("div", class_="lh-solid")

# Create a folder to save the images
folder_name = "build-category"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Loop through each lh-solid div
for i, div in enumerate(lh_solid_divs):
    # Find the image tag inside the div
    img_tag = div.find("img")
    if img_tag:
        # Get the src attribute of the image
        img_src = img_tag["src"]
        
        # Download the image
        img_data = requests.get(img_src).content
        with open(os.path.join(folder_name, f'image_{i+1}.jpg'), 'wb') as handler:
            handler.write(img_data)

print(f"Downloaded {i+1} images to the folder '{folder_name}'.")
