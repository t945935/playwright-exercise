"""Python + Playwright：台股今日開盤漲幅排行（上市／上櫃普通股）。"""

import argparse
from collections import Counter
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import csv
import json
from pathlib import Path
import re
import sys
import time

from playwright.sync_api import Error as PlaywrightError, sync_playwright


TAIPEI = timezone(timedelta(hours=8), "Asia/Taipei")
MIS = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
MARKETS = {
    "tse": ("上市", "https://openapi.twse.com.tw/v1/opendata/t187ap03_L", "公司代號", "公司簡稱"),
    "otc": ("上櫃", "https://www.tpex.org.tw/openapi/v1/mopsfin_t187ap03_O", "SecuritiesCompanyCode", "CompanyAbbreviation"),
}


def get_json(request, url, params=None):
    for attempt in range(3):
        try:
            response = request.get(url, params=params, timeout=20_000)
            try:
                if not response.ok:
                    raise ValueError(f"HTTP {response.status}")
                return response.json()
            finally:
                response.dispose()
        except (PlaywrightError, ValueError):
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def positive_number(value):
    try:
        result = Decimal(str(value).replace(",", ""))
        return result if result.is_finite() and result > 0 else None
    except InvalidOperation:
        return None


def opening_record(quote, today):
    """只接受今天已成交的開盤價；不使用 z 最新價或 pz 試撮價。"""
    if quote.get("d") != today:
        return None, "非今日行情"
    opening = positive_number(quote.get("o"))
    if opening is None or positive_number(quote.get("v")) is None:
        return None, "尚無有效開盤成交"
    previous = positive_number(quote.get("y"))
    if previous is None:
        return None, "缺少昨收參考價"
    gain = (opening - previous) / previous * 100
    return {
        "code": quote["c"], "name": quote.get("n", ""),
        "market": MARKETS[quote["ex"]][0], "date": quote["d"],
        "open": float(opening), "previous_close_reference": float(previous),
        "opening_change": float(opening - previous),
        # 先用完整精度排序，最後才四捨五入輸出。
        "opening_gain_pct": gain, "quote_time": quote.get("t", ""),
    }, None


def rank_records(records, limit):
    records = sorted((r for r in records if r["opening_gain_pct"] > 0),
                     key=lambda r: (-r["opening_gain_pct"], r["code"]))
    result = []
    for index, record in enumerate(records[:limit], 1):
        result.append({"rank": index, **record,
                       "opening_gain_pct": round(float(record["opening_gain_pct"]), 4)})
    return result


