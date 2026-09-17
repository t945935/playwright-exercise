# Python 範例索引

正式來源共 16 個，根目錄相容入口與技能副本不重複計數。章節為規劃對應，並非章稿完成狀態。

| 編號 | 應用 | 正式程式 | 舊入口 | 章 | 技術 | 執行條件／效果 | 指南 |
|---|---|---|---|---|---|---|---|
| E01 | 開啟 Playwright 網站 | [open_page.py](../examples/01_basics/open_page.py) | `example.py` | 03 | 瀏覽器 | 不需登入 | 待補 |
| E02 | 開啟部落格 | [open_blog.py](../examples/01_basics/open_blog.py) | `t1.py` | 03 | 瀏覽器 | 原有個人公開網址；等待手動關閉 | 待補 |
| E03 | 開啟 Blogger 後台 | [open_blogger_admin.py](../examples/02_browser_sessions/open_blogger_admin.py) | `t2.py` | 08 | CDP | 已登入 Chrome；Windows／WSL 設定 | 待補 |
| E04 | 開啟 Google Play 圖書後台 | [open_play_books.py](../examples/02_browser_sessions/open_play_books.py) | `a5.py` | 08 | CDP | 已登入 Chrome；Windows／WSL 設定 | 待補 |
| E05 | AI Agent 分類完整書單 | [happyebook_ai_agent.py](../examples/03_data_queries/happyebook_ai_agent.py) | `happyebook_ai_agent.py` | 05、09 | 瀏覽器 | 讀取公開書單 | 待補 |
| E06 | 今日 AI 新聞 | [ai_news_today.py](../examples/03_data_queries/ai_news_today.py) | `ai_news_today.py` | 11 | APIRequestContext | RSS 查詢，不啟動瀏覽器 | [操作指南](guides/ai-news.md) |
| E07 | 臺鐵彰化→嘉義 08:00–10:00 | [tra_changhua_chiayi.py](../examples/03_data_queries/tra_changhua_chiayi.py) | `tra_banqiao_tainan.py` | 06、12 | 瀏覽器 | 查時刻表，不訂票 | [操作指南](guides/tra.md) |
| E08 | 高鐵板橋→台南 09:00–11:00 | [thsr_banqiao_tainan.py](../examples/03_data_queries/thsr_banqiao_tainan.py) | `thsr_banqiao_tainan.py` | 06、13 | 瀏覽器 | 查時刻表，不訂票 | [操作指南](guides/thsr.md) |
| E09 | 開盤漲幅排行榜 | [stock_open_gainers.py](../examples/03_data_queries/stock_open_gainers.py) | `stock_open_gainers.py` | 14 | APIRequestContext | 需有效開盤行情；預設上市 | [操作指南](guides/stock-opening.md) |
| E10 | 台積電股價追蹤 | [tsmc_price_tracker.py](../examples/04_tracking/tsmc_price_tracker.py) | `tsmc_price_tracker.py` | 15 | APIRequestContext | 保存 SQLite；比較前次有效紀錄 | [操作指南](guides/tsmc-tracker.md) |
| E11 | 活動報名提醒 | [event_registration_watch.py](../examples/04_tracking/event_registration_watch.py) | `event_registration_watch.py` | 16 | 瀏覽器 | 偵測入口並本機通知，不自動報名 | [操作指南](guides/event-watch.md) |
| E12 | Happy eBook 新書雷達 | [happyebook_new_books.py](../examples/04_tracking/happyebook_new_books.py) | `happyebook_new_books.py` | 10 | 瀏覽器 | 保存完整基準與歷史 | [操作指南](guides/book-radar.md) |
| E13 | 多尺寸截圖 | [website_screenshots.py](../examples/05_visuals/website_screenshots.py) | `website_screenshots.py` | 07 | 瀏覽器 | 手機、平板、電腦；輸出 PNG／HTML | [操作指南](guides/screenshots.md) |
| E14 | Blogger 發文 | [publish_blogger_post.py](../examples/06_publishing/publish_blogger_post.py) | `t3.py` | 17 | CDP | 會直接發布文章；需已登入 Chrome | 待補 |
| E15 | 建立 Google Play 書籍 | [create_play_book.py](../examples/06_publishing/create_play_book.py) | `a6.py` | 17 | CDP | 會建立及儲存書籍；需已登入 Chrome | 待補 |
| E16 | JSON 填寫書籍資料 | [fill_play_book.py](../examples/06_publishing/fill_play_book.py) | `a8.py` | 17 | CDP | 一般模式會建立／修改草稿；需 metadata | 待補 |

CDP 範例沿用既有已登入 Chrome；一般瀏覽器範例使用 Playwright Chromium。APIRequestContext 範例透過 Playwright 發送 HTTP 請求，不需要啟動 Chromium。既有 8 份指南已整理，其餘指南列為寫作待辦。

完整的登入、外站與副作用狀態見[範例驗證矩陣](example-status.md)。

## 學習順序

建議 E01 → E13 → E05 → E12，接著選擇新聞、交通、行情或活動主題；登入與發布案例最後學習。新書基準、活動狀態與股價資料庫位於 `outputs/`，搬移對照見 [目錄整理說明](directory-map.md)。
