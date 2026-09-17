# 高鐵板橋至台南班次（Python + Playwright）

預設查詢台灣時間今天 **09:00–11:00 從高鐵板橋出發、抵達高鐵台南**的班次，包含起訖時間邊界。這兩站均為高鐵車站。

安裝（Python 3.10+）：

```bash
python -m pip install playwright
python -m playwright install chromium
```

執行：

```bash
python examples/03_data_queries/thsr_banqiao_tainan.py
# 本專案的虛擬環境
.venv/bin/python examples/03_data_queries/thsr_banqiao_tainan.py
# 指定日期、時段並顯示瀏覽器
python examples/03_data_queries/thsr_banqiao_tainan.py --date 2026-09-18 --start 09:00 --end 11:00 --headed
```

程式開啟[高鐵官方時刻表](https://www.thsrc.com.tw/ArticleContent/a3b630bb-1066-4352-a1ef-58c7b4e8ef7c)，選擇站點、日期及時間並按查詢，再讀取該頁完整班次資料。官網每頁顯示 5 班，程式會篩選完整結果，不只擷取第一頁。抵達時間使用 DestinationTime，避免誤用停靠站清單中台南站的再出發時間。

日期須在官網開放查詢範圍內。輸出車次、出發／抵達時間、行車時間、自由座車廂及備註，儲存在 `outputs/transport/thsr/` 的 CSV、JSON。CSV 可用 Excel 開啟，JSON 保留車次前導零。可用 `--output-dir` 指定其他目錄，相同查詢再次執行會更新同名結果。

查詢失敗會報錯並盡可能儲存 `.error.html`，不把網站失效誤判成沒有班次。有時刻表不代表仍有座位，程式不會進行訂票。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
