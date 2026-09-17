# 今日台股開盤漲幅排行

Python 3.10+ 與 Playwright。預設只查上市公司名冊中的四位數普通股，依**今日開盤價相對行情昨收參考價的漲幅百分比**由大到小排列，列出前 20 名開高股票。不是股價上漲金額排行，也不是即時成交價漲幅排行。同漲幅以代號排序。

```bash
python -m pip install playwright
python examples/03_data_queries/stock_open_gainers.py
```

本專案執行：

```bash
.venv/bin/python examples/03_data_queries/stock_open_gainers.py
.venv/bin/python examples/03_data_queries/stock_open_gainers.py --market tse --top 10
.venv/bin/python examples/03_data_queries/stock_open_gainers.py --market otc --top 30
.venv/bin/python examples/03_data_queries/stock_open_gainers.py --market all --codes 2330 2317 6488
.venv/bin/python examples/03_data_queries/stock_open_gainers.py --wait-open
```

`--codes` 只會比較指定股票，不代表全市場排行。`--output-dir` 可修改預設 `stock_output` 目錄。CSV 使用 UTF-8 BOM，方便以 Excel 開啟；JSON 額外包含時間、掃描數、排除原因與資料缺漏。同一天、同模式再次執行會更新同名檔案。

09:00 前執行會清楚顯示尚未開盤，不查詢也不寫入空排行。加上 `--wait-open` 會等到當天 09:01 再查一次，可按 Ctrl+C 取消。此選項不會建立每日排程，也不保證當天是交易日；休市或個股延後開盤仍可能沒有資料。09:00 後執行則立即查詢。

資料來源為證交所及櫃買中心公開公司名冊，以及證交所基本市況報導 MIS 的 `getStockInfo.jsp`。使用 Playwright 的 APIRequestContext，不需要啟動 Chromium 或登入。每批最多查 50 檔，批次間隔 0.3 秒，失敗最多嘗試三次。

- 日期使用台灣 UTC+8，僅接受 `d` 為今天且 `o`（開盤價）、`v`（累計成交量）有效的行情。
- 計算公式：`(o / y - 1) × 100%`，`y` 採 MIS 提供的昨收參考欄位。除權息、減資或特殊交易日，參考基準可能調整，不能視為未調整的前一日實際收盤價報酬率。
- 不使用最新價 `z`、試撮價 `pz` 代替開盤價。盤前、休市、尚未成交或來源未更新時，不把昨日資料充作今日排行。
- 新上市、停牌及資料未完整回傳的股票可能缺資料；輸出會標示掃描範圍及排除數量。行情分批取得，尚未開盤的股票稍後可能加入排行。資料來源可能延遲，亦可能變更介面。
- 名冊不含 ETF、權證與特別股；不保證當天新增公司已出現在公開名冊中。

每天需要更新時執行一次即可。建議開盤後執行，例如 09:05；尚未開盤的股票可稍後重跑。結束碼 0 為查詢完成（可包含尚無今日開盤），1 為無法取得資料，2 為參數錯誤或部分行情不完整。

來源入口：[證交所 OpenAPI](https://openapi.twse.com.tw/)、[櫃買中心 OpenAPI](https://www.tpex.org.tw/openapi/)、[證交所基本市況報導](https://mis.twse.com.tw/stock/index.jsp)。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
