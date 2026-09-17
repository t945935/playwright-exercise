# 登入與出版案例的讀者設定

E03、E04、E14、E15、E16 沿用已登入的 Chrome。先在 Chrome 手動登入自己的帳號；程式不會輸入密碼。公開範例已移除作者帳號預設值，缺少設定時會在連接瀏覽器前停止。

以下以 Windows PowerShell 為例。請將範例字串換成自己的資料；環境變數僅對目前終端機及其子程序有效，不需要另裝 dotenv。

## Blogger

```powershell
$env:BLOGGER_EMAIL = '你的Google帳號電子郵件'
$env:BLOGGER_BLOG_ID = '你的數字網誌ID'
$env:BLOGGER_PUBLIC_URL = 'https://你的網誌.blogspot.com/'
.\.venv\Scripts\python.exe examples/02_browser_sessions/open_blogger_admin.py
```

網誌 ID 是 Blogger 後台 `/blog/posts/` 後面的數字；公開網址不是後台網址。使用 `publish_blogger_post.py` 會建立並發布測試文章，請先檢查程式中的 `POST_TITLE`、`POST_CONTENT` 與所選網誌。

## Google Play 圖書

```powershell
$env:PLAY_BOOKS_PUBLISHER_URL = 'https://play.google.com/books/publish/a/你的數字出版帳戶ID#home'
.\.venv\Scripts\python.exe examples/02_browser_sessions/open_play_books.py
```

請從自己已登入的出版中心確認帳戶 ID；設定值需符合上述網址格式。`create_play_book.py` 會新增書籍並儲存；`fill_play_book.py` 一般模式會新增或選取草稿並填寫資料。

只驗證 JSON，不連接 Chrome：

```powershell
.\.venv\Scripts\python.exe examples/06_publishing/fill_play_book.py --metadata book-metadata.json --validate-only
```

`book-metadata.json` 格式：

```json
{
  "BOOK_TITLE": "我的示範書籍",
  "BOOK_SUBTITLE": "讀者練習資料",
  "BOOK_DESCRIPTION": "這是一段示範書籍說明。"
}
```

## Chrome 連線與 WSL

原範例優先使用 `BLOGGER_CDP_URL` 或 `CHROME_CDP_URL`；未指定時讀取 Windows Chrome 的 `DevToolsActivePort`。請依自己的 Chrome 版本啟用遠端偵錯；若 Chrome 顯示連線授權提示，手動確認。

WSL 執行時會轉由 Windows 的 `python.exe` 執行，因此 Windows Python 也必須安裝 Playwright。WSL 的 `.venv` 不會自動提供 Windows 套件。讀者版會將上述帳號變數及 CDP 設定傳給 Windows 子程序。

macOS／Linux 可設定對應 CDP 網址連接自行啟動的 Chrome；目前未完成這些登入環境的實際驗證。Bash 設定範例為 `export BLOGGER_BLOG_ID='你的數字網誌ID'`，其餘變數同理。
