from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
import uvicorn
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QuantitativeDTO(BaseModel):
    product_name: str
    scrape_client: bool = False

app = FastAPI()

async def scrape_client_data(client: httpx.AsyncClient, product_name: str) -> dict:
    logger.info(f"Scraping client for product: {product_name}")
    client_request_body = {
        "lazada_url": f"https://dummy.lazada.com/{product_name}",
        "carousell_url": f"https://dummy.carousell.com/{product_name}"
    }
    try:
        response = await client.post("http://localhost:8003/scrape/client", json=client_request_body)
        response_json = response.json()
        logger.info(f"Client scrape succeeded for product: {product_name}")
        return {"results": response_json}
    except httpx.RequestError as e:
        logger.error(f"Client scrape service unavailable: {str(e)}")
        return {"error": f"Client scrape service unavailable: {str(e)}"}
    except ValueError as e:
        logger.error(f"Invalid JSON from scrape client: {str(e)}")
        return {"error": f"Invalid JSON from scrape client: {str(e)}"}

async def scrape_market_data(client: httpx.AsyncClient, product_name: str) -> dict:
    logger.info(f"Scraping market for product: {product_name}")
    product_request_body = {
        "product": product_name
    }
    try:
        response = await client.post("http://localhost:8003/scrape/markets", json=product_request_body)
        response_json = response.json()
        logger.info(f"Market scrape succeeded for product: {product_name}")
        return {"results": response_json}
    except httpx.RequestError as e:
        logger.error(f"Product scrape service unavailable: {str(e)}")
        return {"error": f"Product scrape service unavailable: {str(e)}"}
    except ValueError as e:
        logger.error(f"Invalid JSON from scrape product: {str(e)}")
        return {"error": f"Invalid JSON from scrape product: {str(e)}"}

def format_for_interpretation(data):
    if not data or "scraped_data" not in data:
        return {}
    top_items = sorted(data["scraped_data"], key=lambda x: x.get("page_ranking", float("inf")))[:5]
    return {
        "top_listings": top_items,
        "average_price": data.get("average_price")
    }

async def interpret_data(client: httpx.AsyncClient, product_name: str, results: dict) -> dict:
    logger.info(f"Interpreting data for product: {product_name}")

    interpret_request_body = {
        "product": product_name,
        "lazada_results": format_for_interpretation(results.get("lazada")),
        "carousell_results": format_for_interpretation(results.get("carousell"))
    }
    try:
        response = await client.post("http://localhost:8004/interpret_data", json=interpret_request_body)
        response_json = response.json()
        logger.info(f"Interpretation succeeded for product: {product_name}")
        return response_json
    except httpx.RequestError as e:
        logger.error(f"Interpretation service unavailable: {str(e)}")
        return {"error": f"Interpretation service unavailable: {str(e)}"}
    except ValueError as e:
        logger.error(f"Invalid JSON from interpretation service: {str(e)}")
        return {"error": f"Invalid JSON from interpretation service: {str(e)}"}

@app.post("/quantitative")
async def get_quantitative_analysis(request: QuantitativeDTO):
    logger.info(f"Starting quantitative analysis: product_name={request.product_name}, scrape_client={request.scrape_client}")
    final_response = {}

    async with httpx.AsyncClient(timeout=30) as client:
        # Scrape client data if requested
        if request.scrape_client:
            client_result = await scrape_client_data(client, request.product_name)
            if "results" in client_result:
                final_response["client_scrape_results"] = client_result["results"]
            if "error" in client_result:
                final_response["client_error"] = client_result["error"]

        # Scrape market data
        market_result = await scrape_market_data(client, request.product_name)
        if "results" in market_result:
            final_response["market_scrape_results"] = market_result["results"]
        if "error" in market_result:
            final_response["market_error"] = market_result["error"]

        # Combine results for interpretation
        combined_results = {}
        if "client_scrape_results" in final_response:
            combined_results.update(final_response["client_scrape_results"])
        if "market_scrape_results" in final_response:
            combined_results.update(final_response["market_scrape_results"])

        # Interpret combined results
        interpretation = await interpret_data(client, request.product_name, combined_results)
        final_response["interpretation"] = interpretation

    # Handle total failure
    if request.scrape_client and final_response.get("client_error") and final_response.get("market_error"):
        return JSONResponse(
            status_code=502,
            content={
                "client_error": final_response["client_error"],
                "market_error": final_response["market_error"]
            }
        )

    return {k: v for k, v in final_response.items() if v is not None}

if __name__ == "__main__":
    uvicorn.run("quantitative_composite:app", host="0.0.0.0", port=8005, reload=True)
