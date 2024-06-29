import os
import requests
from bs4 import BeautifulSoup
import urllib.parse

def fetch_image(url, class_name, category_name, model_name, variant_name):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the image tag by class name
        img_tag = soup.find('div', class_=class_name).find('img')
        
        if img_tag:
            # Get the image source URL
            image_url = img_tag.get('src')
            
            # Download the image
            download_image(image_url, category_name, model_name, variant_name)
        else:
            print("Image tag not found.")
    else:
        print(f"Failed to retrieve page: {response.status_code}")

def download_image(image_url, category_name, model_name, variant_name):
    # Parse the image URL to get the filename
    parsed_url = urllib.parse.urlparse(image_url)
    filename = os.path.basename(parsed_url.path)
    
    # Create directory structure if not exists
    folder_path = os.path.join('products', category_name, model_name, variant_name)
    os.makedirs(folder_path, exist_ok=True)
    
    # Download the image and save it to the specified folder
    image_path = os.path.join(folder_path, filename)
    
    # Check if the image already exists
    if not os.path.exists(image_path):
        # Download the image
        with open(image_path, 'wb') as img_file:
            img_file.write(requests.get(image_url).content)
        print(f"Image downloaded successfully: {image_path}")
    else:
        print(f"Image already exists: {image_path}")

# Example usage with direct parameters
fetch_image(
    "https://www.build.com/signature-hardware-948455/s1707230?uid=4027494",
    "transform-component-module_content__FBWxo",
    "sinks",
    "model-xyz",
    "variants"
)
