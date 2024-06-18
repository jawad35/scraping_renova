import json

def get_details_part(div_element):
    # Find the main div with class 'lh-copy H_oFW'

    if div_element:
        content_dict = {}
        tag_count = {}

        # Traverse through all child tags of the main div
        for child in div_element.descendants:
            if child.name:
                if child.name not in tag_count:
                    tag_count[child.name] = 1
                else:
                    tag_count[child.name] += 1

                # Create a unique key for each tag
                tag_key = f"{child.name}{tag_count[child.name]}"
                content_dict[tag_key] = child.get_text(strip=True)

        # Save the content dictionary to a JSON file
        with open('content.json', 'w') as json_file:
            json.dump(content_dict, json_file, indent=4)
        print("Content has been saved to content.json.")
        return content_dict