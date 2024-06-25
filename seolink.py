from playwright.sync_api import sync_playwright
import re
import time

def extract_images_from_style(page):
    # Extract background images from style tags and inline styles
    style_images = []
    style_elements = page.query_selector_all('style')
    for style in style_elements:
        style_content = style.inner_html()
        style_images.extend(re.findall(r'url\(([^)]+)\)', style_content))
    inline_elements = page.query_selector_all('[style]')
    for elem in inline_elements:
        style_content = elem.get_attribute('style')
        style_images.extend(re.findall(r'url\(([^)]+)\)', style_content))
    return style_images

def extract_images_from_scripts(page):
    # Extract images from script tags
    script_images = []
    script_elements = page.query_selector_all('script')
    for script in script_elements:
        script_content = script.inner_html()
        script_images.extend(re.findall(r'(https?://\S+\.(?:jpg|jpeg|png))', script_content))
    return script_images

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context(
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    )
    page = context.new_page()
    url = 'https://www.build.com/signature-hardware-948461/s1707231?uid=4027533'
    page.goto(url)
    
    # Wait for the page to load and JavaScript to execute
    page.wait_for_load_state('networkidle')
    time.sleep(5)  # Increase sleep time to ensure elements are loaded

    try:
        # Get the entire page content
        page_content = page.content()
        print(page_content)
        # Search for "339" text in the page content
        found_text = re.search(r'\b339\b', page_content)

        if found_text:
            print("Text '339' found on the page.")
        else:
            print("Text '339' not found on the page.")

        # Find all image elements
        image_elements = page.query_selector_all('img')
        image_urls = [img.get_attribute('src') for img in image_elements]

        # Find background images in style tags and inline styles
        style_images = extract_images_from_style(page)
        image_urls.extend(style_images)

        # Find images in script tags
        script_images = extract_images_from_scripts(page)
        image_urls.extend(script_images)

        # Filter image URLs containing the specified part
        filter_part = "h_55/product/"
        filtered_image_urls = [url for url in image_urls if filter_part in url]

        # Extract the text between the last and second-last hyphens and store in array
        extracted_texts = []
        for img_url in filtered_image_urls:
            match = re.search(r'/([^/]+)-[^-]+\.(?:jpg|jpeg|png|gif)$', img_url)
            if match:
                extracted_text = match.group(1)
                extracted_texts.append(extracted_text)
                print(f"Found image URL: {img_url}")
                print(f"Extracted text: {extracted_text}")

        # Print the extracted texts
        print("Extracted texts:", extracted_texts)

    except Exception as e:
        print("An error occurred:", e)

    browser.close()

with sync_playwright() as playwright:
    run(playwright)
