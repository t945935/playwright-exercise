"""執行後會在 Blogger 發布一篇「新文章測試3」，沿用已登入的 Chrome。"""
import os
from pathlib import Path
import re
import subprocess
import sys

EMAIL = os.environ.get("BLOGGER_EMAIL", "")
BLOG_URL = os.environ.get("BLOGGER_PUBLIC_URL", "")
BLOG_ID = os.environ.get("BLOGGER_BLOG_ID", "")
ADMIN_URL = f"https://www.blogger.com/blog/posts/{BLOG_ID}?hl=zh-TW"
POST_TITLE = "新文章測試3"
POST_CONTENT = "新文章測試3"


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
        edit_url = None
        publish_requested = False
        try:
            page = browser.contexts[0].new_page()
            page.set_default_timeout(30000)
            page.goto(ADMIN_URL, wait_until="domcontentloaded")
            account = page.get_by_role("button", name=re.compile(re.escape(EMAIL)))
            try:
                expect(account).to_be_visible(timeout=15000)
            except AssertionError as error:
                raise RuntimeError(
                    f"未確認 {EMAIL} 的登入狀態。請在一般 Chrome 手動登入或切換到此帳號，再執行程式。"
                ) from error
            print(f"已確認登入帳號：{EMAIL}")
            page.bring_to_front()
            create = page.locator('[aria-label="建立新文章"]:visible').first
            if create.count() == 0:
                page.get_by_role("button", name="主選單", exact=True).click()
            create.click()
            page.wait_for_url(re.compile(rf"/blog/post/edit/{BLOG_ID}/[0-9]+"))
            edit_url = page.url
            print(f"新文章編輯頁：{edit_url}", flush=True)

            title = page.get_by_role("textbox", name="標題", exact=True)
            # 可見 iframe 才是正文；避免選到 Google 選單的隱藏 iframe。
            editor = page.frame_locator("iframe:visible").locator("body")
            title.fill(POST_TITLE)
            editor.click()
            page.keyboard.insert_text(POST_CONTENT)
            expect(title).to_have_value(POST_TITLE)
            expect(editor).to_have_text(POST_CONTENT)

            page.get_by_role("button", name="發布", exact=True).click()
            confirm = page.get_by_role("alertdialog").get_by_role(
                "button", name="確認", exact=True
            )
            confirm.wait_for(state="visible")
            publish_requested = True
            confirm.click()
            page.wait_for_url(re.compile(rf"/blog/posts/{BLOG_ID}(?:[?]|$)"))

            post_id = edit_url.split("?")[0].rstrip("/").split("/")[-1]
            row = page.get_by_role("listitem").filter(
                has=page.locator(f'a[href$="/blog/post/edit/{BLOG_ID}/{post_id}"]')
            ).last
            expect(row).to_contain_text(POST_TITLE)
            expect(row).to_contain_text("已發布")
            print(f"已發布：{POST_TITLE}", flush=True)

            public_link = row.locator(f'a[href^="{BLOG_URL}"]').first
            public_link.wait_for(state="attached")
            public_url = public_link.get_attribute("href")
            page.goto(public_url, wait_until="domcontentloaded")
            expect(page.locator(".post-title").first).to_have_text(POST_TITLE)
            expect(page.locator(".post-body").first).to_have_text(POST_CONTENT)
            print(f"已確認公開頁面的標題與內文：{POST_CONTENT}")
            print(f"文章網址：{public_url}")
        except Exception:
            if edit_url:
                print(f"請檢查此篇文章：{edit_url}", file=sys.stderr)
            if publish_requested:
                print("已嘗試送出發布，請先確認文章狀態，避免重跑造成重複貼文。", file=sys.stderr)
            raise
        finally:
            # 只中斷 CDP 控制連線，原本的 Chrome 及網誌分頁仍保持開啟。
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}", file=sys.stderr)
        sys.exit(1)
