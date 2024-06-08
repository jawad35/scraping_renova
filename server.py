from typing import List
from fastapi import FastAPI
import os

# from bs4 import BeautifulSoup
# from requests_html import AsyncHTMLSession
from getAllProductsLinks import scrape_product_links_shawfloors
# from getTotalPages import get_total_pages
# from getDetailsAllPages import scrape_webpage
# from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from color import get_color
from hardwood import hardwood_scrape_urls
from vinyl import vinyl_scrape_urls

# from width import get_width
# from texture import get_texture
# from Type import get_type_data
# import collections
from descriptionMaker import generate_rewrite
from seolink import generate_seo_link
from getProFullDetail import scrape_urls
from all_build_p_details import scrape_product_links_build

# from getThumbSliderImages import thumb_slider_images
app = FastAPI()
from fastapi.staticfiles import StaticFiles
# Directory where product folders are stored
base_directory = "products"

# Check if the base directory exists, create it if not
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

# Mount the static files directory
app.mount("/products", StaticFiles(directory=base_directory), name="products")
app.mount("/images", StaticFiles(directory="images"), name="images")
# app.mount("/slides", StaticFiles(directory="slides"), name="slides")

# async def scrape_color_info(url):
#     session = AsyncHTMLSession()
#     response = await session.get(url)

#     # Increase the timeout value (in seconds)
#     await response.html.arender(timeout=300)  # Increase the timeout to 100 seconds

#     # Parse the HTML content
#     soup = BeautifulSoup(response.html.html, 'html.parser')

#     # Find the swatch item
#     swatch_item = soup.find('div', class_='grid-swatch-link swatch-item')

#     if swatch_item:
#         # Extract color name
#         color_name = swatch_item.find('div', class_='item-color-name').text.strip()

#         # Extract background image URL
#         style_attribute = swatch_item.find('div', class_='center-cropped swatchThumb')['style']
#         background_image_url = style_attribute.split("('")[1].split("')")[0]

#         return {"color_name": color_name, "background_image_url": background_image_url}
#     else:
#         return {"error": "Swatch item not found."}

# @app.get("/totalpages")
# async def read_root():
#     total_pages = await get_total_pages()
#     return {"total_pages": total_pages}

# @app.get("/")
# async def read_root():
#     productLinks = await scrape_product_links()
#     return {"Hello": productLinks}

# @app.get("/plinks/{page_no}")
# async def read_item(page_no:int):
#     productLinks = await scrape_product_links(page_no)
#     return {"Product_links": productLinks}


# Define a Pydantic model to represent the request body schema
class URLRequest(BaseModel):
    urls: List[str]

@app.post("/getcarpet")
async def get_products_details(request: URLRequest):
    product = scrape_urls(request.urls)
    print(product)
    # with ThreadPoolExecutor() as executor:
    #     executor.map(scrape_webpage, request.urls)
    return product

class URLsRequest(BaseModel):
    no: int
    url:str

class URLsRequest(BaseModel):
    no: int
    category:str

@app.post("/page-products-links")
def get_products_details(request: URLsRequest):
    try:
        if request.category[:-1] == "carpets":
            product_links = scrape_product_links_shawfloors(request.no, request.category[:-1])
        elif request.category[:-1] == "hardwoods":
            product_links = scrape_product_links_shawfloors(request.no, request.category[:-1])
        elif request.category[:-1] == "vinyls":
            product_links = scrape_product_links_shawfloors(request.no, request.category[:-1])
        elif request.category[:-1] == "tiles":
            product_links = scrape_product_links_build(request.urls, request.folder)
        elif request.category[:-1] == "sinks":
            product_links = scrape_product_links_build(request.urls, request.folder)
        elif request.category[:-1] == "faucets":
            product_links = scrape_product_links_build(request.urls, request.folder)
        elif request.category[:-1] == "vanities":
            product_links = scrape_product_links_build(request.urls, request.folder)
        elif request.category[:-1] == "doors":
            product_links = scrape_product_links_shawfloors(request.no, request.category[:-1])   
        elif request.category[:-1] == "laminates":
            product_links = scrape_product_links_shawfloors(request.no, request.category[:-1])   
        elif request.category[:-1] == "countertops":
            product_links = scrape_product_links_shawfloors(request.no, request.category[:-1])             
        print(product_links)
        return {"product_links": product_links}
    except Exception as e:
        print(e)
        # raise HTTPException(status_code=500, detail=str(e)) 

