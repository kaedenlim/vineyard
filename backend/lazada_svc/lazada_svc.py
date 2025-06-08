from fastapi import FastAPI, Query
import uvicorn
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta
import random
import re
from dataclasses import dataclass
from typing import List
import logging
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)

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

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
]

def extract_price(price_str):
    """Extracts numerical value from a currency string."""
    cleaned = re.sub(r"[^\d.]", "", price_str)
    return float(cleaned) # if "." in cleaned else int(cleaned)

app = FastAPI()

@app.get("/lazada/scrape_market", response_model=ScrapeResult)
def scrape_lazada(product_name: str = Query(..., description="Product name to search")):
    logging.info(f"Scrape route '/lazada/scrape_market' called with product_name: {product_name}")
    times = 1;
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=random.choice(USER_AGENTS),
            # Add additional headers to look more like a real browser
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
        )
        # Enable JavaScript and cookies
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = context.new_page()

        # go to url
        page.goto("https://lazada.sg")

        # Select the input field
        # Fill the input field with clothes, will take input from NLP
        search_box = page.get_by_placeholder("Search in Lazada")
        search_box.wait_for()
        search_box.type(product_name)
        search_box.press("Enter")

        # Facilitate keeping track of average price
        total_items = 0
        total_price = 0.0
        
        rank = 1;
        while times:
            times -= 1
            page.wait_for_timeout(5000)

            # Get all the products on the page and their counts to keep track
            items_elements = page.locator("div[data-qa-locator='product-item']")
            items = items_elements.all();

            scraped_data = []

            for item in items:
                try:
                    item_title = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(2) a[title]").text_content()
                    item_link = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(2) a[href]").nth(0).get_attribute("href")
                    item_price_pre = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(3) span:first-child").text_content()
                    item_price = 0
                    if item_price_pre != '':
                        item_price = extract_price(item_price_pre)
                    item_image = item.locator("div:first-child div:first-child div:first-child div:first-child a:first-child div.picture-wrapper img[type='product']").get_attribute("src")
                    
                    discount_element = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(4) span:first-child del")
                    item_discount = 0
                    if discount_element.count() > 0:
                        item_discount = 1 - (item_price / extract_price(discount_element.text_content()))

                    full_item_url = urljoin("https://lazada.sg", item_link)

                    product = Product(
                        Title=item_title,
                        Price=item_price,
                        Discount=item_discount,
                        Image=item_image if item_image.startswith("https://img.lazcdn") else "",
                        Link=full_item_url,
                        Ranking=rank
                    )

                    scraped_data.append(product)

                    total_items += 1
                    total_price += item_price
                    rank += 1

                    if len(scraped_data) >= 10:
                        break
            
                # button = page.locator("button.ant-pagination-item-link span[aria-label='right']")
                # if button.is_visible() and button.get_attribute("disabled") is None:
                #     times -= 1
                #     button.click()
                # else:
                #     print("No more pages left.")
                #     break
                except Exception as e:
                    logging.error(f"Error extracting a listing: {e}")
            if len(scraped_data) >= 10:
                break
        
        # Get average price for the product
        average_price = total_price / total_items if total_items > 0 else 0.0

        # Get current time in Singapore Time (ISO format)
        sgt_timezone = timezone(timedelta(hours=8))
        timestamp = datetime.now(sgt_timezone).isoformat() + "Z"
        
        lazada = ScrapeResult(
            scraped_data=scraped_data,
            timestamp=timestamp,
            average_price=average_price
        )
    
        logging.info(f"Scraped {len(scraped_data)} products from market search")
        return lazada

@app.get("/lazada/scrape_client")
def scrape_lazada_client(profile_url: str = Query(..., description="Profile URL")):
    logging.info(f"Scrape route '/lazada/scrape_client' called with profile_url: {profile_url}")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent=random.choice(USER_AGENTS),
            # Add additional headers to look more like a real browser
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Connection': 'keep-alive',
            }
        )
        # Enable JavaScript and cookies
        context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        page = context.new_page()

        # go to url
        page.goto(profile_url)
        times = 1

        while times:
            times -= 1
            page.wait_for_timeout(5000)

            # Get all the products on the page and their counts to keep track
            items = page.locator("div[data-qa-locator='product-item']").all()

            scraped_data = []

            for item in items:
                try:
                    item_title = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(2) a:first-child").text_content()
                    item_link = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(2) a[href]").nth(0).get_attribute("href")
                    item_price = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(3) span:first-child").text_content()
                    item_image = item.locator("div:first-child div:first-child div:first-child div:first-child a:first-child div.picture-wrapper img[src]").get_attribute("src")
                    
                    stripped_price = float(item_price.strip("'$'"))
                    full_item_url = "https:" + item_link

                    scraped_data.append({
                        "title": item_title,
                        "price": stripped_price,
                        "image": item_image if item_image.startswith("https://img.lazcdn") else "",
                        "link": full_item_url
                    })

                    if len(scraped_data) >= 10:
                        break
            
                # button = page.locator("button.ant-pagination-item-link span[aria-label='right']")
                # if button.is_visible() and button.get_attribute("disabled") is None:
                #     times -= 1
                #     button.click()
                # else:
                #     print("No more pages left.")
                #     break
                except Exception as e:
                    logging.error(f"Error extracting a listing: {e}")

        logging.info(f"Scraped {len(scraped_data)} products from client profile")
        return scraped_data

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("lazada_svc:app", host="0.0.0.0", port=8001, reload=True)