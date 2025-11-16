from playwright.sync_api import sync_playwright
import json
import re
import os
from datetime import datetime

url = "https://www.dtek-dnem.com.ua/ua/shutdowns"
BROWSERLESS_TOKEN = os.getenv("BROWSERLESS_TOKEN", "")

def scrape_dtek():
    browserless_url = f"wss://production-sfo.browserless.io/chromium/playwright?token={BROWSERLESS_TOKEN}&stealth=true"
    
    print(f"[{datetime.now()}] Connecting to Browserless.io with stealth mode...")
    
    with sync_playwright() as p:
        browser = p.chromium.connect(browserless_url)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = context.new_page()
        
        page.goto(url, wait_until='networkidle')

        page.wait_for_function("typeof DisconSchedule !== 'undefined' && DisconSchedule.fact")
        page.wait_for_timeout(1000)
        
        html = page.content()
        
        browser.close()
        print(f"[{datetime.now()}] ✓ Page scraped successfully")

    match = re.search(r'DisconSchedule\.fact\s*=\s*(\{.+?\})\s*</script>', html, re.DOTALL)

    if not match:
        print("❌ Failed to extract data")
        return

    json_text = match.group(1)
    data = json.loads(json_text)

    with open('dtek_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Data saved to dtek_data.json")

if __name__ == "__main__":
    scrape_dtek()
