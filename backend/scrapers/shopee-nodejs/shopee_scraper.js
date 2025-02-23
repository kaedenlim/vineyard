require('dotenv').config(); // Load credentials from .env
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const fs = require('fs');

// Use Stealth Plugin
puppeteer.use(StealthPlugin());

const PRODUCT_URL = "https://shopee.sg/Jeep-JP-EW011-TWS-True-Wireless-Bluetooth-Earphones-HiFi-Sound-Wireless-Earbuds-Noise-Cancellation-HD-Calls-Headset-i.1058254930.16696926436";
const OUTPUT_FILE = "shopee_product_details.json";

// Load credentials from .env file
const USERNAME = process.env.SHOPEE_USERNAME;
const PASSWORD = process.env.SHOPEE_PASSWORD;

async function loginShopee(page) {
    console.log("🔄 Navigating to Shopee login page...");
    await page.goto("https://shopee.sg/buyer/login", { waitUntil: "networkidle2" });

    // Wait for login fields
    await page.waitForSelector("input[name='loginKey']", { timeout: 60000 });

    // Enter Username
    console.log("🔑 Entering Username...");
    await page.type("input[name='loginKey']", USERNAME, { delay: 100 });

    // Enter Password
    console.log("🔑 Entering Password...");
    await page.type("input[name='password']", PASSWORD, { delay: 100 });

    // Click Login Button
    console.log("🔄 Clicking Login...");
    await page.click("button.b5aVaf.PVSuiZ.Gqupku.qz7ctP.qxS7lQ.Q4KP5g");

    // Wait for manual CAPTCHA solving (if needed)
    console.log("⏳ If CAPTCHA appears, solve it manually...");
    await page.waitForNavigation({ waitUntil: "networkidle2", timeout: 60000 });

    console.log("✅ Logged in successfully!");
}

async function scrapeShopee() {
    console.log("🚀 Launching browser with stealth mode...");
    const browser = await puppeteer.launch({
        headless: false,
        args: [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-blink-features=AutomationControlled"
        ]
    });

    const page = await browser.newPage();

    // Enable Chrome DevTools Protocol (CDP)
    const client = await page.target().createCDPSession();
    await client.send('Network.enable');
    await client.send('Page.enable');
    await client.send('Runtime.enable');

    // Spoof WebRTC & WebGL
    await page.evaluateOnNewDocument(() => {
        Object.defineProperty(navigator, 'webdriver', { get: () => false });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });

        // WebGL Spoof
        const getParameter = WebGLRenderingContext.prototype.getParameter;
        WebGLRenderingContext.prototype.getParameter = function(param) {
            if (param === 37445) return 'Intel Inc.';
            if (param === 37446) return 'Intel Iris OpenGL Engine';
            return getParameter(param);
        };

        // WebRTC Spoof (Prevent IP Leak)
        Object.defineProperty(navigator, 'mediaDevices', {
            get: () => ({
                enumerateDevices: async () => [],
                getUserMedia: async () => { throw new Error("Permission denied"); }
            })
        });
    });

    // Login to Shopee
    await loginShopee(page);

    console.log("🔄 Navigating to product page...");
    await page.goto(PRODUCT_URL, { waitUntil: "networkidle2", timeout: 60000 });

    // Simulate scrolling (important for loading dynamic content)
    console.log("🔄 Scrolling page to trigger lazy loading...");
    for (let i = 0; i < 10; i++) {
        await page.evaluate(() => window.scrollBy(0, 500));
        await new Promise(r => setTimeout(r, Math.random() * 3000 + 1000));
    }

    console.log("🔄 Extracting product details...");

    // Extract product details
    const productDetails = await page.evaluate(() => {
        const titleElement = document.querySelector("div.pdp-mod-product-badge-title");
        const priceElement = document.querySelector("div.pdp-product-price");
        const ratingElement = document.querySelector("div.pdp-product-rating span");
        const reviewsElement = document.querySelector("div.section-seller-info__item span");
        const availabilityElement = document.querySelector("button.pdp-button_theme_orange");
        const images = Array.from(document.querySelectorAll("div.pdp-mod-common-image div img"))
            .map(img => img.src);

        return {
            title: titleElement ? titleElement.innerText : "N/A",
            price: priceElement ? priceElement.innerText : "N/A",
            rating: ratingElement ? ratingElement.innerText : "N/A",
            reviews: reviewsElement ? reviewsElement.innerText : "N/A",
            availability: availabilityElement ? "In Stock" : "Out of Stock",
            images: images.length > 0 ? images : "N/A"
        };
    });

    console.log("✅ Product details extracted:", productDetails);

    // Save results to JSON file
    fs.writeFileSync(OUTPUT_FILE, JSON.stringify(productDetails, null, 2));
    console.log(`✅ Scraped product details saved to ${OUTPUT_FILE}`);

    await browser.close();
}

// Run the scraper
scrapeShopee().catch(console.error);