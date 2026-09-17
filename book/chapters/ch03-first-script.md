# 第 3 章　第一支自動化程式：開啟網站、讀取標題與執行除錯

上一章確認了環境。本章開始讀程式。第一個範例故意很短，因為短程式最適合觀察每一個動作，也最容易判斷是哪一步出了問題。

## 3.1　從四個動作開始

開啟 [E01](../../examples/01_basics/open_page.py)：

```python
import argparse
from playwright.sync_api import sync_playwright

parser = argparse.ArgumentParser()
parser.add_argument("--headed", action="store_true")
args = parser.parse_args()
with sync_playwright() as p:
    browser = p.chromium.launch(headless=not args.headed)
    page = browser.new_page()
    page.goto("https://playwright.dev")
    print(page.title())
    browser.close()
```

`sync_playwright()` 建立 Python 與 Playwright 的連線；`p.chromium.launch()` 啟動 Chromium；`new_page()` 建立分頁；`goto()` 導向網址；`title()` 讀取標題。最後的 `browser.close()` 關閉瀏覽器。`with` 區塊結束時，Playwright 連線也會被清理。

這段程式沒有使用固定秒數等待。`goto()` 預設會等待頁面完成基本導覽，Playwright 的動作也會在適當時機等待元素可操作。等待條件比「睡兩秒」更能適應網路快慢；第 6 章會再深入討論。

## 3.2　從專案根目錄執行

每次先確認目前目錄：

```bash
pwd
ls examples/01_basics
.venv/bin/python examples/01_basics/open_page.py
.venv/bin/python examples/01_basics/open_page.py --headed
```

Windows PowerShell 使用：

```powershell
Get-Location
Get-ChildItem examples/01_basics
.\.venv\Scripts\python.exe examples/01_basics/open_page.py
```

輸出應包含 `Fast and reliable end-to-end testing for modern web apps | Playwright`。標題可能因網站改版而改變，因此範例只示範讀取，不把整句文字寫成必要條件。

## 3.3　加入可讀的檢查

如果需求是「頁面必須包含 Playwright」，可以用 `expect` 表達完成條件：

```python
import re
from playwright.sync_api import sync_playwright, expect

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://playwright.dev")
    expect(page).to_have_title(re.compile("Playwright"))
    browser.close()
```

斷言失敗時，錯誤訊息會告訴你實際頁面和等待時間。這比只印出 `None` 或空清單更容易追查。正式應用也應在輸出前檢查資料完整性，例如書卡數量是否等於網站顯示的總數。

## 3.4　有畫面與無畫面模式

`launch()` 預設使用無畫面模式。伺服器或排程可以維持這個設定；除錯時可執行 E01 的 `--headed`：

```python
browser = p.chromium.launch(headless=False)
```

除錯時先用有畫面模式觀察導覽、彈窗和滾動位置；流程穩定後才切換 headless。無畫面不代表不會載入內容，它只是沒有可見視窗。若程式在 headless 成功、有畫面失敗，通常要檢查視窗大小、彈窗或環境依賴，而不是立即加長等待時間。

## 3.5　逐步定位失敗

網站開啟失敗時，用最小步驟切開問題：

```python
page.goto("https://playwright.dev", wait_until="domcontentloaded")
print("URL:", page.url)
print("TITLE:", page.title())
print("H1:", page.locator("h1").first.inner_text())
```

如果 URL 不對，是導覽或重新導向問題；URL 正確但標題不對，可能是頁面仍在載入或網站改版；標題正確而 `h1` 找不到，才是定位器問題。每次只改一件事，錯誤才不會被新的變更遮住。

## 3.6　練習

1. 將網址改成 `https://happyebook.com/`，印出頁面標題與目前 URL。
2. 將 `page.screenshot(path="outputs/first-page.png")` 加在 `title()` 後面，確認 `outputs/` 會自動建立後再執行。
3. 故意把網址改成不存在的網域，記下例外類型和錯誤訊息；再恢復正確網址。

完成條件是你能說明每一行的責任，並能從 URL、標題、元素三個層次定位失敗。下一章會補上這些程式背後所需的 Python 資料結構與檔案處理。

<!-- 編輯紀錄：初稿；搭配 E01。驗證日期 2026-09-17，Python 3.12.3、Playwright 1.63.0。 -->
