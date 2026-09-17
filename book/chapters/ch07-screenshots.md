# 第 7 章　多尺寸截圖：手機、平板、電腦畫面與除錯記錄

截圖是成果，也是除錯證據。當頁面在你的電腦上看起來正常，讀者卻遇到不同版面時，一張包含視窗大小、網址和時間的截圖，比一句「畫面不一樣」更有用。

## 本章目標

完成後，你能以三種 viewport 產生可追溯的 PNG、HTML 與 JSON 報告。

## 執行前準備

需要已安裝 Chromium；截圖預設使用無畫面模式，除錯時再加上 `--headed`。

## 7.1　設定 viewport

E13 將三種常見尺寸整理成設定：手機 390×844、平板 820×1180、電腦 1440×900。瀏覽器的 viewport 是 CSS 像素，不等同於實體螢幕像素；它用來觸發網站的響應式版面。

```python
page = browser.new_page(viewport={"width": 390, "height": 844}, is_mobile=True)
page.goto(url, wait_until="domcontentloaded")
page.screenshot(path="phone.png", full_page=True)
```

手機和桌面應使用獨立 page，避免前一種 viewport、Cookie 或捲動位置影響下一種結果。`full_page=True` 會擷取完整頁面；`--viewport-only` 則只保存首屏，適合比較首屏排版。

## 7.2　處理延遲載入

長頁面的圖片常在捲動到附近才載入。E13 會分段向下捲動，等待可見圖片，最後回到頂部再拍攝。這個流程要有上限：無限捲動網站不能讓程式永遠等待。

```python
def scroll_to_bottom(page, viewport_height: int, max_steps: int = 40):
    for _ in range(max_steps):
        page.mouse.wheel(0, viewport_height)
        page.wait_for_timeout(150)
        if page.evaluate("document.scrollingElement.scrollTop + innerHeight >= document.scrollingElement.scrollHeight"):
            break
    page.evaluate("window.scrollTo(0, 0)")

# page 是 7.1 節建立的分頁
viewport_height = page.viewport_size["height"]
scroll_to_bottom(page, viewport_height)
```

固定等待在這裡只用於讓滾動事件觸發，並以迴圈上限保護程式；真正的圖片完整性要在報告中記錄未載入數量。輸出報告不應宣稱所有圖片成功，除非程式真的檢查過。

## 7.3　讓截圖可追溯

每次執行使用新的時間資料夾，內含三張 PNG、`index.html` 和 `report.json`。報告應記錄：網址、尺寸、實際頁高、水平溢出、未載入圖片數和擷取時間。檔名不要只叫 `latest.png`，否則下一次執行會覆蓋除錯證據。

```bash
.venv/bin/python examples/05_visuals/website_screenshots.py https://happyebook.com/books.html
```

開啟輸出資料夾的 `index.html`，可並排查看三種尺寸。出版用圖片需另行挑選到 `book/assets/images/`，並記錄來源與日期；`outputs/` 是執行資料，不會直接變成書籍素材。

成功時終端機會顯示三個尺寸都完成：

```text
完成 3/3 個尺寸。比較頁面：.../index.html
```

檔名通常是 `phone_390x844.png`、`tablet_820x1180.png` 和 `desktop_1440x900.png`；實際資料夾名稱會包含擷取時間。

## 7.4　截圖與測試的差異

截圖可以協助觀察，卻不等於視覺回歸測試。不同作業系統的字型、裝置像素比和外部廣告可能讓像素不同。若要做穩定測試，應鎖定瀏覽器版本、比較可接受差異，並先處理動態內容。

## 7.5　練習

1. 只擷取 `https://happyebook.com/books.html` 首屏，再比較完整頁面報告。
2. 將手機寬度改為 320，觀察哪個區塊首先換行或溢出。
3. 將一張輸出 PNG 搬到 `book/assets/images/`，補上章稿中的來源、日期和用途記錄。

下一章會處理另一種「畫面看得到但程式看不到」的情境：登入狀態存在你的 Chrome，卻不在新啟動的瀏覽器工作階段。

<!-- 編輯紀錄：初稿；搭配 E13 與 SCREENSHOTS 指南。 -->
