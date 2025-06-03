from fastapi import FastAPI
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
import os
from typing import Dict, List
import logging
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

load_dotenv()

class LazadaCarousellResults(BaseModel):
    average_price: float
    top_listings: List

class InterpretationRequest(BaseModel):
    product: str
    lazada_results: LazadaCarousellResults
    carousell_results: LazadaCarousellResults

def generate_interpretation(product_data: Dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
        
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Interpret the following product data and provide insights:
    
    Product Name: {product_data['product_name']}
    
    Scraped Results:
    {product_data['interpretation_data']}
    
    Please provide:
    1. Price analysis and comparison
    2. Market trends and observations
    3. Potential value for money assessment
    4. Any notable patterns or interpretation
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a product analysis expert providing insights about market trends to facilitate market entry. Be concise and give actionable recommendations that are less than 3 sentences in total."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        logger.warning(f"Error generating interpretation: {str(e)}")
        return f"Error generating interpretation: {str(e)}" 
        
@app.post("/interpret_data")
def interpret_data(data: InterpretationRequest):
    logger.info("Interpret endpoint was hit")
    # Get the scraped data from the request body
    interpretation_data = {
        "lazada_average_price": data.lazada_results.average_price,
        "carousell_average_price": data.carousell_results.average_price,
        "lazada_top_listings": data.lazada_results.top_listings,
        "carousell_top_listings": data.carousell_results.top_listings
    }
    
    interpretation = generate_interpretation({
        "product_name": data.product,
        "interpretation_data": interpretation_data
    })
    logger.info("Successfully generated interpretation")
    
    return interpretation

if __name__ == "__main__":
    uvicorn.run("interpret_service:app", host="0.0.0.0", port=8004, reload=True)