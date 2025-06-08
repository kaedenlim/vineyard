import logging
from fastapi import FastAPI, Query
import uvicorn
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta
import random
import re
from dataclasses import dataclass
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Product:
    Title: str
    Price: float
    Discount: float
    Image: str
    Link: str
    Ranking: int

@dataclass
class ScrapeResult:
    scraped_data: List[Product]
    timestamp: str
    average_price: float

def extract_price(price_str):
    """Extracts numerical value from a currency string."""
    cleaned = re.sub(r"[^\d.]", "", price_str)
    return float(cleaned) # if "." in cleaned else int(cleaned)

app = FastAPI()

@app.get("/carousell/scrape_market", response_model=ScrapeResult)
def scrape_carousell(product_name: str = Query(..., description="Product name to search")):
    logger.info(f"Route /carousell/scrape_market called with product_name={product_name}")

    with sync_playwright() as p:

        # Facilitate keeping track of average price
        total_items = 0
        total_price = 0.0

        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
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
            logger.warning("No listings found")
            browser.close()

        for listing in listings:
            try:
                # Extract product name
                product_title = listing.locator("p[style*='--max-line']").text_content()
                
                price_locator = listing.locator("div:first-child a:nth-of-type(2) div:nth-of-type(2) p:first-child")
                if price_locator.count() == 0:
                    continue
                price_pre = price_locator.get_attribute("title")
                if not price_pre:
                    continue
                price = 0
                if price_pre != "" and price_pre != '':
                    price = extract_price(price_pre)

                discount = 0
                discount_element = listing.locator("div:first-child a:nth-of-type(2) div:nth-of-type(2) span")
                if discount_element.count() > 0:
                    discount_title = discount_element.get_attribute("title")
                    if discount_title:
                        discount = 1 - (price/extract_price(discount_title))

                image_locator = listing.locator("div:first-child a:nth-of-type(2) div:first-child div:has(img) img")
                if image_locator.count() == 0:
                    continue
                image = image_locator.get_attribute("src")
                if not image:
                    continue

                relative_link_locator = listing.locator("div:first-child a:nth-of-type(2)").last
                if relative_link_locator.count() == 0:
                    continue
                relative_link = relative_link_locator.get_attribute("href")
                if not relative_link:
                    continue

                Link = BASE_URL + relative_link if relative_link else "N/A"

                product = Product(
                    Title=product_title,
                    Price=price,
                    Discount=discount,
                    Image=image,
                    Link=Link,
                    Ranking=total_items + 1
                )
                # Save data
                scraped_data.append(product)

                total_items += 1
                total_price += price

                # Stop collecting products once 10 have been scraped
                if total_items >= 10:
                    break

            except Exception as e:
                logger.warning(f"Error extracting a listing: {e}")

        browser.close()

        logger.info(f"Scraped {len(scraped_data)} products from market search")

        # Get average price for the product
        average_price = total_price / total_items if total_items > 0 else 0.0

        # Define Singapore timezone (UTC+8)
        sgt_timezone = timezone(timedelta(hours=8))

        # Get current time in Singapore Time (ISO format)
        current_time_sgt = datetime.now(sgt_timezone).isoformat() + "Z"

        carousell = ScrapeResult(
            scraped_data=scraped_data,
            timestamp=current_time_sgt,
            average_price=average_price
        )

        return carousell
    
    
@app.get("/carousell/scrape_client")
def scrape_carousell_client(profile_url: str = Query(..., description="Profile URL")):
    logger.info(f"Route /carousell/scrape_client called with profile_url={profile_url}")
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
            logger.warning("No listings found")
            browser.close()

        for listing in listings:
            try:
                # Extract product status
                product_status_element = listing.locator("div:first-child a:first-child div:first-child p:first-child")
                if product_status_element.count() > 0:
                    product_status_text = product_status_element.text_content()
                    if product_status_text != "Buyer Protection":
                        logger.warning("This product is 'SOLD' or product_status is 'RESERVED'")
                        continue
                else:
                    # If product status element missing, skip listing
                    continue

                # Extract product name
                product_title_locator = listing.locator("p[style*='--max-line']")
                if product_title_locator.count() == 0:
                    continue
                product_title = product_title_locator.text_content()

                relative_link_locator = listing.locator("div:first-child a:first-child").last
                if relative_link_locator.count() == 0:
                    continue
                relative_link = relative_link_locator.get_attribute("href")
                if not relative_link:
                    continue
        
                # Extract price (from `title` attribute)
                price_locator = listing.locator("div:first-child a:first-child div:nth-of-type(2) p:first-child")
                if price_locator.count() == 0:
                    continue
                price_title = price_locator.get_attribute("title")
                if not price_title:
                    continue
                price = extract_price(price_title)

                # Extract image url
                image_locator = listing.locator("div:first-child a:first-child div:first-child div:has(img) img")
                if image_locator.count() == 0:
                    continue
                image = image_locator.get_attribute("src")
                if not image:
                    continue

                Link = "https://carousell.sg" + relative_link if relative_link else "N/A"

                # Save data
                scraped_data.append({
                    "Title": product_title,
                    "Price": price,
                    "Image": image,
                    "Link": Link,
                })

            except Exception as e:
                logger.warning(f"Error extracting a listing: {e}")

        browser.close()

        logger.info(f"Scraped {len(scraped_data)} products from client profile")

        return scraped_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("carousell_svc:app", host="0.0.0.0", port=8002, reload=True)