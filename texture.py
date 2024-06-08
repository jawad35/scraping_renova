import requests
from bs4 import BeautifulSoup
import json

async def get_texture(url="https://shawfloors.com/flooring/carpet"):
    response = await requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find all list items inside the ul element
        list_items = soup.select("div.filter-VisualName ul li")

        # Initialize a list to store the data
        data = []

        # Loop through each list item and extract the href link and span text
        for item in list_items:
            a_tag = item.find("a", class_="sideFilter")
            href = a_tag['href']
            span_text = a_tag.find("span").text.strip()
            data.append({"href": href, "text": span_text})

        # Return the data as JSON
        return json.dumps(data, indent=4)
    else:
        return "Failed to retrieve the webpage."

# # Example usage:
# url = "https://shawfloors.com/flooring/carpet"
# json_data = get_texture(url)
# print(json_data)
