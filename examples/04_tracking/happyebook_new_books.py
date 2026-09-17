"""Python + Playwright 新書雷達：比較 Happy eBook 本次與上次完整書單。"""

import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright, expect


URL = "https://happyebook.com/books.html"
TAIPEI = timezone(timedelta(hours=8))


def validate_books(books):
    if not isinstance(books, list) or not books:
        raise ValueError("完整書單為空或格式錯誤，不更新比較基準。")
    seen = set()
    for book in books:
        if not isinstance(book, dict) or not isinstance(book.get("title"), str) or not book["title"].strip():
            raise ValueError("書目缺少有效書名，不更新比較基準。")
        address = book.get("url")
        if not isinstance(address, str):
            raise ValueError("書目缺少網址。")
        parsed = urlsplit(address)
        if parsed.scheme != "https" or parsed.netloc != "happyebook.com":
            raise ValueError(f"書目連結格式異常：{address}")
        if address in seen:
            raise ValueError(f"書目連結重複，請確認網站資料：{address}")
        seen.add(address)
    return books


def collect_books(page):
    page.goto(URL, wait_until="domcontentloaded")
    summary = page.locator("[data-books-count]")
    expect(summary).to_contain_text("全部上架作品")
    cards = page.locator("article.book-card")
    more = page.get_by_role("button", name=re.compile(r"^顯示更多書籍"))
    expected_total = None
    while True:
        match = re.search(r"顯示\s*(\d+)\s*/\s*(\d+)\s*本", summary.inner_text())
        if not match:
            raise ValueError("無法確認完整書單數量，請檢查網站是否改版。")
        shown, total = map(int, match.groups())
        if total <= 0 or shown > total:
            raise ValueError("書單數量異常，不更新比較基準。")
        if expected_total is not None and total != expected_total:
            raise ValueError("讀取期間書單總數改變，請重新查詢。")
        expected_total = total
        expect(cards).to_have_count(shown)
        if shown == total:
            break
        expect(more).to_be_visible()
        more.click()
        expect(cards.nth(shown)).to_be_attached()
    expect(cards).to_have_count(expected_total)
    books = cards.evaluate_all("""elements => elements.map(card => {
        const detail = [...card.querySelectorAll('a')].find(a => a.textContent.trim() === '更多資訊');
        return {
            title: card.querySelector('h3')?.textContent.trim() || '',
            subtitle: card.querySelector('.book-subtitle')?.textContent.trim() || '',
            category: card.querySelector('.tag.category')?.textContent.trim() || '',
            url: detail?.href || '',
            reading_url: card.querySelector('.book-cover-link')?.href || ''
        };
    })""")
    return validate_books(books)


def compare_books(previous, current):
    validate_books(current)
    if previous is None:
        return [], []
    validate_books(previous)
    old = {book["url"] for book in previous}
    new = {book["url"] for book in current}
    return ([book for book in current if book["url"] not in old],
            [book for book in previous if book["url"] not in new])


def load_previous(path):
    if not path.exists():
        return None
    state = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(state, dict) or state.get("source") != URL or state.get("version") != 1:
        raise ValueError("既有基準檔格式不符；保留原檔，請確認輸出目錄。")
    validate_books(state.get("books"))
    return state


def write_json(path, value):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def html_report(report, current):
    first = report["first_run"]
    title = "已建立書單基準" if first else f"新增 {len(report['new_books'])} 筆書目"
    displayed = current if first else report["new_books"]
    cards = []
    for book in displayed:
        cards.append(f'<article><h2><a href="{escape(book["url"], quote=True)}">{escape(book["title"])}</a></h2>'
                     f'<p>{escape(book.get("subtitle", ""))}</p><small>{escape(book.get("category", ""))}</small></article>')
    description = "第一次執行只建立基準，以下為目前完整書單。" if first else "以下為相較上次完整書單新增的項目。"
    if not displayed:
        cards.append("<p>這次沒有發現新書。</p>")
    return f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Happy eBook 新書雷達</title>
<style>body{{font:16px system-ui;max-width:960px;margin:40px auto;padding:0 20px;background:#f6f8fc;color:#182337}}
h1{{font-size:30px}}h2{{font-size:19px;margin:0}}a{{color:#145cb5}}article{{background:white;padding:20px;margin:14px 0;border-radius:12px}}
p{{line-height:1.7}}small{{color:#586679}}</style><h1>Happy eBook 新書雷達</h1>
<p>{escape(report['checked_at'])}｜完整書單 {report['total']} 筆</p><h2>{title}</h2><p>{description}</p>
<p>「新增」表示相較上次查詢新出現的書目，不代表出版日期。暫時下架後重現、或更換網址，也可能列入新增。</p>
<p>上次有、本次未出現：{len(report['missing_books'])} 筆（不代表確認下架）。</p>
{''.join(cards)}<p>來源：<a href="{URL}">Happy eBook 書籍列表</a></p></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器操作")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/books/radar")
    args = parser.parse_args()
    folder = args.output_dir
    baseline = folder / "baseline.json"
    previous = load_previous(baseline)
    print("正在讀取 Happy eBook 完整書單…", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        try:
            page = browser.new_page(locale="zh-TW")
            page.set_default_timeout(30_000)
            page.set_default_navigation_timeout(60_000)
            current = collect_books(page)
        finally:
            browser.close()
    added, missing = compare_books(previous["books"] if previous else None, current)
    now = datetime.now(TAIPEI)
    report = {"source": URL, "checked_at": now.isoformat(), "first_run": previous is None,
              "previous_checked_at": previous.get("checked_at") if previous else None,
              "total": len(current), "new_books": added, "missing_books": missing}
    folder.mkdir(parents=True, exist_ok=True)
    history = folder / "history"
    history.mkdir(exist_ok=True)
    snapshot = {"version": 1, "source": URL, "checked_at": now.isoformat(), "books": current}
    stamp = now.strftime("%Y%m%d_%H%M%S_%f")
    write_json(history / f"{stamp}.json", {"report": report, "snapshot": snapshot})
    write_json(folder / "latest.json", report)
    (folder / "latest.html").write_text(html_report(report, current), encoding="utf-8")
    # 讀取、比對與輸出均成功後才替換上次基準。
    write_json(baseline, snapshot)
    if previous is None:
        print(f"首次執行，已建立 {len(current)} 筆書目的基準；下次會比較新增書籍。")
    else:
        print(f"完整書單 {len(current)} 筆；新增 {len(added)} 筆；本次未出現 {len(missing)} 筆。")
        for book in added:
            print(f"新書：{book['title']}\n      {book['url']}")
    print(f"\n報告：{(folder / 'latest.html').resolve()}\n基準：{baseline.resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}\n未完成的查詢不更新比較基準。", file=sys.stderr)
        raise SystemExit(1)
