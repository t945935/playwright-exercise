# 附錄 C　安裝失敗與常見錯誤排除

先取得版本和完整錯誤，再決定要修哪一層：

```bash
.venv/bin/python --version
.venv/bin/python -c "import playwright; print(playwright.__file__)"
.venv/bin/python -m playwright --version
```

`No module named playwright` 表示使用錯誤的 Python 或尚未安裝套件；`Executable doesn't exist` 表示尚未執行 `playwright install chromium`；Linux shared library 錯誤可嘗試 `playwright install --with-deps chromium`。

若定位器逾時，先用 `--headed` 觀察頁面網址、登入狀態和可見文字，再確認角色、名稱和 CSS。不要先加大 timeout，也不要用空清單掩蓋例外。若頁面成功但結果為零，檢查查詢日期、休市、活動截止或網站改版。

回報時保留：範例路徑、完整命令、版本、作業系統、執行時間、stderr 和必要的非私人頁面資訊。刪除 Cookie、Token、帳號和私有網址後再貼上。
