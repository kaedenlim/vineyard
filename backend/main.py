from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from scrapers.lazada import scrape_lazada
from scrapers.carousell import scrape_carousell, onboard_carousell
from dto.onboard_dto import OnboardDTO
from typing import List

app = FastAPI(root_path="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/onboard")
def onboard(request: OnboardDTO):
    carousell_results = []
    lazada_results = []
    shopee_results = []
    
    if request.carousell_url:
        carousell_url = request.carousell_url
        carousell_results = onboard_carousell(str(carousell_url))
    

    return {"status": "success", "carousell_results": carousell_results}

@app.get("/scrape/{product_name}")
def scrape(product_name: str):
    # this scrapes for lazada, the 1 is for the no of pages to scrape (avoid bot detection)
    lazada_results = scrape_lazada(product_name, 1)
    carousell_results = scrape_carousell(product_name)
    
    # return all scraped data and the average value
    return {"lazada_results": lazada_results, "carousell_results": carousell_results}
