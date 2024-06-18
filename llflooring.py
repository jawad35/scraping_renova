import requests
from bs4 import BeautifulSoup

# URL of the target page
url = "https://www.llflooring.com/p/dream-home-8mm-mountain-trail-oak-wpad-waterproof-laminate-flooring-8.03-in.-wide-x-48-in.-long-10054225.html"

# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the section containing the specifications
    spec_section = soup.find('div', class_='spec-section')
    
    # Find all list items within the spec section
    if spec_section:
        spec_list = spec_section.find('ul', class_='spec-container')
        items = spec_list.find_all('li') if spec_list else []

        # Loop through the list items and extract the details
        for item in items:
            spec_name_div = item.find('div', class_='spec-name')
            spec_details_div = item.find('div', class_='spec-details')
            
            # Extract the text from span inside spec-name and spec-details
            spec_name = spec_name_div.find('span').text.strip() if spec_name_div.find('span') else spec_name_div.text.strip()
            spec_details = spec_details_div.find('span').text.strip() if spec_details_div.find('span') else spec_details_div.text.strip()
            
            print(f"{spec_name}: {spec_details}")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
