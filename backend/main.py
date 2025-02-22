from fastapi import FastAPI
from scrapers.lazada import scrape_lazada
from scrapers.carousell import scrape_carousell

app = FastAPI()

@app.get("/scrape/{product_name}")
def scrape(product_name: str):
    # this scrapes for lazada, the 1 is for the no of pages to scrape (avoid bot detection)
    lazada_results = scrape_lazada(product_name, 1)
    carousell_results = scrape_carousell(product_name)
    
    # return all scraped data and the average value
    return {"lazada_results": lazada_results, "carousell_results": carousell_results}
