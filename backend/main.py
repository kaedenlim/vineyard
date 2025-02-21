from fastapi import FastAPI
from scrapers.lazada import scrape_lazada

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