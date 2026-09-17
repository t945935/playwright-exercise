"""沿用已登入的 Windows Chrome，開啟 Google Play 圖書出版中心。"""
import os
import re
from pathlib import Path
from urllib.parse import urlparse
import subprocess
import sys

TARGET_URL = os.environ.get("PLAY_BOOKS_PUBLISHER_URL", "")


def run_on_windows():
    version = Path("/proc/version")
    if sys.platform != "linux" or not version.exists():
        return False
    if "microsoft" not in version.read_text().lower():
        return False
    script = subprocess.check_output(
        ["wslpath", "-w", str(Path(__file__).resolve())], text=True
    ).strip()
    quoted_script = "'" + script.replace("'", "''") + "'"
    publisher = TARGET_URL.replace("'", "''")
    endpoint_setting = f"$env:PLAY_BOOKS_PUBLISHER_URL = '{publisher}'; "
    if os.environ.get("CHROME_CDP_URL"):
        endpoint = os.environ["CHROME_CDP_URL"].replace("'", "''")
        endpoint_setting += f"$env:CHROME_CDP_URL = '{endpoint}'; "
    command = (
        endpoint_setting + "$env:PYTHONIOENCODING = 'utf-8'; "
        f"& python.exe {quoted_script}; exit $LASTEXITCODE"
    )
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command])
    if result.returncode:
        raise SystemExit(result.returncode)
    return True


def main():
    if not re.fullmatch(r"https://play\.google\.com/books/publish/a/[0-9]+#home", TARGET_URL):
        raise ValueError("請先設定 PLAY_BOOKS_PUBLISHER_URL；詳見 docs/guides/reader-accounts.md。")
    # Windows Chrome 與 WSL 各有自己的 localhost，改由 Windows Python 連線。
    if run_on_windows():
        return
    from playwright.sync_api import sync_playwright

    endpoint = os.environ.get("CHROME_CDP_URL")
    if not endpoint:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("請使用 Windows Python，或設定 CHROME_CDP_URL。")
        port_file = Path(local_app_data) / "Google/Chrome/User Data/DevToolsActivePort"
        if not port_file.exists():
            raise RuntimeError("請先在 Chrome 開啟 chrome://inspect/#remote-debugging 並啟用遠端偵錯。")
        parts = port_file.read_text().strip().splitlines()
        if len(parts) < 2 or not parts[0].isdigit() or not parts[1].startswith("/devtools/browser/"):
            raise RuntimeError("Chrome 連線資料無效，請重新啟用遠端偵錯。")
        endpoint = f"ws://127.0.0.1:{parts[0]}{parts[1]}"

    print("正在連接已登入的 Chrome；出現提示時請按「允許」。", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(endpoint, timeout=60000)
        try:
            context = browser.contexts[0]
            # 若首頁已開啟，就使用該分頁；其他書籍編輯分頁保持原狀。
            page = next((tab for tab in context.pages if tab.url == TARGET_URL), None)
            if page is None:
                page = context.new_page()
                page.goto(TARGET_URL, wait_until="domcontentloaded", timeout=60000)
            page.bring_to_front()
            if urlparse(page.url).hostname == "accounts.google.com":
                raise RuntimeError(
                    "此 Chrome 需要重新登入。請在一般 Chrome 完成登入後再執行。"
                )
            print(f"網頁標題：{page.title()}")
            print(f"目前網址：{page.url}")
            print("已沿用 Chrome 的現有登入狀態；請在瀏覽器中確認出版中心已載入。")
        finally:
            # 只中斷 CDP 控制連線，原本的 Chrome 及出版中心分頁仍保持開啟。
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}", file=sys.stderr)
        sys.exit(1)
