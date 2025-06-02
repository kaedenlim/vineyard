import asyncio
import random
import os
import csv
from dotenv import load_dotenv
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

# Load credentials
load_dotenv()
USERNAME = os.getenv("SHOPEE_USERNAME")
PASSWORD = os.getenv("SHOPEE_PASSWORD")

PRODUCT_URL = "https://shopee.sg/Jeep-JP-EW011-TWS-True-Wireless-Bluetooth-Earphones-HiFi-Sound-Wireless-Earbuds-Noise-Cancellation-HD-Calls-Headset-i.1058254930.16696926436"
OUTPUT_FILE = "shopee_product_details.csv"

PROXY_SERVER = "your_proxy_here"  # Example: "http://username:password@sg.proxy.com:8000"

async def login_shopee(page):
    print("🔄 Navigating to Shopee login page...")
    await page.goto("https://shopee.sg/buyer/login", timeout=90000)
    await stealth_async(page)

    await asyncio.sleep(random.uniform(3, 5))
    await page.wait_for_selector("input[name='loginKey']", timeout=60000)

    for char in USERNAME:
        await page.type("input[name='loginKey']", char, delay=random.uniform(50, 150))
    await asyncio.sleep(random.uniform(2, 4))

    for char in PASSWORD:
        await page.type("input[name='password']", char, delay=random.uniform(50, 150))
    await asyncio.sleep(random.uniform(3, 6))

    print("🔄 Clicking login button...")
    await page.click("button.b5aVaf.PVSuiZ.Gqupku.qz7ctP.qxS7lQ.Q4KP5g")
    await asyncio.sleep(random.uniform(5, 10))

    print("✅ Logged in successfully!")

async def scrape_shopee_product():
    async with async_playwright() as p:
        print("🚀 Launching browser in ultra-stealth mode...")
        browser = await p.chromium.launch(
            headless=False,
            proxy={"server": PROXY_SERVER},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-infobars",
                "--disable-features=IsolateOrigins,site-per-process",
            ]
        )

        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-SG",
            timezone_id="Asia/Singapore",
            permissions=["geolocation"],
            geolocation={"latitude": 1.3521, "longitude": 103.8198},
            device_scale_factor=1.25
        )
        page = await context.new_page()
        await login_shopee(page)

        print("🔄 Navigating to product page...")
        await page.goto(PRODUCT_URL, timeout=90000)
        await asyncio.sleep(random.uniform(3, 7))

        print("🔄 Simulating user interactions...")
        for _ in range(random.randint(5, 10)):
            await page.mouse.move(random.randint(300, 1000), random.randint(100, 600))
            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(random.uniform(2, 5))

        await page.wait_for_selector("div.product-briefing", timeout=60000)

        print("🔄 Extracting product details...")
        title = await page.inner_text("div.pdp-mod-product-badge-title") if await page.query_selector("div.pdp-mod-product-badge-title") else "N/A"
        price = await page.inner_text("div.pdp-product-price") if await page.query_selector("div.pdp-product-price") else "N/A"
        rating = await page.inner_text("div.pdp-product-rating span") if await page.query_selector("div.pdp-product-rating span") else "N/A"
        reviews = await page.inner_text("div.section-seller-info__item span") if await page.query_selector("div.section-seller-info__item span") else "N/A"
        availability = "In Stock" if await page.query_selector("button.pdp-button_theme_orange") else "Out of Stock"

        image_elements = await page.query_selector_all("div.pdp-mod-common-image div img")
        image_urls = [await img.get_attribute("src") for img in image_elements if img]

        print("✅ Product details extracted!")

        with open(OUTPUT_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Product Name", "Price", "Rating", "Reviews", "Availability", "Images"])
            writer.writerow([title, price, rating, reviews, availability, ", ".join(image_urls)])

        print(f"✅ Scraped product details saved to {OUTPUT_FILE}")
        await browser.close()

asyncio.run(scrape_shopee_product())