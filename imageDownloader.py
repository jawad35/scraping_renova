import os
import requests
from urllib.parse import urlparse

def download_image(image_url, save_directory='images'):
    try:
        # Parse the URL to get the image name
        parsed_url = urlparse(image_url)
        image_name = os.path.basename(parsed_url.path)

        # Ensure the save directory exists
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Set the headers to mimic a browser request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # Send a GET request to the image URL
        response = requests.get(image_url, headers=headers, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            image_path = os.path.join(save_directory, image_name)
            with open(image_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
            print(f"Image successfully downloaded: {image_path}")
        else:
            print(f"Failed to retrieve the image. Status code: {response.status_code}")

    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
image_url = 'https://shawfloors.widen.net/content/tgxa1fhxc4/web/5E278_00103_main.jpg?quality=85&crop=true&w=60&h=60'
download_image(image_url)
