import json
import requests
from urllib.parse import urlparse
import time

def fetch_data_from_api(style_number, uid):
    url = f"https://specifications.shawinc.com/api/v1/Specifications/{style_number}"
    params = {'uid': uid}
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=30)
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None

def get_color_number(color_name, colors):
    for color in colors:
        if color['colorName'].lower() == color_name.lower():
            return f"{color['colorName']} {color['colorNumber']}"
    return None

if __name__ == "__main__":
    url = "https://shawfloors.com/flooring/carpet/details/attainable-e9965/blizzard"
    segments = urlparse(url).path.split('/')
    last_segment = segments[-2]
    style_number = last_segment.split('-')[-1]
    uid = 'E2908A32-403E-42DA-81B7-394FFD478BC9'
    
    # Number of requests to make
    num_requests = 10
    successful_results = 0
    
    for i in range(1, num_requests + 1):
        data = fetch_data_from_api(style_number, uid)
        if data is not None:
            successful_results += 1
            print(f"Result {i}:")
            print(data)
        else:
            print(f"Failed to fetch data for result {i}")
        
        # Add a short delay between requests to avoid overwhelming the server
        time.sleep(0.5)  # Adjust the delay as needed

    print(f"Total successful results: {successful_results}")
