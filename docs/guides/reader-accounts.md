# 登入與出版案例的讀者設定

E03、E04、E14、E15、E16 沿用已登入的 Chrome。先在 Chrome 手動登入自己的帳號；程式不會輸入密碼。公開讀者版已移除作者帳號預設值，缺少設定時會在連接瀏覽器前停止。

## Blogger

Windows PowerShell：

```powershell
$env:BLOGGER_EMAIL = '你的Google帳號電子郵件'
$env:BLOGGER_BLOG_ID = '你的數字網誌ID'
$env:BLOGGER_PUBLIC_URL = 'https://你的網誌.blogspot.com/'
.\.venv\Scripts\python.exe examples/02_browser_sessions/open_blogger_admin.py
```

網誌 ID 是 Blogger 後台 `/blog/posts/` 後面的數字；公開網址不是後台網址。`publish_blogger_post.py` 預設會建立並發布測試文章；請先以 `--dry-run` 確認，不會連線或建立文章：

```bash
.venv/bin/python examples/06_publishing/publish_blogger_post.py --dry-run
```

## Google Play 圖書

```powershell
$env:PLAY_BOOKS_PUBLISHER_URL = 'https://play.google.com/books/publish/a/你的數字出版帳戶ID#home'
.\.venv\Scripts\python.exe examples/02_browser_sessions/open_play_books.py
```

`create_play_book.py` 預設會新增書籍並儲存；先用 `--dry-run` 確認目標。`fill_play_book.py` 一般模式會新增或選取草稿並填寫資料；先用 `--validate-only` 或 `--dry-run` 檢查 metadata JSON，不連接後台：

```powershell
.\.venv\Scripts\python.exe examples/06_publishing/fill_play_book.py --metadata book-metadata.json --validate-only
```

預覽建立書籍：

```bash
.venv/bin/python examples/06_publishing/create_play_book.py --dry-run
```

## Chrome 與 WSL

範例優先使用 `BLOGGER_CDP_URL` 或 `CHROME_CDP_URL`；未指定時讀取 Windows Chrome 的 `DevToolsActivePort`。WSL 執行時會轉由 Windows 的 `python.exe` 執行，因此 Windows Python 也必須安裝 Playwright。不要把 Cookie、profile 或環境變數提交到 GitHub。

這些範例會讀取或修改登入後台，請使用自己的測試網誌或草稿帳號，並在每個不可逆動作前人工確認。
