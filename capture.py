import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.makedirs("docs", exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # Make the viewport wide enough so it looks nice
        page = await browser.new_page(viewport={"width": 1000, "height": 800})
        
        # 1. Empty state
        await page.goto("http://localhost:8000/")
        await page.wait_for_selector("#emptyState", state="visible")
        # Slight delay for styling
        await page.wait_for_timeout(500)
        await page.screenshot(path="docs/screenshot-empty.png")
        
        # 2. Click an example and wait for trace
        # The first example is: "A user entered their password on a phishing page..."
        await page.click(".example-btn")
        
        # Wait for answer to load (typing indicator to disappear, assistant message to appear)
        await page.wait_for_selector(".msg.assistant .answer-text", state="visible", timeout=30000)
        
        # Wait for the trace toggle to appear
        await page.wait_for_selector(".trace-toggle", state="visible", timeout=15000)
        
        # Click the trace toggle to expand it
        await page.click(".trace-toggle")
        
        # Wait for it to be open
        await page.wait_for_selector(".trace-list.open", state="visible", timeout=5000)
        
        # Add a slight delay for any UI transitions
        await page.wait_for_timeout(500)
        
        # Take the screenshot
        await page.screenshot(path="docs/screenshot-answer.png")
        
        await browser.close()

asyncio.run(main())
