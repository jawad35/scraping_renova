import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json

async def get_color(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                list_items = soup.select("div.filter-ColorFamilyDesc ul li")
                data = []
                for item in list_items:
                    a_tag = item.find("a", class_="sideFilter")
                    href = a_tag["href"]
                    color_name = a_tag.find("span", class_="filterText").text.strip()
                    data.append({"href": href, "colorName": color_name})
                return json.dumps(data)
            else:
                return "Failed to retrieve the webpage."

async def get_width(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                list_items = soup.select("div.filter-WidthName ul li")
                data = []
                for item in list_items:
                    a_tag = item.find("a", class_="sideFilter")
                    href = a_tag["href"]
                    width_name = a_tag.find("span").text.strip()
                    data.append({"href": href, "widthName": width_name})
                return json.dumps(data)
            else:
                return "Failed to retrieve the webpage."

async def get_texture(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                list_items = soup.select("div.filter-TextureName ul li")
                data = []
                for item in list_items:
                    a_tag = item.find("a", class_="sideFilter")
                    href = a_tag["href"]
                    texture_name = a_tag.find("span").text.strip()
                    data.append({"href": href, "textureName": texture_name})
                return json.dumps(data)
            else:
                return "Failed to retrieve the webpage."

async def get_type_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "html.parser")
                list_items = soup.select("div.filter-TypeName ul li")
                data = []
                for item in list_items:
                    a_tag = item.find("a", class_="sideFilter")
                    href = a_tag["href"]
                    type_name = a_tag.find("span").text.strip()
                    data.append({"href": href, "typeName": type_name})
                return json.dumps(data)
            else:
                return "Failed to retrieve the webpage."

async def main():
    url = "https://shawfloors.com/flooring/carpet"
    tasks = [
        get_color(url),
        get_texture(url),
    ]
    results = await asyncio.gather(*tasks)
    print(results)
    return results

# Run the event loop
asyncio.run(main())
