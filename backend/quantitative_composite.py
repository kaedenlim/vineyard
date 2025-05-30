from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import httpx
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/quantitative")
async def get_quantitative_analysis(request: Request):
    data = await request.json()
    product_name = data.get("product_name")
    ref_client = data.get("reference_client", False)

    results = {}

    async with httpx.AsyncClient() as client:
        if ref_client:
            client_request_body = {
                "lazada_url": f"https://dummy.lazada.com/{product_name}",
                "carousell_url": f"https://dummy.carousell.com/{product_name}",
                "username": "test_user"
            }
            client_response = await client.post("http://localhost:8003/scrape/client", json=client_request_body)
            results["client"] = client_response.json() if client_response.status_code == 200 else {}

        product_request_body = {
            "product": product_name,
            "username": "test_user"
        }
        product_response = await client.post("http://localhost:8003/scrape/product", json=product_request_body)
        results["product"] = product_response.json() if product_response.status_code == 200 else {}

    return results

if __name__ == "__main__":
    uvicorn.run("quantitative_composite:app", host="0.0.0.0", port=8005, reload=True)
