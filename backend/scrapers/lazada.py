# import nest_asyncio; nest_asyncio.apply()  # This is needed to use sync API in repl 
from playwright.sync_api import sync_playwright

def scrape_lazada(product_name: str, times: int):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # go to url
        page.goto("https://lazada.sg")

        # Select the input field
        # Fill the input field with clothes, hardcoded for now, will take input from NLP
        search_box = page.get_by_placeholder("Search in Lazada")
        search_box.wait_for()
        search_box.type(product_name)
        search_box.press("Enter")

        while times > 0:
            page.wait_for_timeout(5000)

            items = page.locator("div[data-qa-locator='product-item']")
            no_items = items.count()
            scraped_data = []

            for i in range(no_items):
                item_title = items.nth(i).locator("a[title]")
                item_price = items.nth(i).locator(".ooOxS")
                
                scraped_data.append({
                    "title": item_title.text_content() if item_title else None,
                    "price": item_price.text_content().strip("'$'") if item_price else None,
                })
            
            button = page.locator("button.ant-pagination-item-link span[aria-label='right']")
            # if button.is_visible() and button.get_attribute("disabled") is None:
            button.click()
            # else:
            #     print("No more pages left.")
            #     break
            times -= 1
    
        return scraped_data


        
        
        
