import json
from bs4 import BeautifulSoup

def get_details_part(div_element):
    if div_element:
        content_dict = {}
        tag_count = {}

        # Traverse through all child tags of the main div
        for child in div_element.descendants:
            if child.name:
                if child.name == 'ul':
                    ul_key = f"ul{tag_count.get('ul', 0) + 1}"
                    content_dict[ul_key] = []
                    for li in child.find_all('li'):
                        content_dict[ul_key].append(li.get_text(strip=True))
                    tag_count['ul'] = tag_count.get('ul', 0) + 1
                else:
                    if child.name not in tag_count:
                        tag_count[child.name] = 1
                    else:
                        tag_count[child.name] += 1

                    # Create a unique key for each tag
                    tag_key = f"{child.name}{tag_count[child.name]}"
                    if child.name != 'li' and child.name != 'ul':
                        content_dict[tag_key] = child.get_text(strip=True)

        # Save the content dictionary to a JSON file
        with open('content.json', 'w') as json_file:
            json.dump(content_dict, json_file, indent=4)
        print("Content has been saved to content.json.")
        return content_dict