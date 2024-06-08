import requests
from bs4 import BeautifulSoup
import json

url = "https://shawfloors.com/flooring/carpet"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all list items inside the ul element which have both 'a' and 'div' tags
    list_items = soup.select("div.filter-CollectionDesc ul li:has(a):has(div)")

    # Initialize a list to store the data
    data = []

    # Loop through each filtered list item and extract the href attribute and span text
    for item in list_items:
        a_tag = item.find("a", class_="sideFilter")
        href = a_tag['href']
        span_text = a_tag.find("span").text.strip()
        data.append({"href": href, "text": span_text})

    # Save the data to a JSON file
    with open("collection_data.json", "w") as json_file:
        json.dump(data, json_file, indent=4)

    print("Data saved to collection_data.json")
else:
    print("Failed to retrieve the webpage.")
