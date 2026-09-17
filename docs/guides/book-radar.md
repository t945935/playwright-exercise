# Happy eBook 新書雷達

以 Python 3.10+ 與 Playwright 擷取[完整書單](https://happyebook.com/books.html)，逐次比對新增書籍。

```bash
python -m pip install playwright
python -m playwright install chromium
python examples/04_tracking/happyebook_new_books.py
```

本專案直接執行：

```bash
.venv/bin/python examples/04_tracking/happyebook_new_books.py
# 顯示瀏覽器操作
.venv/bin/python examples/04_tracking/happyebook_new_books.py --headed
```

第一次執行只建立基準；隔一段時間再執行，才會顯示相較上次新增的書目。以書籍「更多資訊」頁面網址辨識，因此同名但不同連結會保留，改書名但連結未變不會算新書。新增代表本次首次相較上次出現，無法推斷實際出版日期；重新上架或換網址亦可能列入。

程式自動展開所有書籍，確認卡片數與網站總數一致、連結有效且不重複，才保存資料。連線失敗、卡片未載完、空書單或基準損毀會報錯，不覆寫原本基準。

預設存於專案根目錄的 `outputs/books/radar/`：

- `baseline.json`：上次成功查詢的完整書單。請保留，刪除後會重新建立基準。
- `latest.html`：可直接用瀏覽器開啟的報告；首次顯示全書單，之後顯示新增書籍。
- `latest.json`：本次新增、未再出現書目及查詢時間。
- `history/`：每次成功查詢的報告與完整快照，避免重跑後找不到之前的新書清單。

可用 `--output-dir` 設定其他資料目錄；每個目錄有獨立基準。同一目錄請只執行一個程序。程式每次查詢一次即結束，尚未安裝每日排程。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
