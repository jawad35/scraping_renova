import requests
from bs4 import BeautifulSoup
import os
import json

# URL of the target page
url = "https://www.llflooring.com/p/dream-home-8mm-mountain-trail-oak-wpad-waterproof-laminate-flooring-8.03-in.-wide-x-48-in.-long-10054225.html"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Find the section containing the product-image-zoom-slider div
    zoom_slider = soup.find('div', class_='product-image-zoom-slider')

    # List to store image data for JSON
    image_data = []

    if zoom_slider:
        product_images = zoom_slider.find_all('div', class_='product-image')

        # Create directory to save images
        os.makedirs('llflooringSlides', exist_ok=True)

        for index, product_image in enumerate(product_images):
            img_tag = product_image.find('img')
            if img_tag and 'data-imgurl' in img_tag.attrs:
                img_url = img_tag['data-imgurl']

                # Get the image content
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    img_name = f"image_{index}.jpg"
                    img_path = os.path.join('llflooringSlides', img_name)

                    # Save the image
                    with open(img_path, 'wb') as f:
                        f.write(img_response.content)

                    # Add image data to the list
                    image_data.append({
                        "index": index,
                        "name": img_name,
                        "url": img_url
                    })
                else:
                    print(f"Failed to download image {img_url}")

        # Save image data to a JSON file
        json_path = os.path.join('llflooringSlides', 'images.json')
        with open(json_path, 'w') as json_file:
            json.dump(image_data, json_file, indent=4)

        print("Images and JSON data have been saved.")
    else:
        print("No product-image-zoom-slider div found on the page.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
