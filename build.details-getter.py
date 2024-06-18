# import requests
# from bs4 import BeautifulSoup
# import json

# # URL of the target page
# url = "https://www.llflooring.com/p/dream-home-xd-10mm-and-pad-delaware-bay-driftwood-laminate-flooring-7.6-in.-wide-x-54.45-in.-long-10050045.html"  # Replace with your actual URL

# # Send a GET request to the URL
# response = requests.get(url)

# # Check if the request was successful
# if response.status_code == 200:
#     # Parse the HTML content using BeautifulSoup
#     soup = BeautifulSoup(response.content, 'html.parser')

#     # Find the main div with class 'lh-copy H_oFW'
#     main_div = soup.find('div', class_='description-and-detail')

#     if main_div:
#         content_dict = {}
#         tag_count = {}

#         # Traverse through all child tags of the main div
#         for child in main_div.descendants:
#             if child.name:
#                 if child.name not in tag_count:
#                     tag_count[child.name] = 1
#                 else:
#                     tag_count[child.name] += 1

#                 # Create a unique key for each tag
#                 tag_key = f"{child.name}{tag_count[child.name]}"
#                 content_dict[tag_key] = child.get_text(strip=True)

#         # Save the content dictionary to a JSON file
#         with open('content.json', 'w') as json_file:
#             json.dump(content_dict, json_file, indent=4)

#         print("Content has been saved to content.json.")
#     else:
#         print("Main div with class 'lh-copy H_oFW' not found on the page.")
# else:
#     print(f"Failed to retrieve the page. Status code: {response.status_code}")
