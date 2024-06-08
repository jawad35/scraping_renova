from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import json

async def get_type_data(url="https://shawfloors.com/flooring/carpet"):
    # Set up Chrome options to run headlessly
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")

    # Initialize the WebDriver
    driver = webdriver.Chrome(options=chrome_options)

    # Open the webpage
    await driver.get(url)

    # Find all <a> tags within the specified div using By class
    a_tags = driver.find_elements(By.CSS_SELECTOR, "div.filter.filter-TypeName a.sideFilter")

    # Extract href links and span text
    data = []
    for a_tag in a_tags:
        href = a_tag.get_attribute("href")
        span_element = a_tag.find_element(By.CSS_SELECTOR, "span")
        # Check if the span element has text
        span_text = span_element.text if span_element.text else span_element.get_attribute("textContent")
        data.append({"Href": href, "SpanText": span_text})

    # Close the WebDriver
    driver.quit()

    # Return data as JSON
    return json.dumps(data)

# # Example usage:
# url = "https://shawfloors.com/flooring/carpet"
# json_data = get_type_data(url)
# print(json_data)
