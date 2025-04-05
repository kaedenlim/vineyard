import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scrapers.lazada import scrape_lazada, onboard_lazada
from scrapers.carousell import scrape_carousell, onboard_carousell
from models.dto import ScrapeDTO, OnboardDTO
from typing import List
from ai_insights import generate_product_insights

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
    
    if request.lazada_url:
        lazada_results = onboard_lazada(str(request.lazada_url))

    if request.carousell_url:
        carousell_results = onboard_carousell(str(request.carousell_url))

    return {
        "shopee": shopee_results,
        "lazada": lazada_results,
        "carousell": carousell_results
    }

@app.post("/scrape")
def scrape(scrape_request: ScrapeDTO):
    # this scrapes for lazada, default is 1 page to scrape (avoid bot detection)
    lazada_results = scrape_lazada(scrape_request.product)
    carousell_results = scrape_carousell(scrape_request.product)
    
    # return all scraped data and the average value
    return {"lazada_results": lazada_results, "carousell_results": carousell_results}

@app.post("/insights/{product_name}")
async def get_insights(product_name: str, request: Request):
    # Get the scraped data from the request body
    data = await request.json()
    scraped_data = data['all_scraped_data']
    print(scraped_data)
    # Generate AI insights using the provided scraped data
    insights = generate_product_insights({
        "product_name": product_name,
        "scraped_data": scraped_data
    })
    print(insights)
    
    return {
        "insights": insights
    }
