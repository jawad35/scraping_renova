import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def extract_table_data(url, accordion_header_ids):
    # Set Chrome options for headless mode
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # Initialize the WebDriver with Chrome options
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Open the webpage
        driver.get(url)

        # Wait for the cookie consent button to be clickable and then dismiss it
        try:
            WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler"))).click()
        except:
            pass  # If the element is not clickable or not found, do nothing

        # Function to click on accordion headers by their IDs
        def click_accordion_header(header_id):
            try:
                header = driver.find_element(By.ID, header_id)
                header.click()
                time.sleep(1)  # Pause to allow the section to expand
            except Exception as e:
                print(f"Could not click header {header_id}: {e}")

        extracted_data = {"description": {}}

        # Click each accordion header and extract data
        for header_id in accordion_header_ids:
            click_accordion_header(header_id)
            table = driver.find_element(By.CSS_SELECTOR, '#full-product-details-specs .specs .table.table-striped')

            # Extract key-value pairs from the table
            data = {}
            rows = table.find_elements(By.TAG_NAME, 'tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) == 2:
                    key = cells[0].text.strip()
                    value = cells[1].text.strip()
                    data[key] = value

            extracted_data["description"][header_id] = data

        return extracted_data
    finally:
        # Close the WebDriver
        driver.quit()

# Example usage
url = 'https://shawfloors.com/flooring/carpet/details/nature-within-5e278/washed-linen'
accordion_header_ids = ['headingOne']
data = extract_table_data(url, accordion_header_ids)

# Save data in JSON format
with open('products-description.json', 'w') as json_file:
    json.dump(data, json_file)

print("Data saved successfully in 'products-description.json'")
