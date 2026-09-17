# 附錄 A　GitHub 範例下載與更新方式

讀者版儲存在 [t945935/playwright-exercise](https://github.com/t945935/playwright-exercise)。公開下載不需要登入；提出問題或勘誤才需要 GitHub 帳號。

不熟悉 Git 時，在儲存庫頁面選 **Code → Download ZIP**，解壓縮後進入資料夾。熟悉 Git 時：

```bash
git clone https://github.com/t945935/playwright-exercise.git
cd playwright-exercise
git pull
```

每次更新前先備份自己的 `outputs/`。程式和資料是兩回事；更新程式不應刪除新書基準、股價資料庫或活動狀態。不要上傳 `.venv/`、`.browser-profile/`、Cookie、帳號設定或個人報表。

問題回報請附範例檔名、命令、作業系統、Python／Playwright 版本、查詢日期和錯誤文字。先移除密碼、Token、Cookie、私人網址和後台截圖。

## A.1　確認版本

```bash
git log -1 --oneline
.venv/bin/python --version
.venv/bin/python -m playwright --version
```

讀者服務首頁的 `CHANGELOG.md` 記錄書籍附檔變更。真實網站會改版，若程式版本不變而結果改變，仍應在 Issue 中記下查詢日期。
