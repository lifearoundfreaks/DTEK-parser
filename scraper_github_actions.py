from playwright.sync_api import sync_playwright
import json
import re
import os
from datetime import datetime
import requests

url = "https://www.dtek-dnem.com.ua/ua/shutdowns"
BROWSERLESS_TOKEN = os.getenv("BROWSERLESS_TOKEN", "")

def scrape_dtek():
    # Try using Browserless.io REST API with content endpoint (different IP pool)
    print(f"[{datetime.now()}] Using Browserless.io REST API...")
    try:
        browserless_api = f"https://production-sfo.browserless.io/content?token={BROWSERLESS_TOKEN}"
        response = requests.post(
            browserless_api,
            json={
                "url": url,
                "gotoOptions": {
                    "waitUntil": "networkidle"
                },
                "waitFor": 3000,
                "stealth": True,
                "blockAds": True
            },
            timeout=60
        )
        html = response.text
        print(f"[{datetime.now()}] Got response from Browserless.io")
    except Exception as e:
        print(f"❌ Browserless.io failed: {e}")

    if 'Incapsula' in html or 'incident_id' in html:
        print("❌ Bot protection detected! HTML preview:")
        print(html[:500])
        return

    match = re.search(r'DisconSchedule\.fact\s*=\s*(\{.+?\})\s*</script>', html, re.DOTALL)
    if not match:
        print("❌ Failed to extract data. HTML preview:")
        print(html[:500])
        return

    data = json.loads(match.group(1))

    with open('dtek_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✓ Data saved to dtek_data.json")

if __name__ == "__main__":
    scrape_dtek()
