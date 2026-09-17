"""Python + Playwright：查高鐵板橋→台南，預設今天 09:00–11:00 出發。"""

import argparse
import csv
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import re
import sys

from playwright.sync_api import sync_playwright, expect


TAIPEI = timezone(timedelta(hours=8))
URL = "https://www.thsrc.com.tw/ArticleContent/a3b630bb-1066-4352-a1ef-58c7b4e8ef7c"


def clock_time(value):
    if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value):
        raise argparse.ArgumentTypeError("請輸入 HH:MM，例如 09:00")
    return value


def filter_trains(table, day, start, end):
    title = table.get("Title", {})
    if title.get("StartStationName") != "板橋" or title.get("EndStationName") != "台南":
        raise ValueError("回傳站點與板橋→台南不符。")
    date_text = day.strftime("%Y/%m/%d")
    if date_text not in title.get("TitleSplit1", ""):
        raise ValueError("回傳日期與查詢日期不符。")
    items = table.get("TrainItem")
    if not isinstance(items, list):
        raise ValueError("官網班次資料格式已變更。")
    trains, seen = [], set()
    for item in items:
        if item.get("RunDate") != date_text:
            continue
        departure = item.get("DepartureTime", "")
        arrival = item.get("DestinationTime", "")
        if not re.fullmatch(r"\d{2}:\d{2}", departure) or not re.fullmatch(r"\d{2}:\d{2}", arrival):
            raise ValueError("班次出發或抵達時間格式異常。")
        if not start <= departure <= end:
            continue
        number = str(item["TrainNumber"])
        if number in seen:
            continue
        seen.add(number)
        trains.append({"train_no": number, "departure": departure, "arrival": arrival,
                       "duration": item["Duration"],
                       "non_reserved_cars": item.get("NonReservedCar", ""),
                       "note": item.get("Note", "")})
    return sorted(trains, key=lambda t: (t["departure"], t["train_no"]))


def query_trains(page, day, start, end):
    page.goto(URL, wait_until="domcontentloaded")
    # 關閉官網的 Cookie 選擇視窗。
    decline = page.get_by_role("button", name="不同意", exact=True)
    if decline.is_visible():
        decline.click()
    page.locator("#select_location01").select_option("BanQiao")
    page.locator("#select_location02").select_option("TaiNan")
    page.locator("#typesofticket").select_option("tot-1")
    page.locator("#Departdate03").fill(day.strftime("%Y/%m/%d"))
    page.locator("#outWardTime").fill(start)
    page.locator("#outWardTime").press("Tab")
    expect(page.locator("#select_location01")).to_have_value("BanQiao")
    expect(page.locator("#select_location02")).to_have_value("TaiNan")
    expect(page.locator("#Departdate03")).to_have_value(day.strftime("%Y/%m/%d"))
    expect(page.locator("#outWardTime")).to_have_value(start)
    with page.expect_response(lambda r: "/TimeTable/Search" in r.url and r.request.method == "POST") as pending:
        page.locator("#start-search").click()
    response = pending.value
    if not response.ok:
        raise RuntimeError(f"高鐵查詢失敗：HTTP {response.status}")
    result = response.json()
    if not result.get("success"):
        raise RuntimeError(f"高鐵未接受查詢：{str(result)[:400]}")

    # 官網只顯示每頁 5 班，但 app.timetableData 保存完整查詢結果。
    # 讀取此資料後自行篩选結束時間，避免漏掉第二頁的班次。
    page.wait_for_function("typeof app !== 'undefined' && app.timetableData && app.timetableData.DepartureTable")
    table = page.evaluate("() => app.timetableData.DepartureTable")
    return filter_trains(table, day, start, end)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", type=date.fromisoformat, help="YYYY-MM-DD，預設台灣時間今天")
    parser.add_argument("--start", type=clock_time, default="09:00")
    parser.add_argument("--end", type=clock_time, default="11:00")
    parser.add_argument("--headed", action="store_true", help="顯示瀏覽器視窗")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/transport/thsr")
    args = parser.parse_args()
    if args.start > args.end:
        parser.error("開始時間不可晚於結束時間；請查詢同日出發時段。")
    day = args.date or datetime.now(TAIPEI).date()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    base = args.output_dir / f"banqiao_tainan_{day}_{args.start.replace(':', '')}_{args.end.replace(':', '')}"
    print(f"查詢 {day} 高鐵板橋→台南，{args.start}–{args.end} 出發…", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not args.headed)
        try:
            page = browser.new_page(locale="zh-TW", timezone_id="Asia/Taipei", viewport={"width": 1440, "height": 1000})
            page.set_default_timeout(30_000)
            page.set_default_navigation_timeout(60_000)
            try:
                trains = query_trains(page, day, args.start, args.end)
            except Exception:
                error_path = base.with_suffix(".error.html")
                error_path.write_text(page.content(), encoding="utf-8")
                print(f"查詢失敗，頁面已儲存：{error_path.resolve()}", file=sys.stderr)
                raise
        finally:
            browser.close()
    report = {"date": str(day), "from": "高鐵板橋", "to": "高鐵台南",
              "departure_start": args.start, "departure_end": args.end,
              "queried_at": datetime.now(TAIPEI).isoformat(), "source": URL, "trains": trains}
    base.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with base.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=["train_no", "departure", "arrival", "duration", "non_reserved_cars", "note"])
        writer.writeheader()
        writer.writerows(trains)
    print(f"\n共 {len(trains)} 班（班次查詢不代表尚有座位）：")
    for train in trains:
        print(f"{train['train_no']}  {train['departure']} → {train['arrival']}  行車 {train['duration']}  自由座車廂 {train['non_reserved_cars']}")
    print(f"\n已儲存：{base.with_suffix('.csv').resolve()}\n        {base.with_suffix('.json').resolve()}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}", file=sys.stderr)
        raise SystemExit(1)
