from fastapi import FastAPI
from scrapers.lazada import scrape_lazada
from scrapers.carousell import carousell_scraper

app = FastAPI()

@app.post("/scrape/{product_name}")
def scrape(product_name: str):
    # this scrapes for lazada
    lazada_results = scrape_lazada(product_name, 3)

    # compute the average of the listings
    lazada_sum = 0
    lazada_count = 0
    for item in lazada_results:
        lazada_sum += float(item["price"])
        lazada_count += 1
    lazada_sum /= lazada_count
    
    # return all scraped data and the average value
    return {"lazada_results": lazada_results, "lazada_aggregrate_values": lazada_sum}

@app.get("/scrape/{product_name}/carousell")
def scrape_carousell(product_name: str):
    carousell_results = carousell_scraper(product_name)

    # compute the average of the listings
    carousell_sum = 0
    carousell_count = 0
    for item in carousell_results:
        carousell_sum += item["price"]
        carousell_count += 1
    carousell_sum /= carousell_count
    
    # return all scraped data and the average value
    return {"lazada_results": carousell_results, "lazada_aggregrate_values": carousell_sum}
