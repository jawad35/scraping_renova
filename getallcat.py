from selenium import webdriver

# Initialize the WebDriver (assuming you have downloaded the appropriate driver for your browser)
driver = webdriver.Chrome()  # Change this to the appropriate WebDriver for your browser

# Open the webpage
driver.get("https://shawfloors.com/flooring/carpet/details/inspired-design-cc81b/ocean-villa")

try:
    # Find all elements with class "grid-swatch-link"
    swatch_elements = driver.find_elements("class","grid-swatch-link")

    # Iterate over each swatch element
    for swatch_element in swatch_elements:
        # Find the element with class "item-color-name" inside the swatch element
        item_color_name_element = swatch_element.find_element("class","item-color-name")
        # Extract the text from the item color name element
        item_color_name = item_color_name_element.text

        # Find the element with class "center-cropped" inside the swatch element
        background_image_element = swatch_element.find_element("class","center-cropped")
        # Extract the value of the "style" attribute which contains the background image URL
        background_image_url = background_image_element.get_attribute("style")
        # Extract the URL from the style attribute
        background_image_url = background_image_url.split("url('")[1].split("')")[0]

        # Print the extracted item color name and background image URL
        print("Item Color Name:", item_color_name)
        print("Background Image URL:", background_image_url)
        print()

finally:
    # Close the browser window
    driver.quit()
