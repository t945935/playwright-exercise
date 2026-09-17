# 今日 AI 新聞（Python + Playwright）

使用 Python 3.10 以上版本與 Playwright 的 APIRequestContext 讀取 Google News RSS，搜尋繁中及英文 AI 新聞。無須 API 金鑰、登入或安裝 Chromium。

```bash
python -m pip install playwright
python examples/03_data_queries/ai_news_today.py
```

本專案已有虛擬環境時可執行：

```bash
.venv/bin/python examples/03_data_queries/ai_news_today.py
```

預設抓取執行當天（台灣 UTC+8）的新聞，依 RSS 發布時間篩選，排除未來時間，再去重並由新到舊輸出最多 30 則。標題維持原始語言。Google News 搜尋結果有收錄與數量限制，不保證完整涵蓋所有消息。使用者點開結果的 Google News 連結後可前往媒體原文。

結果存於 `outputs/news/ai_news_YYYY-MM-DD.json` 與同名 `.md`，包含標題、來源、時間與連結。同一天再次執行會更新同名檔案。

```bash
# 輸出全部符合日期的搜尋結果
python examples/03_data_queries/ai_news_today.py --limit 0

# 指定日期、數量與輸出目錄
python examples/03_data_queries/ai_news_today.py --date 2026-09-17 --limit 50 --output-dir reports
```

遇到連線錯誤會最多嘗試三次；部分搜尋失敗時仍保存其餘結果並標示錯誤。結束碼 0 表示完成（也可能是零則新聞），1 表示全部搜尋失敗，2 表示參數錯誤或結果有警告。全部搜尋失敗時不覆寫先前結果。

若要每天自動執行，可在 Linux 的 `crontab -e` 加入以下設定（cron 主機時區須為 Asia/Taipei；此處每日 09:00 更新）：

```cron
0 9 * * * cd /你的路徑/playwright-exercise && .venv/bin/python examples/03_data_queries/ai_news_today.py >> /tmp/ai_news_today.log 2>&1
```

此專案不會自行安裝排程。Windows 可在工作排程器設定每日執行 Python，參數為腳本絕對路徑，並設定「開始位置」為專案目錄。

參考：[Playwright APIRequestContext](https://playwright.dev/python/docs/api/class-apirequestcontext)。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
