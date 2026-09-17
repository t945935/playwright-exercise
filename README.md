# Python × Playwright 自動化實戰｜讀者服務

**從安裝入門到新聞、交通、股價與新書追蹤的 16 個應用**

本書的 Python 範例、操作指南與問題回報入口。**目前收錄 16 個應用，分成 6 類；前言、第 1–18 章與五個附錄均已完成初稿。**

[範例索引](docs/example-index.md) · [閱讀目錄](book/toc.md) · [術語表](book/glossary.md) · [更新紀錄](CHANGELOG.md) · [問題回報](https://github.com/t945935/playwright-exercise/issues/new/choose)

## 下載範例

不熟悉 Git：點上方 **Code → Download ZIP**，解壓縮後用終端機進入資料夾。

熟悉 Git：

```bash
git clone https://github.com/t945935/playwright-exercise.git
cd playwright-exercise
```

下載公開範例不需要登入 GitHub。提出問題需要 GitHub 帳號。

## 安裝與第一次執行

Python 3.10+；整理時驗證環境為 Python 3.12.3、Playwright 1.63.0。完整跨平台驗證尚在進行。

Windows PowerShell：

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe examples/01_basics/open_page.py
```

macOS／Linux／WSL：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m playwright install chromium
.venv/bin/python examples/01_basics/open_page.py
.venv/bin/python -m unittest discover -s tests/python -p 'test_*.py'
```

不需要啟用虛擬環境；以上命令直接使用環境內的 Python。第一次成功會在終端機印出 Playwright 網站標題。

若 Linux 提示缺少瀏覽器系統套件，可執行 `.venv/bin/python -m playwright install --with-deps chromium`；此步驟可能要求系統管理員權限。

## 選一個應用開始

以下命令以 macOS／Linux／WSL 為例；Windows 將 `.venv/bin/python` 換成 `.\.venv\Scripts\python.exe`。

```bash
# 一次拍下手機、平板、電腦畫面
.venv/bin/python examples/05_visuals/website_screenshots.py https://happyebook.com

# 取得 AI Agent 分類的完整書單
.venv/bin/python examples/03_data_queries/happyebook_ai_agent.py --headless

# 新書雷達：首次建立基準，之後與上次比較
.venv/bin/python examples/04_tracking/happyebook_new_books.py
```

報表與截圖會在 `outputs/` 自動建立。下載包沒有作者的歷史基準，第一次執行會建立你自己的紀錄。

| 分類 | 數量 | 主題 |
|---|---:|---|
| [01_basics](examples/01_basics/) | 2 | 網頁開啟、讀取標題 |
| [02_browser_sessions](examples/02_browser_sessions/) | 2 | Blogger、Play Books 登入工作階段 |
| [03_data_queries](examples/03_data_queries/) | 5 | 書單、AI 新聞、臺鐵、高鐵、開盤漲幅 |
| [04_tracking](examples/04_tracking/) | 3 | 台積電股價、活動報名、新書雷達 |
| [05_visuals](examples/05_visuals/) | 1 | 多尺寸網頁截圖 |
| [06_publishing](examples/06_publishing/) | 3 | 發布文章、建立與填寫電子書資料 |

根目錄 `.py` 為舊檔名相容入口，不重複計數。完整命令、參數及執行效果見 [範例索引](docs/example-index.md)。登入與出版案例需先閱讀 [讀者帳號設定](docs/guides/reader-accounts.md)，並先執行 `--dry-run` 或 `--validate-only`。

## 回報問題與勘誤

到 [Issues](https://github.com/t945935/playwright-exercise/issues/new/choose) 選擇「範例執行問題」或「書籍勘誤」。請附範例檔名、執行指令、作業系統、Python／Playwright 版本及錯誤文字；移除帳號、Cookie 與其他登入資訊。

真實網站可能改版，行情與交通資料也會隨查詢時間改變。請保留實際查詢日期，方便重現問題。此專案尚未提供固定書籍版本的 Release；更新進度見 [CHANGELOG](CHANGELOG.md)。
