from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn
from pydantic import BaseModel, HttpUrl
from typing import Optional
import logging
import httpx
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

class ScrapeClientDTO(BaseModel):
    lazada_url: Optional[HttpUrl] = None
    carousell_url: Optional[HttpUrl] = None

class ScrapeProductDTO(BaseModel):
    product: str

async def scrape_lazada_market(product_name: str):
    url = f"http://localhost:8001/lazada/scrape_market?product_name={product_name}"
    logger.info(f"Scraping Lazada market with URL: {url}")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Successfully scraped Lazada market")
                    return {"results": data}
                except ValueError:
                    logger.error("Invalid JSON in response from Lazada market")
                    return {"error": "Invalid JSON in response"}
            logger.error(f"Request to Lazada market failed with status code {response.status_code}")
            return {"error": f"Request failed with status code {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request error occurred for Lazada market: {str(e)}")
            return {"error": f"Request error occurred: {str(e)}"}

async def scrape_lazada_client(url: str):
    outgoing_url = f"http://localhost:8001/lazada/scrape_client?profile_url={url}"
    logger.info(f"Scraping Lazada client with URL: {outgoing_url}")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(outgoing_url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Successfully scraped Lazada client")
                    return {"results": data}
                except ValueError:
                    logger.error("Invalid JSON in response from Lazada client")
                    return {"error": "Invalid JSON in response"}
            logger.error(f"Request to Lazada client failed with status code {response.status_code}")
            return {"error": f"Request failed with status code {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request error occurred for Lazada client: {str(e)}")
            return {"error": f"Request error occurred: {str(e)}"}

async def scrape_carousell_market(product_name: str):
    url = f"http://localhost:8002/carousell/scrape_market?product_name={product_name}"
    logger.info(f"Scraping Carousell market with URL: {url}")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Successfully scraped Carousell market")
                    return {"results": data}
                except ValueError:
                    logger.error("Invalid JSON in response from Carousell market")
                    return {"error": "Invalid JSON in response"}
            logger.error(f"Request to Carousell market failed with status code {response.status_code}")
            return {"error": f"Request failed with status code {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request error occurred for Carousell market: {str(e)}")
            return {"error": f"Request error occurred: {str(e)}"}

async def scrape_carousell_client(url: str):
    outgoing_url = f"http://localhost:8002/carousell/scrape_client?profile_url={url}"
    logger.info(f"Scraping Carousell client with URL: {outgoing_url}")
    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.get(outgoing_url)
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Successfully scraped Carousell client")
                    return {"results": data}
                except ValueError:
                    logger.error("Invalid JSON in response from Carousell client")
                    return {"error": "Invalid JSON in response"}
            logger.error(f"Request to Carousell client failed with status code {response.status_code}")
            return {"error": f"Request failed with status code {response.status_code}"}
        except httpx.RequestError as e:
            logger.error(f"Request error occurred for Carousell client: {str(e)}")
            return {"error": f"Request error occurred: {str(e)}"}

@app.post("/scrape/client")
async def scrape_client(request: ScrapeClientDTO):
    errors = {}
    result = {}

    if request.lazada_url:
        lazada_results = await scrape_lazada_client(request.lazada_url)
        if lazada_results.get("error"):
            errors["lazada_error"] = lazada_results["error"]
        else:
            result["lazada"] = lazada_results.get("results")

    if request.carousell_url:
        carousell_results = await scrape_carousell_client(request.carousell_url)
        if carousell_results.get("error"):
            errors["carousell_error"] = carousell_results["error"]
        else:
            result["carousell"] = carousell_results.get("results")

    if ("lazada_error" in errors) and ("carousell_error" in errors):
        return JSONResponse(status_code=502, content=errors)

    result.update(errors)
    return result

@app.post("/scrape/markets")
async def scrape_markets(request: ScrapeProductDTO):
    lazada_task = scrape_lazada_market(request.product)
    carousell_task = scrape_carousell_market(request.product)
    lazada_results, carousell_results = await asyncio.gather(lazada_task, carousell_task)

    errors = {}
    result = {}

    if lazada_results.get("error"):
        errors["lazada_error"] = lazada_results["error"]
    else:
        result["lazada"] = lazada_results.get("results")

    if carousell_results.get("error"):
        errors["carousell_error"] = carousell_results["error"]
    else:
        result["carousell"] = carousell_results.get("results")

    if ("lazada_error" in errors) and ("carousell_error" in errors):
        return JSONResponse(status_code=502, content=errors)

    result.update(errors)
    return result

if __name__ == "__main__":
    uvicorn.run("scrape_comp:app", host="0.0.0.0", port=8003, reload=True)