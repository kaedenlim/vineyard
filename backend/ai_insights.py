from openai import OpenAI
from dotenv import load_dotenv
import os
from typing import List, Dict

# Load environment variables from .env file
load_dotenv()

def generate_product_insights(product_data: Dict) -> str:
    """
    Generates AI insights for a product based on scraped data.
    
    Args:
        product_data (Dict): Dictionary containing product data from various sources
        
    Returns:
        str: Generated insights about the product
    """
    # Get API key from .env file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in .env file")
        
    client = OpenAI(api_key=api_key)
    
    # Prepare the prompt with product data
    prompt = f"""
    Analyze the following product data and provide insights:
    
    Product Name: {product_data['product_name']}
    
    Scraped Results:
    {product_data['scraped_data']}
    
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
                {"role": "system", "content": "You are a product analysis expert providing insights about market prices and trends."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating insights: {str(e)}" 
        