from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://t945935k.blogspot.com/")
    print(page.title())
    input("按 Enter 關閉瀏覽器…")
    browser.close()
