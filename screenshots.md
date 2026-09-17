# 多尺寸網頁截圖（Python + Playwright）

預設拍攝 Happy eBook 的完整頁面，產生三張 PNG 與可直接開啟的 HTML 比較頁：

| 模式 | 視窗大小（CSS px） |
|---|---|
| 手機 | 390 × 844 |
| 平板 | 820 × 1180 |
| 電腦 | 1440 × 900 |

需要 Python 3.10+：

```bash
python -m pip install playwright
python -m playwright install chromium
python examples/05_visuals/website_screenshots.py
```

本專案執行：

```bash
.venv/bin/python examples/05_visuals/website_screenshots.py
# 指定網站
.venv/bin/python examples/05_visuals/website_screenshots.py https://happyebook.com/books.html
# 顯示操作視窗、只拍首屏
.venv/bin/python examples/05_visuals/website_screenshots.py --headed --viewport-only
# 動態網站可等待特定元素出現
.venv/bin/python examples/05_visuals/website_screenshots.py https://happyebook.com/books.html --wait-for .book-card
```

輸出在 `outputs/screenshots/日期時間/`，每次使用新資料夾，保留舊截圖。開啟 `index.html` 可並排比較，點圖片查看原始 PNG；`report.json` 保存網址、視窗尺寸、網頁高度、水平溢出及未載入圖片數。`--output-dir` 可自訂輸出目錄。

完整頁面模式會向下捲動以觸發圖片延遲載入，最多 40 個畫面，每段等待可見圖片最多 1.5 秒，再回到頂部拍攝；不會自動按「載入更多」。字型及圖片等待均有上限，因此無限捲動、外部圖片失效或載入特別慢的網站可能有未載入內容。截圖保留網站實際顯示的 Cookie 提示和彈窗。

使用 Chromium，手機／平板啟用觸控與行動裝置 viewport 模擬，未模擬特定手機 User-Agent，不代表實體手機或 Safari 的結果。各尺寸使用獨立、未登入的環境，像素倍率為 1。PNG 實際高度會隨完整頁面內容增加。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
