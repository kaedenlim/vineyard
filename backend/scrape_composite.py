from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn
from pydantic import BaseModel, HttpUrl
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class OnboardDTO(BaseModel):
    username: str 
    shopee_url: Optional[HttpUrl] = ""  
    lazada_url: Optional[HttpUrl] = ""
    carousell_url: Optional[HttpUrl] = ""

class ScrapeDTO(BaseModel):
    username: str 
    product: str

def scrape_lazada(product_name: str):
    response = httpx.get(f"http://localhost:8001/lazada/scrape?product_name={product_name}")
    return response.json() if response.status_code == 200 else []

def onboard_lazada(url: str):
    response = httpx.get(f"http://localhost:8001/lazada-onboard?url={url}")
    return response.json() if response.status_code == 200 else []

def scrape_carousell(product_name: str):
    response = httpx.get(f"http://localhost:8002/carousell/scrape?product_name={product_name}")
    return response.json() if response.status_code == 200 else []

def onboard_carousell(url: str):
    response = httpx.get(f"http://localhost:8002/carousell-onboard?url={url}")
    return response.json() if response.status_code == 200 else []

@app.get("/scrape/client")
def scrape_client(request: OnboardDTO):
    
    carousell_results = []
    lazada_results = []
    
    if request.lazada_url:
        lazada_results = onboard_lazada(str(request.lazada_url))

    if request.carousell_url:
        carousell_results = onboard_carousell(str(request.carousell_url))

    return {"lazada": lazada_results, "carousell": carousell_results}

@app.get("/scrape/product")
def scrape_product(scrape_request: ScrapeDTO):

    # default is 1 page to scrape (avoid bot detection)
    lazada_results = scrape_lazada(scrape_request.product)
    carousell_results = scrape_carousell(scrape_request.product)

    return {"lazada": lazada_results, "carousell": carousell_results}

if __name__ == "__main__":
    uvicorn.run("scrape_composite:app", host="0.0.0.0", port=8003, reload=True)