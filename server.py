from typing import List
from fastapi import FastAPI
import os

# from bs4 import BeautifulSoup
# from requests_html import AsyncHTMLSession
from getAllProductsLinks import scrape_product_links
from build_links_scraper import scrape_product_links_build

# from getTotalPages import get_total_pages
# from getDetailsAllPages import scrape_webpage
# from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
# from color import get_color
from hardwood import hardwood_scrape_urls
from vinyl import vinyl_scrape_urls

# from width import get_width
# from texture import get_texture
# from Type import get_type_data
# import collections
# from descriptionMaker import generate_rewrite
# from seolink import generate_seo_link
from get_shawfloor_products_details import get_shawfloor_products_data
from get_build_products_details import get_build_products_data
from get_buildersInterior_products_details import get_buildersInteriors_products_data
from buildersinteriors_links_scraper import scrape_product_links_buiders_interiors
from llflooring_links_scraper import scrape_product_links_llflooring
from get_llflooring_products_details import get_llflooring_products_data
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
# app.mount("/images", StaticFiles(directory="images"), name="images")
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
    product = get_shawfloor_products_data(request.urls)
    print(product)
    # with ThreadPoolExecutor() as executor:
    #     executor.map(scrape_webpage, request.urls)
    return product

class URLsRequest(BaseModel):
    no: int
    url:str

class URLsRequest(BaseModel):
    min: int
    max: int
    category:str

@app.post("/page-products-links")
async def get_products_links(request: URLsRequest):
    try:
        if request.category == "carpets":
            product_links = scrape_product_links(request.min, request.max, request.category[:-1])
        elif request.category == "hardwoods":
            product_links = scrape_product_links(request.min, request.max, request.category[:-1])
        elif request.category == "vinyls":
            product_links = scrape_product_links(request.min, request.max, request.category[:-1])
        elif request.category == "tiles":
            product_links = await scrape_product_links_build("https://www.build.com/shop-all-vanities/c113572?page=", request.min, request.max)
        elif request.category == "sinks":
            product_links = await scrape_product_links_build("https://www.build.com/undermount-kitchen-sinks/c113813?page=", request.min, request.max)
        elif request.category == "faucets":
            product_links = await scrape_product_links_build("https://www.build.com/all-kitchen-faucets/c108514?page=", request.min, request.max)
        elif request.category == "vanities":
            product_links = await scrape_product_links_build("https://www.build.com/shop-all-vanities/c113572?page=", request.min, request.max)
        elif request.category == "doors":
            product_links = await scrape_product_links_build("https://www.build.com/all-doors-main/c82041374?page=", request.min, request.max)
        elif request.category == "laminates":
            product_links = await scrape_product_links_llflooring('https://www.llflooring.com/c/laminate-flooring/', request.min, request.max)   
        elif request.category == "countertops":
            product_links = await scrape_product_links_buiders_interiors('https://www.buildersinteriors.com/shop/slab/?bi=1&really_curr_tax=49-product_cat',request.min, request.max)             
        return {"product_links": product_links}
    except Exception as e:
        print(e)
        # raise HTTPException(status_code=500, detail=str(e)) 

class URLRequest(BaseModel):
    urls: List[str]
    category: str

@app.post("/fetch-products")
async def get_products_details(request: URLRequest):
    try:
        if request.category == "carpets":
            products_data = get_shawfloor_products_data(request.urls, request.category)
        elif request.category == "hardwoods":
            products_data = get_shawfloor_products_data(request.urls, request.category)
        elif request.category == "vinyls":
            products_data = get_shawfloor_products_data(request.urls, request.category)
        elif request.category == "tiles":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "sinks":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "faucets":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "vanities":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "doors":
            products_data = get_build_products_data(request.urls, request.category)
        elif request.category == "laminates":
            products_data = await get_llflooring_products_data(request.urls)   
        elif request.category == "countertops":
            products_data = get_buildersInteriors_products_data(request.urls)             
        return products_data
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


class DescriptionRequest(BaseModel):
    parameters:object

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

class URLRequest(BaseModel):
    urls: List[str]
    category: str

# @app.post("/fetch-products")
# async def get_products_details(request: URLRequest):
#     print(request)
#     product = get_build_products_data(request.urls, request.category)
#     # with ThreadPoolExecutor() as executor:
#     #     executor.map(scrape_webpage, request.urls)
#     return product