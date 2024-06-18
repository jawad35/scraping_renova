import os
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_p_tag_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting content from <p> tag
        rating_summary_div = soup.find('div', class_='bv-rating-summary')
        if not rating_summary_div:
            raise Exception("Div with class 'bv-rating-summary' not found")
        
        p_tag = rating_summary_div.find_previous_sibling('p')
        if not p_tag:
            raise Exception("Previous sibling p tag not found")
        
        p_tag_content = p_tag.get_text(strip=True)
                # Example parsing logic, adapt as needed
        div_tag = soup.find('div', class_='col-xs-12 col-sm-10 col-sm-offset-2')
        if not div_tag:
            raise Exception("Div with unique combination of classes not found")

        h1_tag = div_tag.find('h1')
        if not h1_tag:
            raise Exception("h1 tag inside the div not found")

        smooth_star_text = ''.join(h1_tag.find_all(text=True, recursive=False)).strip()
        # Extracting all p tags with class "product-option__label"
        dimensions = soup.find_all('p', class_='product-option__label')
        
        # Collecting text content from each p tag
        p_dimensions = [p_tag.get_text(strip=True).replace('\\', '') for p_tag in dimensions]
        return {
            'dimensions': p_dimensions,
            'brand': smooth_star_text,
            'p_tag_content': p_tag_content,
        }
    except Exception as e:
        return {'url': url, 'error': f"Error extracting p tag content: {e}"}

def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extracting image URL
        image_div = soup.find('div', class_='main-detail-image__fullsize')
        if not image_div:
            raise Exception("Div with class 'main-detail-image__fullsize' not found")

        image_tag = image_div.find('img')
        if not image_tag or not image_tag.has_attr('src'):
            raise Exception("Image tag inside div 'main-detail-image__fullsize' not found")

        image_url = image_tag['src']
        if not image_url.startswith('http'):
            image_url = f"https://www.thermatru.com{image_url}"  # Replace with actual domain

        # Downloading the image
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Saving the image
        output_dir = 'thematurimages'
        image_path = os.path.join(output_dir, os.path.basename(image_url))
        os.makedirs(output_dir, exist_ok=True)
        with open(image_path, 'wb') as file:
            file.write(image_response.content)

        return {
            'image_path': image_path
        }
    except Exception as e:
        return {'url': url, 'error': f"Error downloading image: {e}"}

def process_url(url):
    try:
        p_tag_result = extract_p_tag_content(url)
        if 'error' in p_tag_result:
            return p_tag_result
        
        image_result = download_image(url)
        if 'error' in image_result:
            return image_result
        
        return {
            'dimensions':p_tag_result['dimensions'],
            'brand':p_tag_result['brand'],
            'p_tag_content': p_tag_result['p_tag_content'],
            'image_path': image_result['image_path']
        }
    except Exception as e:
        return {'url': url, 'error': f"Error processing URL: {e}"}

def process_urls_concurrently(urls):
    results = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        # Submit tasks for processing each URL
        futures = {executor.submit(process_url, url): url for url in urls}

        for future in as_completed(futures):
            result = future.result()
            results.append(result)

    return results

# Example usage:
urls = [
    "https://www.thermatru.com/explore-products/door-style/S3500LXE",
    "https://www.thermatru.com/explore-products/door-style/S83600L",
    "https://www.thermatru.com/explore-products/door-style/S3400LXK",
    "https://www.thermatru.com/explore-products/door-style/S3500LXR"
    # Add more URLs as needed
]

# Process the URLs concurrently and get combined results
combined_results = process_urls_concurrently(urls)

print(combined_results)

# # Output the combined results
# for result in combined_results:
#     if 'error' in result:
#         print(f"URL: {result['url']}, Error: {result['error']}")
#     else:
#         print(f"URL: {result['url']}")
#         print(f"P Tag Content: {result['p_tag_content']}")
#         print(f"Image downloaded and saved to {result['image_path']}")
