"""接用已登入的 Windows Chrome，開啟 Blogger；不自動輸入密碼。"""
import os
from pathlib import Path
import re
import subprocess
import sys

EMAIL = os.environ.get("BLOGGER_EMAIL", "")
BLOG_URL = os.environ.get("BLOGGER_PUBLIC_URL", "")
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID", "")
ADMIN_URL = f"https://www.blogger.com/blog/posts/{BLOG_ID}"


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
    forwarded = ""
    for key in ("BLOGGER_EMAIL", "BLOGGER_BLOG_ID", "BLOGGER_PUBLIC_URL", "BLOGGER_CDP_URL"):
        if os.environ.get(key):
            value = os.environ[key].replace("'", "''")
            forwarded += f"$env:{key} = '{value}'; "
    command = (
        forwarded +
        "$env:PYTHONIOENCODING = 'utf-8'; "
        f"& python.exe {quoted_script}; exit $LASTEXITCODE"
    )
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command])
    if result.returncode:
        raise SystemExit(result.returncode)
    return True


def main():
    if not EMAIL or not BLOG_ID.isdigit() or not BLOG_URL.startswith("https://"):
        raise ValueError("請先設定 BLOGGER_EMAIL、BLOGGER_BLOG_ID 與 BLOGGER_PUBLIC_URL；詳見 docs/guides/reader-accounts.md。")
    # Windows Chrome 與 WSL 各有自己的 localhost，改由 Windows Python 連線。
    if run_on_windows():
        return
    from playwright.sync_api import sync_playwright, expect

    endpoint = os.environ.get("BLOGGER_CDP_URL")
    if not endpoint:
        local_app_data = os.environ.get("LOCALAPPDATA")
        if not local_app_data:
            raise RuntimeError("請使用 Windows Python，或設定 BLOGGER_CDP_URL。")
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
            page = browser.contexts[0].new_page()
            page.goto(ADMIN_URL, wait_until="domcontentloaded")
            account = page.get_by_role("button", name=re.compile(re.escape(EMAIL)))
            try:
                expect(account).to_be_visible(timeout=15000)
            except AssertionError as error:
                raise RuntimeError(
                    f"未確認 {EMAIL} 的登入狀態。請在一般 Chrome 手動登入或切換到此帳號，再執行程式。"
                ) from error
            print(f"已確認登入帳號：{EMAIL}")
            page.goto(BLOG_URL, wait_until="domcontentloaded")
            page.bring_to_front()
            print(f"網頁標題：{page.title()}")
            print(f"已開啟：{page.url}")
        finally:
            # 只中斷 CDP 控制連線，原本的 Chrome 及網誌分頁仍保持開啟。
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}", file=sys.stderr)
        sys.exit(1)
