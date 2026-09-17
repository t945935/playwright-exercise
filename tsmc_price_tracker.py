"""Playwright + Python：追蹤台積電 2330，每次與上次有效成交價比較。"""

import argparse
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from html import escape
from pathlib import Path
import sqlite3
import sys
import time

from playwright.sync_api import sync_playwright


TAIPEI = timezone(timedelta(hours=8))
API = "https://mis.twse.com.tw/stock/api/getStockInfo.jsp"
FIELDS = ["checked_at", "quote_at", "price", "previous_price", "change", "change_pct", "status"]
LABELS = {"first": "首次紀錄", "down": "下跌（降價）", "up": "上漲", "same": "持平"}


def positive(value):
    try:
        number = Decimal(str(value).replace(",", ""))
        return number if number.is_finite() and number > 0 else None
    except InvalidOperation:
        return None


def parse_quote(data, now):
    if not isinstance(data, dict) or data.get("rtcode") != "0000":
        raise ValueError("證交所未成功回傳行情")
    quotes = [q for q in data.get("msgArray", []) if q.get("c") == "2330" and q.get("ex") == "tse"]
    if len(quotes) != 1:
        raise ValueError("找不到台積電行情")
    quote = quotes[0]
    if quote.get("d") != now.strftime("%Y%m%d"):
        raise ValueError(f"來源行情日期為 {quote.get('d')}，不是今天；可能休市或尚未更新")
    if quote.get("ts") == "1":
        raise ValueError("來源正提供試撮行情，暫不記錄")
    price = positive(quote.get("z"))
    trade_time = quote.get("t", "")
    # 此次快照無成交時，MIS 可能另外回傳最近一筆正式成交 trade。
    # 使用該筆成交自己的時間，不能把快照更新時間當成成交時間。
    if price is None:
        trade = quote.get("trade") or {}
        if positive(trade.get("v")) is not None:
            price = positive(trade.get("z"))
            trade_time = trade.get("t", "")
    if price is None or positive(quote.get("o")) is None or positive(quote.get("v")) is None:
        raise ValueError("目前未回傳有效正式成交價，保留上次有效紀錄，稍後再查")
    stamp = datetime.strptime(quote["d"] + " " + trade_time, "%Y%m%d %H:%M:%S").replace(tzinfo=TAIPEI)
    if stamp > now + timedelta(seconds=60):
        raise ValueError("行情時間晚於目前時間，請檢查系統時鐘")
    return stamp.isoformat(), price


def init_db(connection):
    connection.execute("""CREATE TABLE IF NOT EXISTS observations (
        id INTEGER PRIMARY KEY, checked_at TEXT NOT NULL, quote_at TEXT NOT NULL,
        price TEXT NOT NULL, previous_price TEXT, change TEXT, change_pct TEXT,
        status TEXT NOT NULL)""")


def save_observation(connection, quote_at, price, checked_at):
    # 單一交易內讀取上次價格並新增紀錄，避免兩個執行程序互相覆蓋。
    connection.execute("BEGIN IMMEDIATE")
    try:
        last = connection.execute("SELECT quote_at, price FROM observations ORDER BY id DESC LIMIT 1").fetchone()
        if last and quote_at < last[0]:
            raise ValueError("來源回傳比上次更舊的行情，略過此筆")
        if last and quote_at == last[0]:
            if price == Decimal(last[1]):
                connection.rollback()
                return None
            raise ValueError("同一行情時間回傳不同價格，暫不記錄")
        previous = Decimal(last[1]) if last else None
        change = price - previous if previous is not None else None
        pct = change / previous * 100 if previous is not None else None
        status = "first" if previous is None else "down" if change < 0 else "up" if change > 0 else "same"
        record = dict(zip(FIELDS, [checked_at, quote_at, str(price),
            str(previous) if previous is not None else None,
            str(change) if change is not None else None,
            str(pct.quantize(Decimal('0.0001'))) if pct is not None else None, status]))
        connection.execute("INSERT INTO observations (" + ",".join(FIELDS) + ") VALUES (?,?,?,?,?,?,?)", list(record.values()))
        connection.commit()
        return record
    except Exception:
        connection.rollback()
        raise


