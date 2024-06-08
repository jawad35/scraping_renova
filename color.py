import requests
from bs4 import BeautifulSoup
import json

def get_color(url="https://shawfloors.com/flooring/carpet"):
    # Send a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.content, "html.parser")

        # Find all list items inside the ul element
        list_items = soup.select("div.filter-ColorFamilyDesc ul li")

        # Initialize a list to store the data
        data = []

        # Loop through each list item and extract the href attribute and color name
        for item in list_items:
            a_tag = item.find("a", class_="sideFilter")
            href = a_tag["href"]
            color_name = a_tag.find("span", class_="filterText").text.strip()
            data.append({"href": href, "colorName": color_name})

        # Return data as JSON
        return json.dumps(data) 

    else:
        return "Failed to retrieve the webpage."

# # Example usage:
# url = "https://shawfloors.com/flooring/carpet"
# json_data = get_color(url)
