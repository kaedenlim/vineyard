from playwright.sync_api import sync_playwright
from datetime import datetime, timezone, timedelta

def scrape_lazada(product_name: str):
    times = 1;
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

        while times:
            times -= 1;
            page.wait_for_timeout(5000)

            # Get all the products on the page and their counts to keep track
            items_locator = page.locator("div[data-qa-locator='product-item']")
            no_items = items_locator.count()
            total_items += no_items

            items = items_locator.all()

            scraped_data = []

            for item in items:
                try:
                    item_title = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(2) a:first-child").text_content()
                    item_link = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(2) a[href]").nth(0).get_attribute("href")
                    item_price = item.locator("div:first-child div:first-child div:nth-of-type(2) div:nth-of-type(3) span:first-child").text_content()
                    item_image = item.locator("div:first-child div:first-child div:first-child div:first-child a:first-child div.picture-wrapper img[src]").get_attribute("src")
                    
                    stripped_price = item_price.strip("'$'")
                    full_item_url = "https:" + item_link

                    scraped_data.append({
                        "title": item_title,
                        "price": stripped_price,
                        "image": item_image if item_image.startswith("https://img.lazcdn") else "",
                        "link": full_item_url
                    })
            
                # button = page.locator("button.ant-pagination-item-link span[aria-label='right']")
                # if button.is_visible() and button.get_attribute("disabled") is None:
                #     times -= 1
                #     button.click()
                # else:
                #     print("No more pages left.")
                #     break
                except Exception as e:
                    print(f"Error extracting a listing: {e}")
        
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

def onboard_lazada(profile_url: str):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
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
                    
                    stripped_price = item_price.strip("'$'")
                    full_item_url = "https:" + item_link

                    scraped_data.append({
                        "title": item_title,
                        "price": stripped_price,
                        "image": item_image if item_image.startswith("https://img.lazcdn") else "",
                        "link": full_item_url
                    })
            
                # button = page.locator("button.ant-pagination-item-link span[aria-label='right']")
                # if button.is_visible() and button.get_attribute("disabled") is None:
                #     times -= 1
                #     button.click()
                # else:
                #     print("No more pages left.")
                #     break
                except Exception as e:
                    print(f"Error extracting a listing: {e}")

        return scraped_data