def export_history(connection, folder):
    rows = connection.execute("SELECT " + ",".join(FIELDS) + " FROM observations ORDER BY id DESC").fetchall()
    with (folder / "tsmc_history.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(FIELDS)
        writer.writerows(rows)
    body = []
    for row in rows[:200]:
        values = list(row)
        status = values[-1]
        values[-1] = LABELS[status]
        body.append(f'<tr class="{status}">' + ''.join(f'<td>{escape(str(v)) if v is not None else "—"}</td>' for v in values) + '</tr>')
    headers = ["查詢時間", "行情時間", "價格（元）", "上次價格", "差額", "變動 %", "結果"]
    html = '''<!doctype html><html lang="zh-Hant"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>台積電價格追蹤</title>
<style>body{font:16px system-ui;margin:32px;color:#1f2937}table{border-collapse:collapse;white-space:nowrap}
td,th{padding:12px;border-bottom:1px solid #ddd;text-align:left}.down{background:#e6f4ea}.up{background:#fce8e6}
.first{background:#e8f0fe}.scroll{overflow:auto}p{line-height:1.7}</style>
<h1>台積電（2330）價格追蹤</h1><p>比較上一次有效紀錄；首次只建立基準。<br>
下跌標綠色，上漲標紅色。顯示最近 200 筆；全部紀錄存於 CSV。行情可能延遲，請查看行情時間。</p>
<p>來源：<a href="https://mis.twse.com.tw/stock/index.jsp">證交所基本市況報導</a>。
重新執行或監看程式後，重新整理此頁查看最新結果。</p><div class="scroll"><table><thead><tr>'''
    html += ''.join(f"<th>{h}</th>" for h in headers) + "</tr></thead><tbody>" + ''.join(body) + "</tbody></table></div></html>"
    (folder / "tsmc_report.html").write_text(html, encoding="utf-8")


def fetch_quote(request):
    response = request.get(API, params={"ex_ch": "tse_2330.tw", "json": "1", "delay": "0", "_": str(time.time_ns())}, timeout=20_000)
    try:
        if not response.ok:
            raise RuntimeError(f"行情來源 HTTP {response.status}")
        return response.json()
    finally:
        response.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="store_true", help="持續追蹤；按 Ctrl+C 停止")
    parser.add_argument("--interval", type=int, default=60, help="監看間隔秒數，至少 30（預設 60）")
    parser.add_argument("--count", type=int, default=0, help="監看查詢次數，0 表示持續執行")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parents[2] / "outputs/stocks/tsmc")
    args = parser.parse_args()
    if args.interval < 30 or args.count < 0:
        parser.error("interval 須至少 30 秒，count 不可小於 0")
    if args.count and not args.watch:
        parser.error("--count 需搭配 --watch")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(args.output_dir / "tsmc_history.sqlite3", timeout=30)
    init_db(connection)
    print("追蹤台積電（2330），與上次有效紀錄比較。", flush=True)
    failures, attempts = 0, 0
    try:
        with sync_playwright() as p:
            request = p.request.new_context(extra_http_headers={"Referer": "https://mis.twse.com.tw/stock/index.jsp"})
            try:
                while True:
                    attempts += 1
                    try:
                        data = fetch_quote(request)
                        now = datetime.now(TAIPEI)
                        quote_at, price = parse_quote(data, now)
                        row = save_observation(connection, quote_at, price, now.isoformat())
                        export_history(connection, args.output_dir)
                        print(f"行情 {quote_at}｜台積電 {price:,.2f} 元", flush=True)
                        if row is None:
                            print("行情尚未更新，不重複新增紀錄。", flush=True)
                        elif row["status"] == "first":
                            print("首次紀錄，已建立比較基準；下次執行會與此價格比較。", flush=True)
                        else:
                            print(f"{LABELS[row['status']]}｜上次 {Decimal(row['previous_price']):,.2f} 元 → 本次 {price:,.2f} 元｜"
                                  f"差額 {Decimal(row['change']):+.2f} 元（{Decimal(row['change_pct']):+.2f}%）", flush=True)
                        print(f"報告：{(args.output_dir / 'tsmc_report.html').resolve()}", flush=True)
                    except Exception as error:
                        failures += 1
                        print(f"本次未完成：{error}。未取得有效行情時不更新比較基準。", file=sys.stderr, flush=True)
                    if not args.watch or (args.count and attempts >= args.count):
                        break
                    time.sleep(args.interval)
            finally:
                request.dispose()
    finally:
        connection.close()
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("\n已停止追蹤，歷史紀錄已保留。")
