from playwright.sync_api import sync_playwright
import re

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )
    page = context.new_page()
    url = 'https://www.build.com/signature-hardware-948461/s1707231?uid=4027533'
    page.goto(url)
    
    # Wait for the page to load
    page.wait_for_load_state('networkidle')

    try:
        # Find the ul element with classes 'ma0' and 'pa0'
        ul_element = page.query_selector('ul.ma0.pa0')

        if not ul_element:
            print("No ul element with classes 'ma0' and 'pa0' found")
            return

        extracted_data = {}
        
        # Find all li elements inside the ul
        li_elements = ul_element.query_selector_all('li')

        for li_element in li_elements:
            # Find the h3 element with class 'tc1-title' inside the li
            h3_element = li_element.query_selector('h3.tc1-title')
            if h3_element:
                section_title = h3_element.inner_text()
                section_key = section_title.lower().replace(' ', '_')
                extracted_data[section_key] = []

                # Find all button elements with class 'qdzeh' inside the li
                button_elements = li_element.query_selector_all('button .qdzeh')
                
                for button_element in button_elements:
                    data_obj = {}

                    # Find the img inside the button
                    img_element = button_element.query_selector('img')
                    if img_element:
                        img_src = img_element.get_attribute('src')
                        match = re.search(r'/([^/]+)-[^-]+\.(?:jpg|jpeg|png|gif)$', img_src)
                        if match:
                            extracted_text = match.group(1)
                            data_obj['img'] = img_src
                            data_obj['model'] = extracted_text

                    # Find the tc2-title inside the button
                    title_element = button_element.query_selector('.tc2-title')
                    if title_element:
                        title_text = title_element.inner_text()
                        data_obj['title'] = title_text

                    # Find the price inside the button
                    price_element = button_element.query_selector('.theme-grey-medium')
                    if price_element:
                        price_text = price_element.inner_text()
                        data_obj['price'] = price_text

                    if data_obj:
                        extracted_data[section_key].append(data_obj)

        print("Extracted data:", extracted_data)

    except Exception as e:
        print("An error occurred:", e)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
