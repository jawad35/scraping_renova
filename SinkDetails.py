from selenium import webdriver
from selenium.webdriver.common.by import By
import json
import multiprocessing

# Function to scrape links from a given page
def scrape_page_links(driver, url):
    driver.get(url)  # Load the page
    links = []
    # Find all anchor elements with class "mw5" and get their href attributes
    elements = driver.find_elements(By.CSS_SELECTOR, 'a.mw5')
    for element in elements:
        links.append(element.get_attribute('href'))
    return links

# Function to be called by each process
def process_page(page_num, base_url, queue):
    driver = webdriver.Chrome()  # Initialize Chrome webdriver
    url = f"{base_url}?page={page_num}"
    links = scrape_page_links(driver, url)  # Scrape links from the page
    driver.quit()  # Close the browser
    queue.put(links)  # Put the links into the queue

# Main function to scrape links from multiple pages
def scrape_all_links(base_url, num_pages):
    all_links = []
    processes = []
    queue = multiprocessing.Queue()

    # Start a process for each page
    for page in range(1, num_pages + 1):
        process = multiprocessing.Process(target=process_page, args=(page, base_url, queue))
        processes.append(process)
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()

    # Collect results from the queue
    while not queue.empty():
        all_links.extend(queue.get())

    return all_links

# Main execution
if __name__ == "__main__":
    base_url = "https://www.build.com/undermount-kitchen-sinks/c113813"
    num_pages = 3  # Specify the number of pages to scrape
    links = scrape_all_links(base_url, num_pages)
    
    # Save links to a JSON file
    with open("build.com.json", "w") as json_file:
        json.dump(links, json_file, indent=4)
