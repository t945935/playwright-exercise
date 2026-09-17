# 附錄 B　Windows、macOS、Linux 與 WSL 執行差異

所有範例都從專案根目錄執行；差別主要是 Python 執行檔路徑和 shell 語法。

| 環境 | Python | 啟用環境 | 常見注意事項 |
|---|---|---|---|
| Windows PowerShell | `.venv\\Scripts\\python.exe` | `.\\.venv\\Scripts\\Activate.ps1` | 執行原則、路徑分隔符、Chrome CDP |
| macOS | `.venv/bin/python` | `source .venv/bin/activate` | 系統 Python 權限、Intel／Apple Silicon |
| Linux | `.venv/bin/python` | `source .venv/bin/activate` | 系統 shared library、無畫面伺服器 |
| WSL | `.venv/bin/python`（公開頁面） | `source .venv/bin/activate` | 連 Windows Chrome 時需 Windows Python |

相同的 Python `Path` 程式可跨平台處理檔案，但外部命令、通知工具和 Chrome profile 不一定相同。登入範例的 WSL 轉接流程見第 8 章；沒有必要登入的案例不應依賴既有 profile。

Windows 若要將輸出路徑傳給參數，使用 PowerShell 的引號；Bash 使用單引號包住包含空白的路徑。不要把 `/home/...` 或 `C:\Users\...` 寫進可供所有讀者複製的排程設定。
