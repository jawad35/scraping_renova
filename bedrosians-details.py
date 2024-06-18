import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

def extract_table_data(url):
    options = Options()
    options.headless = True  # Run in headless mode, comment this line to see browser interaction
    driver = webdriver.Chrome( options=options)
    
    try:
        driver.get(url)
        time.sleep(5)  # Adjust the wait time as needed to ensure page content is fully loaded
        
        data = {}
        table_count = 1
        
        rows = driver.find_elements(By.CSS_SELECTOR, '.application-chart tbody tr')
        for row in rows:
            key = row.find_element(By.CLASS_NAME, 'ng-binding').text.strip()
            values = {}
            
            cells = row.find_elements(By.TAG_NAME, 'td')[1:]  # Skip the first cell which contains the key
            for col_index, cell in enumerate(cells, start=1):
                spans = cell.find_elements(By.CLASS_NAME, 'spanWrapper.ng-scope')
                if spans:
                    values[f'column{col_index}'] = True
                else:
                    values[f'column{col_index}'] = False
            
            data[f't{table_count}'] = {key: values}
            table_count += 1
        
        return data
    
    finally:
        driver.quit()

def save_as_json(data, filename='table_data.json'):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    url = 'https://www.bedrosians.com/en/product/detail/slabs/?itemNo=100006857&queryid=9664195b02a88db87c146aef3785ef4d'
    try:
        table_data = extract_table_data(url)
        if table_data:
            save_as_json(table_data)
            print("Table data extracted and saved successfully.")
        else:
            print("No table data extracted.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
