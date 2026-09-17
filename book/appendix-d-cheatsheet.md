# 附錄 D　命令列參數與 Playwright 常用操作速查

## D.1　常用命令

```bash
.venv/bin/python examples/01_basics/open_page.py
.venv/bin/python examples/03_data_queries/ai_news_today.py --help
.venv/bin/python examples/04_tracking/tsmc_price_tracker.py --watch --interval 60 --count 5
.venv/bin/python examples/05_visuals/website_screenshots.py --headed --viewport-only
```

Windows 將執行檔換成 `.\\.venv\\Scripts\\python.exe`。

## D.2　瀏覽器操作

```python
browser = p.chromium.launch(headless=True)
context = browser.new_context(locale="zh-TW")
page = context.new_page()
page.goto(url, wait_until="domcontentloaded")
page.get_by_role("button", name="查詢", exact=True).click()
page.get_by_label("出發站").select_option(label="彰化")
expect(page.locator(".result")).to_be_visible()
page.screenshot(path="result.png", full_page=True)
browser.close()
```

## D.3　資料與等待

`locator()` 建立定位器，`inner_text()` 讀可見文字，`text_content()` 讀 DOM 文字，`input_value()` 讀輸入值，`evaluate()` 取得屬性或頁面資訊。優先等待 URL、元素附加、元素可見或文字出現；只有在觸發滾動事件等必要情況才使用短暫固定等待。

`APIRequestContext` 適合 RSS 和行情等直接 HTTP 資料；它仍需要檢查 HTTP 狀態、欄位、日期和來源時間。
