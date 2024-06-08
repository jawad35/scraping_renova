from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def verify_collapse_status(url):
    # Set up the WebDriver
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        # Load the webpage
        driver.get(url)
        # Execute JavaScript to click on all elements with class 'fa-plus'
        script = """
        var plusElements = document.querySelectorAll('.fa-plus');
        plusElements.forEach(function(element) {
            element.click();
            // Wait for 3 seconds
            setTimeout(function() {
                // Check if the corresponding collapse element is expanded
                var collapseElement = element.closest('.card-header').nextElementSibling;
                if (collapseElement.classList.contains('show')) {
                    console.log("Collapse has been expanded.");
                } else {
                    console.error("Collapse has not been expanded.");
                }
            }, 3000);
        });
        """
        driver.execute_script(script)

        print("Verification of collapse status completed.")
        
        # Wait for 3 seconds after completing the verification
        time.sleep(10)

        print("Script execution completed.")

        # You can perform additional actions or scraping here
        
    finally:
        # Close the WebDriver
        driver.quit()

# Example usage
url = "https://shawfloors.com/flooring/carpet/details/nature-within-5e278/washed-linen"
verify_collapse_status(url)
