from fastapi import FastAPI, APIRouter, Query
import uvicorn
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta
import random
import re
from dataclasses import dataclass
from typing import List

@dataclass
class Product:
    title: str
    price: float
    discount: float
    image: str
    link: str
    page_ranking: int

@dataclass
class ScrapeResult:
    scraped_data: List[Product]
    timestamp: str
    average_price: float
    top_listings: List[Product]

router = APIRouter()

def extract_price(price_str):
    """Extracts numerical value from a currency string."""
    cleaned = re.sub(r"[^\d.]", "", price_str)
    return float(cleaned) # if "." in cleaned else int(cleaned)

@router.get("/scrape", response_model=ScrapeResult)
def scrape_carousell(product_name: str = Query(..., description="Product name to search")):
    
    scraped_data_with_timestamp = {}

    with sync_playwright() as p:

        # Facilitate keeping track of average price
        total_items = 0
        total_price = 0.0

        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")
        page = context.new_page()
        page.goto("https://www.carousell.sg/")

        BASE_URL = BASE_URL = "https://www.carousell.sg"

        # Locate the input field and fill it
        search_input = page.locator("input[placeholder='Search for an item']")
        search_input.fill(product_name)
        search_input.press("Enter")
        
        page.wait_for_timeout(random.randint(2000, 4000))  
        page.reload() # avoid popup 
        
        page.wait_for_selector("div[data-testid^='listing-card-']", timeout=10000)

        MAX_PAGES = 1
        for _ in range(MAX_PAGES):
            show_more_button = page.locator("button", has_text="Show more results")
            if show_more_button.count() == 0:
                break
            show_more_button.click()
            # Wait for new content to load. Adjust this timeout or use a smarter wait if needed.
            page.wait_for_timeout(random.randint(2000, 3200))

        listings = page.locator("div[data-testid^='listing-card-']").all()
        
        if (len(listings) == 0):
            listings = page.locator("//div[contains(@data-testid, 'listing-card-')]").all()

        scraped_data = []

        if (len(listings) == 0):
            print("No listings found")
            browser.close()

        top_listings = []
        top_listings_count = 10;

        for listing in listings:
            try:
                # Extract seller username
                # username = listing.locator("[data-testid='listing-card-text-seller-name']").text_content()

                # Extract time (since no unique `data-testid`, use relative positioning)
                # time_element = listing.locator("p.D_pK").first  # First paragraph with relevant class
                # time = time_element.text_content() if time_element.is_visible() else "N/A"

                # Extract product name
                product_title = listing.locator("p[style*='--max-line']").text_content()
                #listing.locator("div:first-child a:nth-of-type(2) p:first-child")

                # Extract price (from `title` attribute)
                price_pre = listing.locator("div:first-child a:nth-of-type(2) div:nth-of-type(2) p:first-child").get_attribute("title")
                price = 0
                if price_pre != "" and price_pre != '':
                    price = extract_price(price_pre)

                discount = 0
                discount_element = listing.locator("div:first-child a:nth-of-type(2) div:nth-of-type(2) span")
                if discount_element.count() > 0:
                    discount = 1 - (price/extract_price(discount_element.get_attribute("title")))

                # Extract image url
                image = listing.locator("div:first-child a:nth-of-type(2) div:first-child div:has(img) img").get_attribute("src")

                relative_link = listing.locator("div:first-child a:nth-of-type(2)").last.get_attribute("href")

                url = BASE_URL + relative_link if relative_link else "N/A"

                product = Product(
                    title=product_title,
                    price=price,
                    discount=discount,
                    image=image,
                    link=url,
                    page_ranking=total_items + 1
                )
                # Save data
                scraped_data.append(product)

                if top_listings_count > 0:
                    top_listings.append(product)
                    top_listings_count -= 1

                total_items += 1
                total_price += price

            except Exception as e:
                print(f"Error extracting a listing: {e}")

        browser.close()

        # Get average price for the product
        average_price = total_price / total_items

        # Define Singapore timezone (UTC+8)
        sgt_timezone = timezone(timedelta(hours=8))

        # Get current time in Singapore Time (ISO format)
        current_time_sgt = datetime.now(sgt_timezone).isoformat() + "Z"

        carousell = ScrapeResult(
            scraped_data=scraped_data,
            timestamp=current_time_sgt,
            average_price=average_price,
            top_listings=top_listings
        )

        return carousell
    
    
@router.get("/scrapeclient")
def scrape_carousell_client(profile_url: str = Query(..., description="Profile URL")):
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.110 Safari/537.36")
        page = context.new_page()
        page.goto(profile_url)

        page.wait_for_timeout(random.randint(2000, 4000))  
        # page.reload() # avoid popup 
        
        page.wait_for_selector("div[data-testid^='listing-card-']", timeout=10000)

        while True:
            show_more_button = page.locator("button", has_text="View more")
            if show_more_button.count() == 0:
                break
            show_more_button.click()
            # Wait for new content to load. Adjust this timeout or use a smarter wait if needed.
            page.wait_for_timeout(random.randint(2000, 3200))

        listings = page.locator("div[data-testid^='listing-card-']").all()
        
        if (len(listings) == 0):
            listings = page.locator("//div[contains(@data-testid, 'listing-card-')]").all()

        scraped_data = []

        if (len(listings) == 0):
            print("No listings found")
            browser.close()

        for listing in listings:
            try:
                # Extract product status
                product_status_element = listing.locator("div:first-child a:first-child div:first-child p:first-child")
                if product_status_element.count() > 0 and product_status_element.text_content() != "Buyer Protection":
                    print("this product is 'SOLD' or product_status is 'RESERVED'")
                    continue

                # Extract product name
                product_title = listing.locator("p[style*='--max-line']").text_content()

                relative_link = listing.locator("div:first-child a:first-child").last.get_attribute("href")
        
                # Extract price (from `title` attribute)
                price = extract_price(listing.locator("div:first-child a:first-child div:nth-of-type(2) p:first-child").get_attribute("title"))

                # Extract image url
                image = listing.locator("div:first-child a:first-child div:first-child div:has(img) img").get_attribute("src")

                url = "https://carousell.sg" + relative_link if relative_link else "N/A"

                # Save data
                scraped_data.append({
                    "title": product_title,
                    "price": price,
                    "image": image,
                    "link": url,
                })

            except Exception as e:
                print(f"Error extracting a listing: {e}")

        browser.close()

        return scraped_data
    
    
# Create a FastAPI app and include the router
app = FastAPI()
app.include_router(router, prefix="/carousell")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("carousell:app", host="0.0.0.0", port=8002, reload=True)