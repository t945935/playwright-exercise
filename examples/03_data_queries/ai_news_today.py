"""使用 Playwright 取得今天的 AI 新聞，輸出 JSON 與 Markdown。"""

import argparse
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

from playwright.sync_api import Error as PlaywrightError, sync_playwright


# 台灣目前全年 UTC+8；不依賴作業系統的時區資料庫。
TAIPEI = timezone(timedelta(hours=8), "Asia/Taipei")
SEARCHES = [
    ("台灣 AI", 'AI OR 人工智慧 OR 生成式AI OR 大型語言模型', "zh-TW", "TW", "TW:zh-Hant"),
    ("國際 AI", '"artificial intelligence" OR "AI agent" OR "generative AI"', "en-US", "US", "US:en"),
    ("AI 公司與模型", 'OpenAI OR ChatGPT OR Anthropic OR "Google Gemini" OR "DeepSeek"', "en-US", "US", "US:en"),
]


def search_url(query: str, day: date, hl: str, gl: str, ceid: str) -> str:
    # 搜尋範圍放寬一天，避免搜尋引擎時區與台灣不同；下方再精確篩選。
    query += f" after:{day - timedelta(days=1)} before:{day + timedelta(days=1)}"
    return "https://news.google.com/rss/search?" + urlencode(
        {"q": query, "hl": hl, "gl": gl, "ceid": ceid}
    )


def parse_feed(body: bytes, day: date, now: datetime) -> tuple[list[dict], int]:
    root = ET.fromstring(body)
    if root.tag != "rss" or root.find("channel") is None:
        raise ValueError("回應不是 RSS，可能遇到驗證頁或網站改版。")
    news, invalid = [], 0
    for item in root.findall("./channel/item"):
        try:
            published = parsedate_to_datetime(item.findtext("pubDate", ""))
            if published.tzinfo is None:
                raise ValueError("發布時間缺少時區")
            published = published.astimezone(TAIPEI)
        except (ValueError, TypeError, OverflowError):
            invalid += 1
            continue
        if published.date() != day or published > now:
            continue
        title = item.findtext("title", "").strip()
        url = item.findtext("link", "").strip()
        source = item.findtext("source", "").strip()
        if not title or not url.startswith("https://"):
            invalid += 1
            continue
        if source and title.endswith(" - " + source):
            title = title[: -(len(source) + 3)]
        news.append({"title": title, "source": source or "未標示來源",
                     "published_at": published.isoformat(), "url": url})
    return news, invalid


def deduplicate(news: list[dict]) -> list[dict]:
    seen_urls, seen_titles, result = set(), set(), []
    for item in sorted(news, key=lambda n: n["published_at"], reverse=True):
        key = (re.sub(r"\s+", " ", item["title"]).strip().casefold(), item["source"].casefold())
        if item["url"] in seen_urls or key in seen_titles:
            continue
        seen_urls.add(item["url"])
        seen_titles.add(key)
        result.append(item)
    return result


def fetch_feed(request, url: str) -> bytes:
    for attempt in range(3):
        try:
            response = request.get(url, timeout=30_000)
            try:
                if not response.ok:
                    raise ValueError(f"HTTP {response.status}")
                return response.body()
            finally:
                response.dispose()
        except (PlaywrightError, ValueError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise RuntimeError("下載失敗")


def markdown(report: dict) -> str:
    lines = [f"# {report['date']} AI 新聞", "",
             f"擷取時間：{report['fetched_at']}（台灣時間）", "",
             f"搜尋結果去重後 {report['matched_count']} 則，輸出 {len(report['articles'])} 則。", "",
             "來源為 Google News RSS；時間依 RSS 發布時間，連結為 Google News 轉址。",
             "本清單是搜尋結果，不保證涵蓋所有 AI 新聞，也不包含全文或 AI 生成摘要。", ""]
    for error in report["errors"]:
        lines.extend([f"⚠ {error}", ""])
    if not report["articles"]:
        lines.extend(["目前沒有符合日期的新聞。", ""])
    for index, item in enumerate(report["articles"], 1):
        title = re.sub(r"([\\`*\[\]<>])", r"\\\1", item["title"]).replace("\n", " ")
        lines.extend([f"{index}. [{title}](<{item['url']}>)",
                      f"   - {item['source']}｜{item['published_at']}", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=date.fromisoformat, help="指定日期 YYYY-MM-DD；預設今天")
    parser.add_argument("--limit", type=int, default=30, help="最多輸出幾則；0 表示全部（預設 30）")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/news")
    args = parser.parse_args()
    now = datetime.now(TAIPEI)
    day = args.date or now.date()
    if args.limit < 0 or day > now.date():
        parser.error("limit 不可小於 0，日期不可晚於今天。")

    news, errors, feeds, successful, invalid = [], [], [], 0, 0
    with sync_playwright() as p:
        request = p.request.new_context()
        try:
            for label, query, hl, gl, ceid in SEARCHES:
                url = search_url(query, day, hl, gl, ceid)
                feeds.append({"name": label, "url": url})
                print(f"正在取得：{label}（{day}）", flush=True)
                try:
                    items, skipped = parse_feed(fetch_feed(request, url), day, now)
                    news.extend(items)
                    invalid += skipped
                    successful += 1
                    print(f"  找到 {len(items)} 則符合日期的新聞", flush=True)
                except (PlaywrightError, ValueError, ET.ParseError) as error:
                    message = f"{label} 取得失敗：{str(error).splitlines()[0]}"
                    errors.append(message)
                    print(message, file=sys.stderr)
        finally:
            request.dispose()
    if not successful:
        print("所有搜尋均失敗，未寫入結果。請檢查網路後重試。", file=sys.stderr)
        return 1
    if invalid:
        errors.append(f"略過 {invalid} 筆缺少有效時間、標題或連結的資料。")
    news = deduplicate(news)
    report = {"date": str(day), "timezone": "Asia/Taipei", "fetched_at": now.isoformat(),
              "matched_count": len(news), "feeds": feeds, "errors": errors,
              "articles": news[:args.limit] if args.limit else news}
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = args.output_dir / f"ai_news_{day}"
    base.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    base.with_suffix(".md").write_text(markdown(report), encoding="utf-8")
    print(f"\n共 {len(news)} 則，輸出 {len(report['articles'])} 則。")
    for item in report["articles"]:
        print(f"{item['published_at'][11:16]} [{item['source']}] {item['title']}")
    print(f"\n結果：{base.with_suffix('.md').resolve()}\n      {base.with_suffix('.json').resolve()}")
    return 2 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
