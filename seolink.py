from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# URL of the webpage
url = "https://www.build.com/signature-hardware-948461/s1707231?uid=4027533"

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')  # Run in headless mode
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')

# Set up the Chrome driver using webdriver-manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Open the webpage
driver.get(url)

try:
    # Wait for the elements with class 'pr2' to be present
    WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pr2')))
    
    # Find all elements with class 'pr2'
    elements_with_class_pr2 = driver.find_elements(By.CLASS_NAME, 'pr2')
    
    # Extract the 'src' attribute from each image and print it
    if elements_with_class_pr2:
        for element in elements_with_class_pr2:
            print(element.get_attribute('src'))
    else:
        print("No images with class 'pr2' found.")
finally:
    # Quit the driver
    driver.quit()
