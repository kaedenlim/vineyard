from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scrapers.lazada import scrape_lazada
from scrapers.carousell import scrape_carousell
from ai_insights import generate_product_insights

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/scrape/{product_name}")
def scrape(product_name: str):
    # this scrapes for lazada, the 1 is for the no of pages to scrape (avoid bot detection)
    lazada_results = scrape_lazada(product_name, 1)
    print(lazada_results)
    carousell_results = scrape_carousell(product_name)
    print(carousell_results)
    # return all scraped data and the average value
    return {"lazada_results": lazada_results, "carousell_results": carousell_results}

@app.get("/insights/{product_name}")
def get_insights(product_name: str):
    # First get the product data
    product_data = {
        "product_name": product_name,
        "lazada_results": scrape_lazada(product_name, 1),
        "carousell_results": scrape_carousell(product_name)
    }
    
    # Generate AI insights
    insights = generate_product_insights(product_data)
    print(insights)
    
    return {
        "product_data": product_data,
        "insights": insights
    }
