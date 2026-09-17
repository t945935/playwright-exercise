import argparse
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description="開啟 Playwright 網站並讀取標題")
parser.add_argument("--headed", action="store_true", help="顯示瀏覽器視窗")
args = parser.parse_args()

with sync_playwright() as p:
    browser = p.chromium.launch(headless=not args.headed)
    page = browser.new_page()
    page.goto("https://playwright.dev")
    print(page.title())
    browser.close()
