# import nest_asyncio; nest_asyncio.apply()  # This is needed to use sync API in repl 
from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta

def scrape_lazada(product_name: str, times: int):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
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

        # Might cause issues if first image is embedded image, need to have default picture
        product_type_image = page.locator("img[type=product]").first.get_attribute("src")

        while times > 0:
            page.wait_for_timeout(5000)

            # Get all the products on the page and their counts to keep track
            items = page.locator("div[data-qa-locator='product-item']")
            no_items = items.count()
            total_items += no_items

            scraped_data = []

            for i in range(no_items):
                item_title = items.nth(i).locator("a[title]")
                item_price = items.nth(i).locator(".ooOxS")
                item_image = items.nth(i).locator("img[type=product]").get_attribute("src")
                item_link = items.nth(i).locator("a[title][href]").get_attribute("href")
                
                stripped_price = item_price.text_content().strip("'$'") if item_price else None
                total_price += float(stripped_price)
                full_item_url = "https:" + item_link if item_link else None

                scraped_data.append({
                    "title": item_title.text_content() if item_title else None,
                    "price": stripped_price if stripped_price else None,
                    "image": item_image if item_image.startswith("https://img.lazcdn") else None,
                    "link": full_item_url
                })
            
            button = page.locator("button.ant-pagination-item-link span[aria-label='right']")
            if button.is_visible() and button.get_attribute("disabled") is None:
                times -= 1
                button.click()
            else:
                print("No more pages left.")
                break
        
        # Get average price for the product
        average_price = total_price / total_items

        # Get current time in Singapore Time (ISO format)
        sgt_timezone = timezone(timedelta(hours=8))
        timestamp = datetime.now(sgt_timezone).isoformat() + "Z"
        
        lazada = {
            "scraped_data": scraped_data,
            "timestamp": timestamp,
            "average_price": average_price,
            "product_type_image": product_type_image
        }
    
        return lazada


        
        
        
