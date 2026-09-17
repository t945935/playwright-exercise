"""瀏覽 Happy eBook 的 AI Agent 分類，列出全部書籍並存成 JSON。

安裝：python -m pip install playwright
      python -m playwright install chromium
執行：python happyebook_ai_agent.py
背景執行：python happyebook_ai_agent.py --headless
"""

import argparse
import json
from pathlib import Path
import re

from playwright.sync_api import Page, expect, sync_playwright


def collect_books(page: Page) -> list[dict[str, str]]:
    # 不等待所有封面圖片載入，以免圖片請求拖慢操作。
    page.goto("https://happyebook.com/", wait_until="domcontentloaded")
    page.locator("header").get_by_role(
        "link", name="書籍列表", exact=True
    ).click()
    page.wait_for_url("**/books.html", wait_until="domcontentloaded")

    page.get_by_role("button", name="AI Agent", exact=True).click()
    summary = page.locator("[data-books-count]")
    expect(summary).to_contain_text("目前篩選結果")

    # 依網站目前的總數展開，不能把 28 本寫死。
    cards = page.locator("article.book-card")
    more = page.get_by_role("button", name=re.compile(r"^顯示更多書籍"))
    while True:
        match = re.search(r"顯示\s*(\d+)\s*/\s*(\d+)\s*本", summary.inner_text())
        if not match:
            raise RuntimeError("無法讀取書籍數量，請檢查網站是否改版。")
        shown, total = map(int, match.groups())
        if shown == total:
            break
        expect(more).to_be_visible()
        more.click()
        # 等待新增的第一張書卡，避免固定 sleep。
        expect(cards.nth(shown)).to_be_attached()

    expect(cards).to_have_count(total)
    books = []
    for card in cards.all():
        books.append({
            "title": card.get_by_role("heading", level=3).inner_text(),
            "subtitle": card.locator(".book-subtitle").inner_text(),
            "url": card.get_by_role("link", name="更多資訊", exact=True).evaluate(
                "link => link.href"
            ),
            "reading_url": card.locator(".book-cover-link").evaluate(
                "link => link.href"
            ),
        })
    # 同名書目可能有不同頁面，保留網站列出的每一筆。
    return books


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headless", action="store_true", help="不顯示瀏覽器視窗")
    parser.add_argument("--output", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/books/ai_agent_books.json")
    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        try:
            page = browser.new_page(locale="zh-TW")
            page.set_default_timeout(30_000)
            page.set_default_navigation_timeout(60_000)
            books = collect_books(page)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(books, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"AI Agent 分類共 {len(books)} 筆書目：")
            for index, book in enumerate(books, start=1):
                print(f"{index}. {book['title']}\n   {book['url']}")
            print(f"\n已儲存至：{args.output.resolve()}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
