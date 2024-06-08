import json
import requests
from urllib.parse import urlparse

def fetch_data_from_api(style_number, uid, proxies=None):
    url = f"https://specifications.shawinc.com/api/v1/Specifications/{style_number}"
    params = {
        'uid': uid,
    }
    
    response = requests.get(url, params=params, proxies=proxies)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to retrieve data. Status code: {response.status_code}")
        return None

def get_color_number(color_name, colors):
    """
    Function to get the color number for a given color name.

    Args:
    color_name (str): The name of the color to search for.
    colors (list): The list of colors data.

    Returns:
    str: A string combining the color name and color number, or None if not found.
    """
    for color in colors:
        if color['colorName'].lower() == color_name.lower():
            return f"{color['colorName']} {color['colorNumber']}"
    return None

# Example usage:
if __name__ == "__main__":
    url = "https://shawfloors.com/flooring/carpet/details/rustique-vibe-ccs72/purity"
    segments = urlparse(url).path.split('/')  # Split the URL path by slashes
    last_segment = segments[-2]  # Get the second-to-last segment
    style_number = last_segment.split('-')[-1]  # Get the text after the last dash
    print(style_number)
    uid = 'E2908A32-403E-42DA-81B7-394FFD478BC9'
    
    # Define your proxy
    proxies = {
       
    }
    
    # Fetch data from the API with the proxy
    data = fetch_data_from_api(style_number, uid, proxies)

    if data:
        colors = data.get('colors')
        
        table_data = {
            "category": data.get("inventoryType"),
            "t1": {
                "style": f"{data.get('sellingStyleNumber')} {data.get('sellingStyleName')}",
                "color": get_color_number("serene still", colors),
                "flooringType": data.get("inventoryType"),
                "collection": data.get("collection"),
                "fiber": data.get("fiber"),
                "width": data.get("productSize").get("width").get("imperial").get("displayValue"),
                "styleType": data.get("construction"),
                "faceWeight": data.get("tuftedWeight").get("imperial").get("displayValue"),
                "backing": data.get("secondaryBacking"),
                "CountryOfOrigin": data.get("countryOfOrigin")
            }
        }

        print(table_data)
    else:
        print("Failed to fetch API response.")
