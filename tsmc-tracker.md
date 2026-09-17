# 台積電價格追蹤範例

用 Python 3.10+ 與 Playwright 取得證交所台積電（上市 2330）行情，保存紀錄，與**上一次成功保存的成交價**比較並標示下跌、上漲、持平。第一次執行只建立基準，並非與昨收比較。

```bash
python -m pip install playwright
python examples/04_tracking/tsmc_price_tracker.py
```

本專案執行：

```bash
.venv/bin/python examples/04_tracking/tsmc_price_tracker.py
# 每 60 秒查詢一次，Ctrl+C 停止
.venv/bin/python examples/04_tracking/tsmc_price_tracker.py --watch
# 每 30 秒查詢一次，共查 5 次
.venv/bin/python examples/04_tracking/tsmc_price_tracker.py --watch --interval 30 --count 5
```

使用 Playwright APIRequestContext，無須登入、API 金鑰或安裝 Chromium。此程式只讀取行情及寫入本機檔案。

輸出預設在專案根目錄的 `outputs/stocks/tsmc/`，可用 `--output-dir` 變更：

- `tsmc_history.sqlite3`：持續累積的有效紀錄，下次執行沿用。
- `tsmc_history.csv`：完整歷史，UTF-8 BOM，可在 Excel 開啟。
- `tsmc_report.html`：最近 200 筆紀錄，綠色標示下跌、紅色標示上漲；瀏覽器開啟後可重新整理。

行情可能延遲，會同時記錄查詢時間與來源行情時間。接受今天的正式成交價 `z`；若該快照沒有成交價，但來源提供最近一筆正式成交 `trade.z`，則使用該筆價格與 `trade.t` 時間。不以委買、委賣、昨收或試撮價替代。盤前、休市、兩處均缺價、舊日期、試撮行情不新增紀錄；同一行情時間不重複記錄。不同日期執行會與上次保留的有效紀錄比較，報告可看到兩筆各自的日期時間。

一般執行一次後結束，不會自動安裝排程。`--watch` 會持續執行，即使休市也會顯示原因並依間隔再查；可隨時 Ctrl+C 結束。資料保存於 SQLite，不要刪除資料庫，否則下次將重新建立基準。

來源：[證交所基本市況報導](https://mis.twse.com.tw/stock/index.jsp)。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
