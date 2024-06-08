from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Directory where product folders are stored
base_directory = "products"

# Check if the base directory exists, create it if not
if not os.path.exists(base_directory):
    os.makedirs(base_directory)

# Mount the static files directory
app.mount("/products", StaticFiles(directory=base_directory), name="products")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
