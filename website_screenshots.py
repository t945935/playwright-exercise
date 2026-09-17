"""Playwright + Python：一次擷取手機、平板、電腦版網頁截圖。"""

import argparse
from datetime import datetime, timedelta, timezone
from html import escape
import json
from pathlib import Path
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


SIZES = [
    {"name": "phone", "label": "手機", "width": 390, "height": 844, "mobile": True},
    {"name": "tablet", "label": "平板", "width": 820, "height": 1180, "mobile": True},
    {"name": "desktop", "label": "電腦", "width": 1440, "height": 900, "mobile": False},
]


def prepare_page(page, full_page):
    # 等待字型與圖片，但設上限，避免外部資源永遠無回應。
    page.evaluate("""async () => {
        await Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 5000))]);
    }""")
    if full_page:
        # 分段捲動以觸發延遲載入；無限捲動網站最多處理 40 個畫面。
        for step in range(40):
            end = page.evaluate("""async () => {
                window.scrollBy(0, Math.max(300, innerHeight * 0.8));
                await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
                const visible = [...document.images].filter(img => {
                    const rect = img.getBoundingClientRect();
                    return rect.bottom > 0 && rect.top < innerHeight;
                });
                await Promise.race([
                    Promise.all(visible.map(img => img.decode().catch(() => {}))),
                    new Promise(r => setTimeout(r, 1500))
                ]);
                return scrollY + innerHeight >= document.documentElement.scrollHeight - 2;
            }""")
            if end:
                break
    page.evaluate("""async () => {
        await Promise.race([
            Promise.all([...document.images].map(img => img.decode().catch(() => {}))),
            new Promise(r => setTimeout(r, 5000))
        ]);
        window.scrollTo(0, 0);
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    }""")


def gallery(report):
    cards = []
    for item in report["screenshots"]:
        cards.append(f'''<article><h2>{escape(item['label'])}</h2>
<p>{item['width']} × {item['height']} CSS px</p>
<a href="{item['file']}" target="_blank"><img src="{item['file']}" alt="{escape(item['label'])}截圖"></a>
<p><a href="{item['file']}" download>下載 PNG</a> · 點圖查看原尺寸</p>
<small>水平溢出：{item['horizontal_overflow']} px；未載入圖片：{item['unloaded_images']}</small></article>''')
    for item in report["errors"]:
        cards.append(f"<article><h2>{escape(item['label'])}：失敗</h2><p>{escape(item['error'])}</p></article>")
    mode = "完整頁面" if report["full_page"] else "首屏"
    return f'''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>多尺寸截圖比較</title>
<style>body{{font:16px system-ui;background:#f1f5f9;color:#172437;margin:0;padding:28px}}
h1{{margin-top:0}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:20px}}
article{{background:white;border-radius:14px;padding:20px;min-width:0}}img{{width:100%;height:520px;object-fit:cover;object-position:top;border:1px solid #ddd}}
a{{color:#1657b0;overflow-wrap:anywhere}}small{{color:#576574}}p{{line-height:1.6}}</style>
<h1>多尺寸截圖比較</h1><p><a href="{escape(report['url'], quote=True)}">{escape(report['url'])}</a><br>
{escape(report['created_at'])}｜{mode}｜點圖開啟完整截圖</p>
<div class="grid">{''.join(cards)}</div>
<p>手機與平板使用 Chromium 裝置模擬；不是實體裝置或 Safari 測試。各尺寸使用獨立、未登入的瀏覽器環境。</p></html>'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?", default="https://happyebook.com/", help="預設 Happy eBook")
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器操作")
    parser.add_argument("--viewport-only", action="store_true", help="只拍第一屏，預設拍完整頁面")
    parser.add_argument("--wait-for", help="等待特定 CSS 選取器顯示，例如 .book-card")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/screenshots")
    args = parser.parse_args()
    if urlparse(args.url).scheme not in ("https", "http") or not urlparse(args.url).netloc:
        parser.error("請輸入完整 http 或 https 網址")
    now = datetime.now(timezone(timedelta(hours=8)))
    folder = args.output_dir / now.strftime("%Y%m%d_%H%M%S_%f")
    folder.mkdir(parents=True, exist_ok=True)
    report = {"url": args.url, "created_at": now.isoformat(), "full_page": not args.viewport_only,
              "screenshots": [], "errors": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        try:
            for size in SIZES:
                print(f"正在拍攝{size['label']}版：{size['width']} × {size['height']}…", flush=True)
                context = browser.new_context(
                    viewport={"width": size["width"], "height": size["height"]},
                    device_scale_factor=1, is_mobile=size["mobile"], has_touch=size["mobile"],
                    locale="zh-TW", timezone_id="Asia/Taipei", color_scheme="light",
                    reduced_motion="reduce")
                try:
                    page = context.new_page()
                    response = page.goto(args.url, wait_until="domcontentloaded", timeout=60_000)
                    if response is None or not response.ok:
                        raise RuntimeError(f"網頁回應異常：HTTP {response.status if response else '無回應'}")
                    if args.wait_for:
                        page.locator(args.wait_for).first.wait_for(state="visible", timeout=30_000)
                    prepare_page(page, not args.viewport_only)
                    metrics = page.evaluate("""() => ({
                        horizontal_overflow: Math.max(0, document.documentElement.scrollWidth - innerWidth),
                        unloaded_images: [...document.images].filter(i => !i.complete || i.naturalWidth === 0).length,
                        document_height: document.documentElement.scrollHeight,
                        viewport_width: innerWidth
                    })""")
                    filename = f"{size['name']}_{size['width']}x{size['height']}.png"
                    page.screenshot(path=str(folder / filename), full_page=not args.viewport_only,
                                    animations="disabled", timeout=30_000)
                    report["screenshots"].append({**size, **metrics, "file": filename,
                                                  "title": page.title(), "final_url": page.url})
                    print(f"  已儲存：{filename}", flush=True)
                except Exception as error:
                    report["errors"].append({"label": size["label"], "error": str(error)})
                    print(f"  拍攝失敗：{str(error).splitlines()[0]}", file=sys.stderr)
                finally:
                    context.close()
        finally:
            browser.close()
    (folder / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (folder / "index.html").write_text(gallery(report), encoding="utf-8")
    print(f"\n完成 {len(report['screenshots'])}/3 個尺寸。比較頁面：{(folder / 'index.html').resolve()}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
