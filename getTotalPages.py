from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

async def get_total_pages():
    try:
        # Initialize Chrome WebDriver with headless option
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)
        driver = webdriver.Chrome()
        # Open the webpage
        driver.get('https://shawfloors.com/flooring/carpet')  # Use the base URL

        # # Find the element with class 'prev disabled'
        prev_element = driver.find_element(By.CSS_SELECTOR, 'a.prev.disabled')

        # # Locate the parent element
        parent_element = prev_element.find_element(By.XPATH, '..')

        # # Find the span element within the parent element
        span_element = parent_element.find_element(By.TAG_NAME, 'span')

        # # Extract the text from the span element
        pagination_text = span_element.text
        total_pages = int(pagination_text.split('/')[-1].strip())
        return total_pages
    except Exception as e:
        print(f"An error occurred: {e}")
        raise  # Re-raise the exception to avoid further execution
