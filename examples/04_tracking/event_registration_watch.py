"""Python + Playwright：監看活動報名按鈕，開放報名時發出本機提醒。"""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


TAIPEI = timezone(timedelta(hours=8))


def read_status(page, selector, open_text, closed_texts):
    target = page.locator(selector)
    # 指定區塊須唯一；不掃整頁，以免誤讀其他活動或歷史說明。
    target.first.wait_for(state="attached", timeout=15_000)
    if target.count() != 1:
        raise ValueError("選取器必須只對應一個報名按鈕或狀態區塊")
    if not target.is_visible():
        return "unknown", "報名區塊目前不可見"
    text = " ".join(target.inner_text().split())
    if not text:
        text = target.get_attribute("value") or target.get_attribute("aria-label") or ""
    if any(word in text for word in closed_texts):
        return "closed", text
    if open_text in text:
        if not target.is_enabled() or target.get_attribute("aria-disabled") == "true":
            return "closed", text + "（按鈕停用）"
        return "open", text
    return "unknown", text


def save_json(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def update_state(path, status, text, config):
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    last_known = previous.get("last_known")
    # 首次已開放也提醒；未知狀態不抹除上次已知狀態，避免重複通知。
    alert = status == "open" and last_known != "open"
    if status in ("open", "closed"):
        last_known = status
    state = {"checked_at": datetime.now(TAIPEI).isoformat(), "status": status,
             "last_known": last_known, "text": text, "config": config}
    save_json(path, state)
    return alert, state


def notify(title, url):
    print(f"\a\n🔔 {title}：已偵測到可報名狀態\n{url}\n", flush=True)
    command = shutil.which("notify-send")
    if command:
        try:
            subprocess.run([command, "--", "活動報名提醒", f"{title}\n{url}"],
                           check=True, timeout=5, capture_output=True)
            return
        except (subprocess.SubprocessError, OSError):
            pass
    print("此環境未能顯示桌面通知，請查看終端機與提醒紀錄。", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="要追蹤的活動頁網址")
    parser.add_argument("--selector", required=True, help="唯一的報名按鈕或狀態區塊 CSS 選取器")
    parser.add_argument("--open-text", default="立即報名", help="開放時會出現的文字")
    parser.add_argument("--closed-text", action="append", help="關閉狀態文字，可重複設定")
    parser.add_argument("--name", default="活動", help="通知中顯示的活動名稱")
    parser.add_argument("--watch", action="store_true", help="持續監看，Ctrl+C 結束")
    parser.add_argument("--interval", type=int, default=300, help="查詢間隔秒數，至少 60，預設 300")
    parser.add_argument("--count", type=int, default=0, help="監看次數；0 為持續監看")
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器視窗")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/events")
    args = parser.parse_args()
    if urlparse(args.url).scheme not in ("https", "http"):
        parser.error("請使用 http 或 https 活動網址")
    if args.interval < 60 or args.count < 0 or (args.count and not args.watch):
        parser.error("interval 至少 60；count 不可為負且需搭配 --watch")
    if not args.open_text.strip() or not args.selector.strip():
        parser.error("選取器與開放文字不可空白")
    closed = args.closed_text or ["尚未開放", "尚未開始", "額滿", "已結束", "截止", "售完"]
    if any(not word.strip() or word in args.open_text for word in closed):
        parser.error("關閉文字不可空白或與開放文字衝突")
    config = {"url": args.url, "selector": args.selector, "open_text": args.open_text, "closed_texts": closed}
    key = hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[:16]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    state_path = args.output_dir / f"{key}.json"
    print(f"監看：{args.name}\n網址：{args.url}\n狀態檔：{state_path}", flush=True)
    failures, attempt = 0, 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        try:
            page = browser.new_page(locale="zh-TW", viewport={"width": 1440, "height": 1000})
            while True:
                attempt += 1
                try:
                    response = page.goto(args.url, wait_until="domcontentloaded", timeout=45_000)
                    if response is None or not response.ok:
                        raise RuntimeError(f"活動頁載入失敗：HTTP {response.status if response else '無回應'}")
                    status, text = read_status(page, args.selector, args.open_text, closed)
                    alert, state = update_state(state_path, status, text, config)
                    print(f"{state['checked_at']}｜{status}｜{text}", flush=True)
                    if alert:
                        with (args.output_dir / "alerts.jsonl").open("a", encoding="utf-8") as stream:
                            stream.write(json.dumps({**state, "name": args.name}, ensure_ascii=False) + "\n")
                        notify(args.name, args.url)
                    if status == "unknown":
                        print("尚不能判斷報名狀態；請確認文字及選取器，必要時使用 --headed 查看。", flush=True)
                except Exception as error:
                    failures += 1
                    print(f"查詢失敗：{str(error).splitlines()[0]}；保留原有狀態。", file=sys.stderr, flush=True)
                if not args.watch or (args.count and attempt >= args.count):
                    break
                # 可隨時 Ctrl+C 結束；每輪重新載入頁面。
                time.sleep(args.interval)
        finally:
            browser.close()
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已停止監看，狀態及提醒紀錄已保留。")
