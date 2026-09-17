# 第 17 章　內容發布自動化：Blogger 發文與電子書後台填寫

讀取資料和發布內容的風險不同。前者通常只產生本機結果；後者會改變外部帳號的狀態。本章教的是如何設計確認界線和可追溯流程，不鼓勵把發布按鈕藏在排程裡。

## 17.1　先分成預覽和執行

E14 `publish_blogger_post.py`、E15 `create_play_book.py` 和 E16 `fill_play_book.py` 沿用已登入 Chrome。公開讀者版已移除作者預設值，改用環境變數；仍應先閱讀 [帳號設定](../../docs/guides/reader-accounts.md)。

書籍教學的安全順序是：準備資料 → `--dry-run` 顯示摘要 → 人工確認帳號和內容 → 建立草稿或發布 → 重新讀回驗證。任何一步失敗都要保留編輯網址和錯誤文字，方便人工檢查。

## 17.2　Blogger 發文

發文程式會開啟後台、確認登入帳號、建立新文章、填寫標題和正文，再按發布並讀回公開網址。第一次執行先使用 `publish_blogger_post.py --dry-run`；它只列印目標與內容，不連線、不建立文章。確認無誤後才使用測試網誌執行正式模式。

原始案例的 `POST_TITLE` 和 `POST_CONTENT` 是測試文字。正式使用應改成命令列或檔案輸入，並在畫面上確認目標網誌。不要把 Blogger ID、郵件或 Chrome profile 提交到公開儲存庫。

## 17.3　Google Play 圖書

E15 先建立書籍資料，E16 從 JSON 讀取書名、副標題和說明，選取或建立草稿後填入欄位。`--validate-only` 可以在不連接瀏覽器的情況檢查必要欄位和文字型別；這應是發布前的固定步驟。

填寫欄位後不代表已儲存、上傳封面、設定價格或發布。先以 `create_play_book.py --dry-run` 預覽建立步驟，以 `fill_play_book.py --dry-run` 預覽 metadata 與目標；每個後台按鈕的副作用都要在章稿和終端輸出說明。

專案附有可離線預覽的 metadata：

```bash
.venv/bin/python examples/06_publishing/fill_play_book.py \
  --metadata tests/python/fixtures/book-metadata.json --dry-run
```

## 17.4　帳號和測試資料

用專門的測試網誌或草稿帳號，避免在正式內容上試跑。若服務沒有測試環境，至少使用明確的測試標題、手動確認和可刪除的草稿。登入狀態留在本機 Chrome，不複製到書籍素材。

## 17.5　練習

1. 用 `--validate-only` 檢查一份 metadata JSON，再故意移除 `BOOK_TITLE` 觀察錯誤。
2. 將 Blogger 程式改成只建立草稿，加入「輸入 YES 才發布」的確認。
3. 列出每個後台按鈕的副作用，標記可逆和不可逆動作。

下一章將把查詢、追蹤和報告程式組成每日工具箱；發布動作仍保留人工確認，不放進無人值守排程。

<!-- 編輯紀錄：初稿；搭配 E14–E16。發布流程未在本次寫作驗證，需使用測試帳號重新核對。 -->
