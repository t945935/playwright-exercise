# 發布與電子書後台

此類包含會修改外部網站的範例。預設模式仍會實際操作後台；第一次學習請先使用各程式的 `--dry-run` 或 `--validate-only`。

| 正式檔案 | 舊入口 | 執行效果 |
|---|---|---|
| publish_blogger_post.py | t3.py | 在 Blogger 建立並發布測試文章；`--dry-run` 只預覽 |
| create_play_book.py | a6.py | 在 Google Play 圖書後台建立書籍；`--dry-run` 只預覽 |
| fill_play_book.py | a8.py | 讀取 metadata JSON 填寫書籍資料；`--validate-only`／`--dry-run` 不連線 |

依賴已登入 Chrome 及讀者自己的環境設定，詳見 [帳號設定](../../docs/guides/reader-accounts.md)。一般執行模式會操作後台；請先以 dry-run 確認帳號、目標與內容，再使用測試帳號執行。
