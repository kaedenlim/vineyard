from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from scrapers.lazada import scrape_lazada, onboard_lazada
from scrapers.carousell import scrape_carousell, onboard_carousell
from models.dto import ScrapeDTO, OnboardDTO
from typing import List
from ai_insights import generate_product_insights


app = FastAPI()

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

    # Merge product data and persist it to user
    merged_results = []
    for carousell_result in carousell_results:
        merged_results.append({
            "title": carousell_result.title,
            "price": carousell_result.price,
            "image": carousell_result.image,
            "link": carousell_result.link,
            "site": "Carousell"
        })
    for lazada_result in lazada_results:
        merged_results.append({
            "title": lazada_result.title,
            "price": lazada_result.price,
            "image": lazada_result.image,
            "link": lazada_result.link,
            "site": "Lazada"
        })
    for shopee_result in shopee_results:
        merged_results.append({
            "title": shopee_result.title,
            "price": shopee_result.price,
            "image": shopee_result.image,
            "link": shopee_result.link,
            "site": "Shopee"
        })

    
    return {
        "shopee": shopee_results,
        "lazada": lazada_results,
        "carousell": carousell_results
    }

@app.post("/scrape")
def scrape(scrape_request: ScrapeDTO):
    # this scrapes for lazada, default is 1 page to scrape (avoid bot detection)
    # lazada_results = scrape_lazada(scrape_request.product)
    carousell_results = scrape_carousell(scrape_request.product)
    
    insights_data = {
        # "lazada_average_price": lazada_results.average_price,
        "carousell_average_price": carousell_results.average_price,
        # "lazada_top_listings": lazada_results.top_listings,
        "carousell_top_listings": carousell_results.top_listings
    }
    
    insights = generate_product_insights({
        "product_name": scrape_request.product,
        "insights_data": insights_data
    })

    return { "carousell_results": carousell_results, "insights": insights}
    # return {"lazada_results": lazada_results,  "carousell_results": carousell_results, "insights_data": insights_data}

@app.post("/insights")
def get_insights(request: Request):
    # Get the scraped data from the request body
    data = request.json()

    # Generate AI insights using the provided scraped data
    insights = generate_product_insights({
        "product_name": data['product_name'],
        "insights_data": data['insights_data']
    })
    print(insights)
    
    return {
        "insights": insights
    }
