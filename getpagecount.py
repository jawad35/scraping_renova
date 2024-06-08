from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize the WebDriver (specify the path to your WebDriver if it's not in your PATH)
driver = webdriver.Chrome()  # Use the appropriate WebDriver for your browser

# Open the webpage
driver.get('https://shawfloors.com/flooring/carpet')  # Replace with your actual webpage URL

# Wait for the page to load completely
time.sleep(3)  # Adjust the sleep time if necessary

# Locate the span element after the 'prev disabled' link
try:
    # Find the element with class 'prev disabled'
    prev_element = driver.find_element(By.CSS_SELECTOR, 'a.prev.disabled')

    # Locate the parent element
    parent_element = prev_element.find_element(By.XPATH, '..')

    # Find the span element within the parent element
    span_element = parent_element.find_element(By.TAG_NAME, 'span')
    
    # Extract the text from the span element
    pagination_text = span_element.text
    # Split the text to get the value after the '/'
    total_pages = pagination_text.split('/')[-1].strip()
    print(f"Total pages: {total_pages}")
except Exception as e:
    print(f"An error occurred: {e}")

# Close the driver
driver.quit()
