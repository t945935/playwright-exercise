"""用 Python + Playwright 查臺鐵彰化→嘉義直達班次，預設今天 08:00–10:00 出發。"""

import argparse
import csv
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright, expect


TAIPEI = timezone(timedelta(hours=8))
URL = "https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/gobytime?lang=ZH_TW"


def clock_time(value):
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise argparse.ArgumentTypeError("時間請使用 HH:MM，例如 08:00")
    if value[-2:] not in ("00", "30") and value != "23:59":
        raise argparse.ArgumentTypeError("官網時段以半小時為單位，另可選 23:59")
    return value


def query_trains(page, day, start, end):
    page.goto(URL, wait_until="domcontentloaded")
    cookie = page.get_by_role("button", name="接受並關閉", exact=True)
    if cookie.is_visible():
        cookie.click()

    form = page.locator("#queryForm")
    form.locator("#startStation").fill("3360-彰化")
    form.locator("#endStation").fill("4080-嘉義")
    form.locator("#rideDate").fill(day.strftime("%Y/%m/%d"))
    form.get_by_role("radio", name="限直達", exact=True).check()
    form.get_by_role("radio", name="查詢出發時間", exact=True).check()
    form.get_by_role("radio", name="全部", exact=True).check()
    form.get_by_role("radio", name="一般", exact=True).check()
    form.locator("#startTime").select_option(start)
    form.locator("#endTime").select_option(end)
    with page.expect_navigation(wait_until="domcontentloaded"):
        form.get_by_role("button", name="查詢", exact=True).click()

    # 確認回應仍是指定的日期及站點，避免把錯誤頁當成無班次。
    expect(page.locator("#startStation")).to_have_value("3360-彰化")
    expect(page.locator("#endStation")).to_have_value("4080-嘉義")
    expect(page.locator("#rideDate")).to_have_value(day.strftime("%Y/%m/%d"))
    expect(page.locator("#startTime")).to_have_value(start)
    expect(page.locator("#endTime")).to_have_value(end)
    rows = page.locator("table.itinerary-controls > tbody > tr.trip-column")
    if not rows.count():
        body = page.locator("body").inner_text()
        if re.search(r"查無.*(?:車次|資料)|無符合.*(?:車次|資料)", body):
            return []
        raise RuntimeError("未找到班次表格，也未找到明確的無班次訊息；請查看儲存的頁面。")

    results = []
    for row in rows.all():
        cells = row.locator(":scope > td").all_inner_texts()
        if len(cells) != 10:
            raise RuntimeError("班次表格欄位已變更，請檢查解析方式。")
        link = row.locator(".train-number a.links")
        title = link.inner_text().strip()
        detail_url = link.evaluate("a => a.href")
        params = parse_qs(urlparse(detail_url).query)
        train_no = params["trainNo"][0]
        if params.get("rideDate") != [day.strftime("%Y/%m/%d")]:
            raise RuntimeError("列車日期與指定查詢日期不符。")
        departure, arrival = cells[1].strip(), cells[2].strip()
        if not re.fullmatch(r"\d{2}:\d{2}", departure) or not start <= departure <= end:
            raise RuntimeError(f"出發時間不在指定範圍：{departure}")
        results.append({
            "train_no": train_no,
            "train_type": title.removesuffix(train_no).strip(),
            "departure": departure, "arrival": arrival,
            # 原樣保留官網行駛時間（可能與分鐘相減有捨入差異）。
            "duration": cells[3].strip(), "route": cells[4].strip(),
            "adult_fare": cells[6].strip(), "detail_url": detail_url,
        })
    return sorted(results, key=lambda row: (row["departure"], row["train_no"]))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=date.fromisoformat, help="YYYY-MM-DD，預設台灣時間今天")
    parser.add_argument("--start", type=clock_time, default="08:00")
    parser.add_argument("--end", type=clock_time, default="10:00")
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器視窗")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/transport/tra")
    args = parser.parse_args()
    if args.start > args.end:
        parser.error("開始時間不可晚於結束時間；本程式查詢同日出發時段。")
    day = args.date or datetime.now(TAIPEI).date()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = args.output_dir / f"changhua_chiayi_{day}_{args.start.replace(':', '')}_{args.end.replace(':', '')}"
    print(f"查詢 {day} 彰化→嘉義，{args.start}–{args.end} 出發的直達班次…", flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        try:
            page = browser.new_page(locale="zh-TW", timezone_id="Asia/Taipei")
            page.set_default_timeout(30_000)
            page.set_default_navigation_timeout(60_000)
            try:
                trains = query_trains(page, day, args.start, args.end)
            except Exception:
                error_path = base.with_suffix(".error.html")
                error_path.write_text(page.content(), encoding="utf-8")
                print(f"查詢失敗，頁面已存至 {error_path.resolve()}", file=sys.stderr)
                raise
        finally:
            browser.close()

    report = {"date": str(day), "from": "彰化", "to": "嘉義",
              "departure_start": args.start, "departure_end": args.end,
              "direct_only": True, "source": URL,
              "queried_at": datetime.now(TAIPEI).isoformat(), "trains": trains}
    base.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["train_no", "train_type", "departure", "arrival", "duration", "route", "adult_fare", "detail_url"]
    with base.with_suffix(".csv").open("w", newline="", encoding="utf-8-sig") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(trains)
    print(f"\n共 {len(trains)} 班（時刻表不代表尚有座位）：")
    for train in trains:
        print(f"{train['departure']} → {train['arrival']}  {train['train_type']} {train['train_no']}  "
              f"{train['duration']}  {train['route']}  全票 {train['adult_fare']}")
    print(f"\n已儲存：{base.with_suffix('.csv').resolve()}\n        {base.with_suffix('.json').resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}", file=sys.stderr)
        raise SystemExit(1)
