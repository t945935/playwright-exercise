# 彰化至嘉義臺鐵班次

正式程式命名為 `tra_changhua_chiayi.py`，查詢彰化至嘉義；根目錄舊檔名 `tra_banqiao_tainan.py` 保留為相容入口。

Python 3.10+，使用 Playwright 實際開啟臺鐵官方時刻表、填寫查詢表單，擷取直達班次。預設日期是台灣時間今天，時段是 **08:00–10:00 從彰化出發**，抵達站為嘉義。

```bash
python -m pip install playwright
python -m playwright install chromium
python examples/03_data_queries/tra_changhua_chiayi.py
```

本專案可直接執行：

```bash
.venv/bin/python examples/03_data_queries/tra_changhua_chiayi.py
```

指定日期、時段或顯示操作視窗：

```bash
python examples/03_data_queries/tra_changhua_chiayi.py --date 2026-09-18 --start 08:00 --end 10:00 --headed
```

時間需使用 HH:MM，依官網選項以半小時為單位（另可使用 23:59）。日期須在官網開放查詢範圍內。程式查詢全部車種、一般票種、限直達；不包括轉乘組合，不會進行訂票。

結果顯示車次、車種、出發及抵達時間、官網行駛時間、經由路線、全票票價與列車詳情連結，並存於 `outputs/transport/tra/` 的 CSV、JSON。CSV 可用 Excel 開啟；`--output-dir` 可改存檔目錄。相同查詢重跑會更新同名檔案。

連線、頁面格式或表單驗證失敗時會明確報錯；若瀏覽器已開啟，會盡可能儲存 `.error.html` 供檢查，不把抓取失敗宣稱為零班次。可加 `--headed` 查看官網當時顯示的訊息。

班次及票價以查詢時的[臺鐵官方時刻表](https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip112/gobytime?lang=ZH_TW)為準；有班次不代表有剩餘座位。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
