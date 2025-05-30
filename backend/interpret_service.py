from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
import uvicorn
import os
from typing import Dict

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

def generate_product_insights(product_data: Dict) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
        
    client = OpenAI(api_key=api_key)

    prompt = f"""
    Analyze the following product data and provide insights:
    
    Product Name: {product_data['product_name']}
    
    Scraped Results:
    {product_data['insights_data']}
    
    Please provide:
    1. Price analysis and comparison
    2. Market trends and observations
    3. Potential value for money assessment
    4. Any notable patterns or insights
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a product analysis expert providing insights about market prices and trends. Be consise and give actionable insights on the price and title to use that are less than 3 sentences in total."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating insights: {str(e)}" 
        
@app.get("/interpret")
def get_insights(data: Request):
    # Get the scraped data from the request body
    insights_data = {
        "lazada_average_price": data.lazada_results.average_price,
        "carousell_average_price": data.carousell_results.average_price,
        "lazada_top_listings": data.lazada_results.top_listings,
        "carousell_top_listings": data.carousell_results.top_listings
    }
    
    insights = generate_product_insights({
        "product_name": data.product,
        "insights_data": insights_data
    })
    
    return {
        "insights": insights
    }

if __name__ == "__main__":
    uvicorn.run("interpret_service:app", host="0.0.0.0", port=8003, reload=True)