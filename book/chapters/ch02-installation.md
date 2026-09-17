# 第 2 章　建立開發環境：安裝 Python、Playwright 與瀏覽器

本章完成後，你會有一個獨立的 Python 環境，能用 Playwright 啟動 Chromium，並執行本書的第一個範例。安裝時最容易混淆的是「Python 套件」和「瀏覽器執行檔」：前者讓程式可以呼叫 Playwright，後者才是真正被控制的瀏覽器。兩者都準備好，程式才能順利執行。

本書以 Python 3.10 以上為前提，範例整理時使用 Python 3.12.3 與 Playwright 1.63.0。Playwright 官方目前的 Python 文件也把 Windows、macOS、Linux 和 WSL 列為支援環境；實際可用版本仍會受作業系統和瀏覽器更新影響，請以 [官方安裝文件](https://playwright.dev/python/docs/intro) 為準。

## 2.1　先確認作業系統與 Python

開啟終端機。Windows 使用 PowerShell；macOS 和 Linux 使用 Terminal；WSL 使用你安裝的 Linux 發行版終端機。先執行版本查詢：

Windows：

```powershell
py --version
```

macOS、Linux 或 WSL：

```bash
python3 --version
```

看到 `Python 3.10`、`Python 3.11`、`Python 3.12` 或更新版本即可繼續。若顯示找不到命令，先安裝 Python，再回來執行同一個查詢。Windows 安裝時請勾選「Add Python to PATH」；如果電腦同時有多個 Python，優先使用 `py` 啟動指定版本。

不要把系統 Python 的所有套件直接拿來寫書籍範例。不同專案可能需要不同版本，下一節的虛擬環境會把本書套件隔離起來。

## 2.2　建立虛擬環境

先進入從 GitHub 下載的專案根目錄，也就是能看到 `requirements.txt` 和 `examples/` 的那一層。Linux、macOS 和 WSL 執行：

```bash
python3 -m venv .venv
```

Windows PowerShell 執行：

```powershell
py -m venv .venv
```

`.venv` 是放置本專案 Python 執行檔與套件的資料夾。它不需要上傳到 GitHub，讀者版的 `.gitignore` 已將它排除。建立一次即可；日後刪除並重新建立，會得到一個乾淨環境。

你可以選擇啟用環境，讓後面的命令都使用它。Linux、macOS 和 WSL：

```bash
source .venv/bin/activate
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

看到命令列開頭出現 `(.venv)` 就表示已啟用。PowerShell 若因執行原則拒絕腳本，可以不啟用，直接使用 `.\.venv\Scripts\python.exe`；這是本書後面指令採用的寫法。若希望允許目前使用者執行本機腳本，可查閱 Microsoft 對 PowerShell ExecutionPolicy 的說明，再依公司或個人電腦政策設定。

## 2.3　安裝 Python 套件

使用虛擬環境中的 Python 安裝固定版本：

Linux、macOS 和 WSL：

```bash
.venv/bin/python -m pip install -r requirements.txt
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` 目前固定 `playwright==1.63.0`，讓書中範例的 API 與讀者安裝的版本一致。安裝完成後查詢版本：

```bash
.venv/bin/python -m playwright --version
```

Windows 對應命令是：

```powershell
.\.venv\Scripts\python.exe -m playwright --version
```

若輸出包含 `1.63.0`，Python 套件已安裝。`pip` 顯示更新通知不代表安裝失敗；本書先以固定版本完成驗證，之後升級時要重新檢查範例。

## 2.4　安裝瀏覽器

Playwright 套件不會把所有瀏覽器一起放進 Python 環境。再執行一次安裝命令，下載 Chromium：

```bash
.venv/bin/python -m playwright install chromium
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe -m playwright install chromium
```

下載時間取決於網路速度。Linux 如果啟動瀏覽器時顯示缺少系統函式庫，可以使用：

```bash
.venv/bin/python -m playwright install --with-deps chromium
```

這會嘗試安裝作業系統套件，可能需要管理員權限；公司電腦或受管理環境應先取得允許。Windows 與 macOS 一般不使用 `--with-deps`。

本書多數範例只需要 Chromium。若日後要測試其他瀏覽器，可以再安裝 `firefox` 或 `webkit`，不必一開始全部下載。

## 2.5　用最小程式驗證

不先連線真實網站，先用專案已有的最小範例驗證四件事：Python 找得到 Playwright、Chromium 已安裝、瀏覽器能啟動、程式能讀到頁面標題。

Linux、macOS 和 WSL：

```bash
.venv/bin/python examples/01_basics/open_page.py
```

Windows PowerShell：

```powershell
.\.venv\Scripts\python.exe examples/01_basics/open_page.py
```

預期會在終端機看到 Playwright 網站的標題，程式隨後結束。範例使用有畫面的瀏覽器；若你在沒有圖形介面的 Linux 伺服器上執行，請先把程式的 `launch()` 改成 `launch(headless=True)`，或使用本章後面的檢查指令。

接著只讀取命令列說明，不會連線或修改外部網站：

```bash
.venv/bin/python examples/04_tracking/happyebook_new_books.py --help
```

如果兩個命令都成功，基礎環境已經完成。各範例的輸出會在執行時建立於 `outputs/`；第一次執行新書雷達時會建立你自己的基準資料。

## 2.6　用一個檢查表找出問題

安裝失敗時，不要先重灌所有東西。依照「命令使用哪個 Python → 套件是否存在 → 瀏覽器是否存在」的順序檢查：

```bash
.venv/bin/python --version
.venv/bin/python -c "import playwright; print(playwright.__file__)"
.venv/bin/python -m playwright --version
.venv/bin/python -m playwright install chromium
```

Windows PowerShell 將 `.venv/bin/python` 換成 `.\.venv\Scripts\python.exe`。四個命令分別確認 Python、Python 模組、Playwright CLI 和 Chromium 安裝步驟。最後一個命令即使顯示瀏覽器已存在，也代表安裝檢查完成。

常見訊息與處理方式如下：

| 訊息或現象 | 可能原因 | 處理方式 |
|---|---|---|
| `No module named playwright` | 使用了系統 Python，或尚未安裝套件 | 使用 `.venv` 裡的 Python，再執行 `pip install -r requirements.txt` |
| `Executable doesn't exist` | 尚未下載 Chromium | 執行 `python -m playwright install chromium` |
| PowerShell 不允許啟用腳本 | 執行原則限制 | 不啟用環境，直接使用 `.venv\Scripts\python.exe` |
| Linux 缺少 shared library | 作業系統套件不足 | 以 `playwright install --with-deps chromium` 補齊，或請管理員安裝 |
| 程式開啟登入頁 | 使用新的工作階段，沒有既有 Cookie | 公開頁面先確認網址；登入案例閱讀第 8 章與讀者帳號設定 |
| 頁面載入但沒有資料 | 外部網站改版、休市或查詢條件沒有結果 | 保存錯誤訊息與查詢日期，不把失敗當成零筆資料 |

最後一項很重要：Playwright 能啟動不代表每個網站今天都一定有資料。環境問題和外部資料問題要分開判斷，後續案例會把這兩種情況明確區分。

## 2.7　整理安裝結果

完成後，請記錄下列資訊，之後回報問題或重建環境會更容易：

```text
作業系統：Windows / macOS / Linux / WSL
Python：3.x.x
Playwright：x.x.x
瀏覽器：Chromium 已安裝
首次驗證：examples/01_basics/open_page.py 成功／失敗
```

不要把 `.venv` 壓縮進書籍附檔，也不要把瀏覽器快取上傳 GitHub。讀者只需要 `requirements.txt` 和 `playwright install chromium` 就能重建相同環境。

## 2.8　練習

1. 在不啟用虛擬環境的情況下，使用完整路徑執行 `open_page.py`。
2. 刪除 `.venv` 後重新建立，執行本章四個檢查命令。
3. 將第一個範例改為 `headless=True`，比較有畫面和沒有畫面時的執行差異。

完成條件是：你能說出本機使用的 Python 版本和 Playwright 版本，能重新安裝 Chromium，並能從專案根目錄成功執行 E01。下一章會閱讀這支最小程式，逐行理解瀏覽器、頁面和標題是如何串起來的。

<!-- 編輯紀錄：初稿；2026-09-17 依官方 Python 安裝文件與本專案 requirements.txt 整理。Linux 系統套件、PowerShell 政策及各平台實際下載結果需在出版前以乾淨環境重新驗證。 -->