def ready_to_query(wait_open):
    now = datetime.now(TAIPEI)
    opening = now.replace(hour=9, minute=0, second=0, microsecond=0)
    if now >= opening:
        return True
    print(f"現在是台灣時間 {now:%Y-%m-%d %H:%M:%S}，尚未到一般交易日 09:00 開盤時間。", flush=True)
    print("目前沒有今日正式開盤價，盤前試撮價不能用來計算開盤排行。", flush=True)
    if not wait_open:
        print("請於開盤後重跑，或加上 --wait-open 等到今天 09:01 自動查詢。")
        print("此次未查詢、未產生或更新排行檔案。")
        return False
    target = opening + timedelta(minutes=1)
    print("等待今天 09:01 再查詢；如遇休市，仍可能沒有資料。按 Ctrl+C 可取消。", flush=True)
    while True:
        remaining = (target - datetime.now(TAIPEI)).total_seconds()
        if remaining <= 0:
            return True
        print(f"距離查詢約 {int(remaining) + 1} 秒…", flush=True)
        time.sleep(min(30, remaining))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--market", choices=["all", "tse", "otc"], default="tse",
                        help="市場：tse 上市（預設）、otc 上櫃、all 兩者")
    parser.add_argument("--top", type=int, default=20, help="列出前幾名（預設 20）")
    parser.add_argument("--codes", nargs="+", help="只查指定代號；不加此參數則查整個市場")
    parser.add_argument("--wait-open", action="store_true", help="盤前執行時，等到今天 09:01 再查詢")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/stocks/opening")
    args = parser.parse_args()
    if args.top < 1:
        parser.error("--top 必須大於 0")
    if not ready_to_query(args.wait_open):
        return 0
    started = datetime.now(TAIPEI)
    today = started.strftime("%Y%m%d")
    markets = list(MARKETS) if args.market == "all" else [args.market]
    companies, errors, skipped, records = {}, [], Counter(), []
    batches_ok = 0
    with sync_playwright() as p:
        request = p.request.new_context(extra_http_headers={
            "Referer": "https://mis.twse.com.tw/stock/index.jsp",
        })
        try:
            for market in markets:
                label, url, code_key, name_key = MARKETS[market]
                print(f"讀取{label}公司名冊…", flush=True)
                try:
                    listing = get_json(request, url)
                    if not isinstance(listing, list) or not listing:
                        raise ValueError("公司名冊格式異常或為空")
                    if code_key not in listing[0]:
                        raise ValueError("公司名冊缺少代號欄位")
                    for item in listing:
                        code = str(item.get(code_key, "")).strip()
                        # 公司名冊普通股代號；排除 ETF、權證與特別股。
                        if re.fullmatch(r"[1-9]\d{3}", code):
                            companies[(market, code)] = item.get(name_key, "")
                except (PlaywrightError, ValueError) as error:
                    errors.append(f"{label}名冊失敗：{str(error).splitlines()[0]}")
            if args.codes:
                unknown = set(args.codes) - {code for _, code in companies}
                if unknown:
                    errors.append("指定代號不在成功讀取的市場名冊：" + ", ".join(sorted(unknown)))
                companies = {key: value for key, value in companies.items() if key[1] in args.codes}
            keys = list(companies)
            for offset in range(0, len(keys), 50):
                batch = keys[offset:offset + 50]
                print(f"讀取行情 {offset + 1}–{offset + len(batch)} / {len(keys)}", flush=True)
                try:
                    data = get_json(request, MIS, {
                        "ex_ch": "|".join(f"{market}_{code}.tw" for market, code in batch),
                        "json": "1", "delay": "0", "_": str(time.time_ns()),
                    })
                    if not isinstance(data, dict) or data.get("rtcode") != "0000" or not isinstance(data.get("msgArray"), list):
                        raise ValueError("行情回應格式異常或服務拒絕查詢")
                    received = set()
                    for quote in data["msgArray"]:
                        key = (quote.get("ex"), quote.get("c"))
                        if key not in batch or key in received:
                            continue
                        received.add(key)
                        record, reason = opening_record(quote, today)
                        if reason:
                            skipped[reason] += 1
                        else:
                            records.append(record)
                    missing = len(batch) - len(received)
                    skipped["未回傳行情"] += missing
                    if missing:
                        errors.append(f"第 {offset // 50 + 1} 批缺少 {missing} 檔行情")
                    batches_ok += 1
                except (PlaywrightError, ValueError) as error:
                    skipped["查詢失敗"] += len(batch)
                    errors.append(f"第 {offset // 50 + 1} 批失敗：{str(error).splitlines()[0]}")
                if offset + 50 < len(keys):
                    time.sleep(0.3)
        finally:
            request.dispose()

    if not batches_ok:
        print("\n沒有成功取得行情，未寫入排行。", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    if datetime.now(TAIPEI).date() != started.date():
        print("查詢跨越午夜，請重新執行以取得同一天行情。", file=sys.stderr)
        return 1
    rows = rank_records(records, args.top)
    status = "partial" if errors else "ok"
    if not records:
        status = "no_today_open"
        message = "尚無今日有效開盤資料：可能尚未開盤、休市或來源尚未更新。"
    elif not rows:
        message = "有效行情中，沒有開盤價高於昨收參考價的股票。"
    else:
        message = "今日開盤漲幅排行" + ("（部分資料缺漏）" if errors else "")
    report = {
        "date": started.date().isoformat(), "timezone": "Asia/Taipei",
        "started_at": started.isoformat(), "finished_at": datetime.now(TAIPEI).isoformat(),
        "market": args.market, "requested_codes": args.codes,
        "formula": "(開盤價 o / 昨收參考價 y - 1) × 100%",
        "source": MIS, "status": status, "message": message,
        "universe_count": len(companies), "valid_open_count": len(records),
        "positive_open_count": sum(r["opening_gain_pct"] > 0 for r in records),
        "skipped": dict(skipped), "errors": errors, "ranking": rows,
    }
    args.output_dir.mkdir(parents=True, exist_ok=True)
    suffix = "selected" if args.codes else args.market
    base = args.output_dir / f"opening_gainers_{today}_{suffix}"
    base.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["rank", "code", "name", "market", "date", "open", "previous_close_reference", "opening_change", "opening_gain_pct", "quote_time"]
    with base.with_suffix(".csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n{report['date']} {message}")
    print(f"名冊 {len(companies)} 檔；有效開盤 {len(records)} 檔；開高 {report['positive_open_count']} 檔")
    for row in rows:
        print(f"{row['rank']:>2}. {row['code']} {row['name']} ({row['market']}) "
              f"開盤 {row['open']:g}／昨收參考 {row['previous_close_reference']:g} "
              f"{row['opening_gain_pct']:+.2f}%")
    for error in errors:
        print(f"警告：{error}", file=sys.stderr)
    print(f"\n輸出：{base.with_suffix('.json').resolve()}\n      {base.with_suffix('.csv').resolve()}")
    return 2 if errors else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已取消。", file=sys.stderr)
        raise SystemExit(130)
