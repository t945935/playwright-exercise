# 發布與電子書後台

此類包含會修改外部網站的原有範例，保留目前行為；書籍教學版的參數化及預覽流程尚待編寫。

| 正式檔案 | 舊入口 | 執行效果 |
|---|---|---|
| publish_blogger_post.py | t3.py | 在 Blogger 建立並發布測試文章 |
| create_play_book.py | a6.py | 在 Google Play 圖書後台建立書籍，儲存並繼續 |
| fill_play_book.py | a8.py | 讀取 metadata JSON，建立或選取草稿後填入書籍資料 |

依賴已登入 Chrome 及讀者自己的環境設定，詳見 [帳號設定](../../docs/guides/reader-accounts.md)。`fill_play_book.py --validate-only` 可驗證輸入資料，但一般執行模式仍會操作後台。目錄整理驗證只解析語法，沒有執行這三個程式。
