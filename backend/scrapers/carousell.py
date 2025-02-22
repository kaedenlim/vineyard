from playwright.sync_api import sync_playwright
import datetime
import random
import re

def extract_price(price_str):
    """Extracts numerical value from a currency string."""
    cleaned = re.sub(r"[^\d.]", "", price_str)
    return float(cleaned) # if "." in cleaned else int(cleaned)

def carousell_scraper(product_name: str):
    with sync_playwright() as p:

        count = 1

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

        listings = page.locator("div[data-testid^='listing-card-']").all()
        
        if (len(listings) == 0):
            listings = page.locator("//div[contains(@data-testid, 'listing-card-')]").all()

        scraped_data = []

        if (len(listings) == 0):
            print("No listings found")
            browser.close()

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
                price = listing.locator("div:first-child a:nth-of-type(2) div:nth-of-type(2) p:first-child").get_attribute("title")
                
                current_time = datetime.datetime.now()

                relative_link = listing.locator("a.D_iU").last.get_attribute("href")

                url = BASE_URL + relative_link if relative_link else "N/A"

                # Save data
                scraped_data.append({
                    "id": count,
                    "url": url,
                    "title": product_title,
                    "price": extract_price(price),
                    "scrape_time": current_time
                })

                count += 1

            except Exception as e:
                print(f"Error extracting a listing: {e}")

        browser.close()

        return scraped_data
