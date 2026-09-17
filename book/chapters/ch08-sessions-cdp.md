# 第 8 章　沿用登入狀態：Chrome、工作階段與 CDP 連線

公開頁面可以用全新的瀏覽器工作階段；Blogger 和 Google Play 圖書後台則需要登入。把帳號密碼寫進程式是不安全的，也會讓範例無法交給其他讀者。本章只沿用讀者手動登入的 Chrome，不自動輸入密碼。

## 本章目標

完成後，你能說明 browser、context、page 的關係，並在不輸入密碼的前提下連接自己的 Chrome。

## 執行前準備

需要已登入的 Chrome、遠端偵錯設定與讀者帳號環境變數；沒有登入帳號時只做設定檢查，不執行後台操作。

## 8.1　理解三層物件

Playwright 啟動的 `browser` 可以包含多個 `context`，每個 context 有自己的 Cookie、local storage 和分頁。`page` 是其中一個分頁。新建 context 不會繼承日常 Chrome 登入狀態，這正是「程式又顯示登入頁」的常見原因。

若要使用既有 Chrome，程式可透過 Chrome DevTools Protocol（CDP）連線到已開啟的瀏覽器，再從既有 context 建立分頁。連線時只控制新分頁，程式結束後關閉 CDP 連線，原本的 Chrome 和其他分頁仍保持開啟。

## 8.2　讀者自己的帳號設定

公開讀者版不含作者的 Blogger ID、公開網址或 Play Books 出版帳戶。先閱讀 [讀者帳號設定](../../docs/guides/reader-accounts.md)，在自己的終端機設定環境變數。程式只在記憶體中讀取設定，不把它寫入輸出報告。

```powershell
$env:BLOGGER_EMAIL = '你的帳號'
$env:BLOGGER_BLOG_ID = '你的數字網誌ID'
$env:BLOGGER_PUBLIC_URL = 'https://你的網誌.blogspot.com/'
```

帳號設定和 CDP 網址是兩件事：前者告訴程式要確認哪個帳號和網誌，後者告訴程式如何連到 Chrome。未設定時，讀者版會在真正操作後台前停止。

## 8.3　驗證而不是猜測登入

連線後先到後台，檢查頁面上可見的帳號識別，再導向公開頁面。這個檢查不能保證所有權限都正確，但能避免把資料寫到錯誤帳號。若找不到預期帳號，程式應停止並要求讀者手動切換，而不是繼續發布。

同一原則適用 Play Books：先確認出版中心網址和書籍草稿，再執行填寫。`fill_play_book.py --validate-only` 只檢查 JSON，不連接瀏覽器；先用專案提供的固定資料驗證格式，可以避免開啟後台才發現欄位缺漏：

```bash
.venv/bin/python examples/06_publishing/fill_play_book.py \
  --metadata tests/python/fixtures/book-metadata.json --validate-only
```

## 8.4　Windows、WSL 與 CDP

Windows Chrome 和 WSL 的 localhost 網路環境可能不同。範例在偵測到 WSL 時，會將腳本的 Windows 路徑轉換後交給 Windows Python 執行；因此 Windows Python 也要安裝 Playwright。不要把 WSL 的 `.venv` 路徑直接當成 Windows 執行檔。

如果使用明確的 `BLOGGER_CDP_URL` 或 `CHROME_CDP_URL`，請確認它只在目前終端機有效，且不要提交到 Git。Chrome 顯示連線授權提示時，手動確認即可；不需要把 Cookie 或 profile 複製到書籍資料夾。

## 8.5　何時不該使用 CDP

不需要登入的查詢，優先使用全新 context。它比較容易重現，也不會讀取個人資料。只有需要既有登入工作階段的後台操作才使用 CDP；發布案例安排在第 17 章，並要求先檢查操作界線。

## 8.6　練習

1. 執行 E03 前只設定帳號資訊，不設定 CDP，記錄程式的明確錯誤。
2. 手動登入自己的 Blogger 後執行 E03，確認程式只開啟分頁，不關閉原有 Chrome。
3. 用 `fill_play_book.py --metadata tests/python/fixtures/book-metadata.json --validate-only` 檢查一份 metadata JSON，確認沒有連接後台。

下一章回到公開頁面，實際取得 Happy eBook 的 AI Agent 書單；它不需要登入，因此會使用乾淨的 Chromium。

<!-- 編輯紀錄：初稿；搭配 E03、E04、E14–E16 與 reader-accounts 指南。 -->
