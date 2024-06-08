from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json

# Set up the Selenium WebDriver
driver = webdriver.Chrome()  # Ensure you have the Chrome WebDriver installed

# Navigate to the webpage
url = "https://www.build.com/kohler-k-6489/s562806?uid=1740930&searchId=ZvXfD3GDiX"
driver.get(url)

# Wait for the tables to be present
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
print(json.dumps(all_tables_data, indent=4))

# Save the extracted table data to a JSON file
with open('tables_data.json', 'w') as json_file:
    json.dump(all_tables_data, json_file, indent=4)

# Close the WebDriver
driver.quit()