@app.post("/gethardwood")
async def get_hardwood_details(request: URLRequest):
    urls = [
        # "https://shawfloors.com/flooring/carpet/details/cabana-life-(t)-e9958/walking-trail",
        # "https://shawfloors.com/flooring/carpet/details/tonal-comfort-blue-5e658/sun-kissed",
        # "https://shawfloors.com/flooring/vinyl/details/paragon-hdnatural-bevel-3038v/oriel",
        "https://shawfloors.com/flooring/hardwood/details/landmark-sliced-oak-sw747/gateway",
        # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/grounded-gray",
        # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/sunbaked",
        # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/natural-beauty"
        # Add more URLs as needed
    ]
    product = hardwood_scrape_urls(urls)
    print(product)
    # with ThreadPoolExecutor() as executor:
    #     executor.map(scrape_webpage, request.urls)
    return product


@app.post("/getvinyl")
async def get_vinyl_details(request: URLRequest):
    urls = [
        # "https://shawfloors.com/flooring/carpet/details/cabana-life-(t)-e9958/walking-trail",
        # "https://shawfloors.com/flooring/carpet/details/tonal-comfort-blue-5e658/sun-kissed",
        "https://shawfloors.com/flooring/vinyl/details/paragon-hdnatural-bevel-3038v/oriel",
        # "https://shawfloors.com/flooring/hardwood/details/landmark-sliced-oak-sw747/gateway",
        # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/grounded-gray",
        # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/sunbaked",
        # "https://shawfloors.com/flooring/carpet/details/fine-structure-cc69b/natural-beauty"
        # Add more URLs as needed
    ]
    product = vinyl_scrape_urls(urls)
    # with ThreadPoolExecutor() as executor:
    #     executor.map(scrape_webpage, request.urls)
    return product

# class ThumbSliderRequest(BaseModel):
#     url: str

# @app.post("/thumb_slider")
# def get_slider_images(request: ThumbSliderRequest):
#     thumb_slider_images(request.url)
#     return {"sucess": "All slider images Scraped!"}

# @app.post("/filters")
# async def read_item(request: ThumbSliderRequest):
#     url = request.url

#     # Call all the asynchronous functions concurrently
#     color_data = await get_color(url)
#     width_data = await get_width(url)

#     return {
#         "colors": color_data,
#         "width": width_data,
#     }

# @app.get("/colors")
# def read_root():
#     colors = get_color()
#     return {"colors": colors}

# @app.get("/textures")
# def read_root():
#     textures = get_texture()
#     return {"textures": textures}


# @app.get("/types")
# def read_root():
#     types = get_type_data()
#     return {"types": types}

# @app.get("/width")
# def read_root():
#     width = get_width()
#     return {"width": width}

# @app.get("/collections")
# def read_root():
#     width = collections()
#     return {"width": width}


# class DescriptionRequest(BaseModel):
#     parameters:object

# @app.post("/gendescription")
# def get_desc(request: DescriptionRequest):
#     desc = generate_rewrite(request.parameters,'')
#     return {"description": desc}

# class SeoLinkRequest(BaseModel):
#     url:str

# @app.post("/seolink")
# def get_seo_link(request: SeoLinkRequest):
#     url = generate_seo_link(request.url,'')
#     return {"url": url}


# build site

# class URLRequest(BaseModel):
#     urls: List[str]
#     folder: str

# @app.post("/b_product_links")
# async def get_products_details(request: URLRequest):
#     product = scrape_product_links_build(request.urls, request.folder)
#     # with ThreadPoolExecutor() as executor:
#     #     executor.map(scrape_webpage, request.urls)
#     return product