"""開啟指定的公開部落格，保留畫面供觀察。"""
import argparse
import os
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default=os.environ.get("BLOGGER_PUBLIC_URL", ""), help="公開網址；也可用 BLOGGER_PUBLIC_URL")
args = parser.parse_args()
if not args.url.startswith("https://"):
    parser.error("請用 --url 或 BLOGGER_PUBLIC_URL 提供 https 公開網址")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto(args.url)
    print(page.title())
    input("按 Enter 關閉瀏覽器…")
    browser.close()
