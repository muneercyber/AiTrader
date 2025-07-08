import os
import time
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright

SCREENSHOT_DIR = "screenshots"
Path(SCREENSHOT_DIR).mkdir(exist_ok=True)

# Async screenshot capturing with Playwright (avoiding sync API in async code)
async def capture_screenshot(pair: str) -> str:
    file_name = f"{pair}_chart_{int(time.time())}.png"
    screenshot_path = os.path.join(SCREENSHOT_DIR, file_name)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://pocketoption.com/en/cabinet/demo-quick-high-low/", timeout=60000)

        try:
            await page.wait_for_selector("canvas", timeout=15000)
            canvas = await page.query_selector("canvas")
            await canvas.screenshot(path=screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Failed to capture chart screenshot: {e}")
        await browser.close()

    return screenshot_path

# Mock candles (replace with real data later)
def get_recent_candles(pair: str, limit: int = 4):
    # Example of 30-second candles, 4 candles = 2 minutes total
    # Replace this with real data from sniffer or WS in future
    base = 1.1000
    candles = []
    for i in range(limit):
        candles.append({
            "time": (datetime.utcnow()).isoformat(),
            "open": base + 0.001 * i,
            "high": base + 0.002 + 0.001 * i,
            "low": base - 0.001 + 0.001 * i,
            "close": base + 0.0015 + 0.001 * i
        })
    return candles
