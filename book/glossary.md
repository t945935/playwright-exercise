# 術語表

- **Browser**：由 `chromium.launch()` 啟動的瀏覽器程序。
- **BrowserContext**：隔離 Cookie、快取與登入狀態的工作階段；一個 Browser 可以建立多個 Context。
- **Page**：Context 中的一個分頁，負責導覽、定位元素與截圖。
- **Locator**：描述頁面元素的查詢物件，例如 `get_by_role()` 或 `locator()`；真正操作時會自動等待。
- **APIRequestContext**：Playwright 提供的 HTTP 用戶端，適合 RSS 或 JSON API，不必啟動可見瀏覽器。
- **CDP**：Chrome DevTools Protocol；本書用 `connect_over_cdp()` 連接使用者已登入的 Chrome。
- **Headless**：無畫面模式。Playwright Python 的 `launch()` 預設為 headless；除錯時可指定 `headless=False`。
