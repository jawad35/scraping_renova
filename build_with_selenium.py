import requests
from bs4 import BeautifulSoup
import openai
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os

def download_image(url, folder_path, image_name):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(folder_path, image_name), 'wb') as file:
                file.write(response.content)
            print(f"Downloaded {image_name}")
        else:
            print(f"Failed to download {image_name}")
    except Exception as e:
        print(f"Error downloading {image_name}: {e}")

def generate_rewrite(description, api_key):
    try:
        client = openai(api_key=api_key)
        completion = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=f"Please rewrite it'{description}'",
            max_tokens=100,
            temperature=0
        )
        return completion.choices[0].text.strip()
    except Exception as e:
        print(f"Error generating rewrite: {e}")
        return description

# Your OpenAI API key

# URL to scrape
url = "https://www.build.com/kraus-khu100-32/s577429?uid=1755668&searchId=q7dM1gRSKB"

# Scrape the data using BeautifulSoup
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')


# Find the span tag with the specific attribute and class name
price_span = soup.find('span', {'data-automation': 'price', 'class': 'lh-copy'})

# Extract and print the text of the span tag
if price_span:
    print(price_span.text.strip())
else:
    print("Price span tag not found")
# Extract the relevant data
# lh_copy_div = soup.find('div', class_='lh-copy H_oFW')
# paragraphs = lh_copy_div.find_all('p')
# lists = lh_copy_div.find_all('ul')

original_text = ""

# Combine all text from paragraphs and lists
# for p in paragraphs:
#     original_text += p.get_text() + "\n\n"

# for ul in lists:
#     for li in ul.find_all('li'):
#         original_text += "- " + li.get_text() + "\n"

# Find the element with the specified class name
target_element = soup.find(class_='lh-copy H_oFW')

# Get all tags within the target element
# all_tags_with_text = target_element.find_all()
# print(all_tags_with_text)
# # Rewrite the text using OpenAI
# rewritten_text = generate_rewrite(all_tags_with_text, api_key)

# # Print the rewritten text (or save it as needed)
# print("Original Text:\n", original_text)
# print("\nRewritten Text:\n", rewritten_text)

# # Save the rewritten text to a file (optional)
# with open('rewritten_description.txt', 'w') as file:
#     file.write(rewritten_text)

# Set up the Selenium WebDriver
driver = webdriver.Chrome()  # Ensure you have the Chrome WebDriver installed

# Navigate to the webpage
driver.get(url)

# Wait for the page to load completely
WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "w-100.w-third-ns")))

# Get the page source and parse it with BeautifulSoup
soup = BeautifulSoup(driver.page_source, 'html.parser')

# Find all divs with the class "w-100 w-third-ns"
table_divs = soup.find_all('div', class_='w-100 w-third-ns')

# Initialize a dictionary to hold the tables data
all_tables_data = {}
table_count = 1

# Iterate through each div with class "w-100 w-third-ns"
for table_div in table_divs:
    # Find the nested divs with class "db-ns"
    nested_divs = table_div.find_all('div', class_='db-ns')
    
    for nested_div in nested_divs:
        table_data = {}
        # Find all tbody elements within the nested div
        tbodies = nested_div.find_all('tbody')
        
        for tbody in tbodies:
            tbody_data = {}
            rows = tbody.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:
                    key = cols[0].get_text(strip=True)
                    value = cols[1].get_text(strip=True)
                    tbody_data[key] = value
            # Assign data to the current table key
            if tbody_data:
                table_data[f't{table_count}'] = tbody_data
                table_count += 1
        # Merge current table data into the main dictionary
        if table_data:
            all_tables_data.update(table_data)

# Print the extracted table data (optional)
# print(json.dumps(all_tables_data, indent=4))

# Save the extracted table data to a JSON file
with open('tables_data.json', 'w') as json_file:
    json.dump(all_tables_data, json_file, indent=4)

# Directory to save images
image_folder = 'categories_build'
os.makedirs(image_folder, exist_ok=True)

# Function to download images from given div class names
def download_images_from_divs(div_class):
    image_divs = soup.find_all('div', class_=div_class)
    for index, div in enumerate(image_divs):
        img_tag = div.find('img')
        if img_tag and 'src' in img_tag.attrs:
            img_url = img_tag['src']
            img_name = f'{div_class}_image_{index+1}.jpg'
            download_image(img_url, image_folder, img_name)

# Download images from divs with class "transform-component-module_content__FBWxo"
# download_images_from_divs('transform-component-module_content__FBWxo')

# Download images from divs with class "bw1 br2"
# download_images_from_divs('br2')

# Close the WebDriver
driver.quit()
