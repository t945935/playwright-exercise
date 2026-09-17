"""讀取 AI 整理的 JSON，新增電子書或接續指定草稿，填寫書籍資料。"""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urlparse
import subprocess
import sys

TARGET_URL = os.environ.get("PLAY_BOOKS_PUBLISHER_URL", "")
BOOK_LANGUAGE = "中文"


def load_metadata(filename):
    data = json.loads(Path(filename).read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("書籍資料必須是 JSON 物件。")
    fields = ("BOOK_TITLE", "BOOK_SUBTITLE", "BOOK_DESCRIPTION")
    for key in fields:
        if key not in data or not isinstance(data[key], str):
            raise ValueError(f"{key} 必須是字串，且不可省略。")
        if key != "BOOK_SUBTITLE" and not data[key].strip():
            raise ValueError(f"{key} 不可空白。")
    # 副標可明確指定空字串；保留正文段落、標點與 Unicode。
    return {key: data[key] for key in fields}


def run_on_windows(args):
    version = Path("/proc/version")
    if sys.platform != "linux" or not version.exists():
        return False
    if "microsoft" not in version.read_text().lower():
        return False
    script = subprocess.check_output(
        ["wslpath", "-w", str(Path(__file__).resolve())], text=True
    ).strip()
    quoted_script = "'" + script.replace("'", "''") + "'"
    metadata_path = subprocess.check_output(
        ["wslpath", "-w", str(Path(args.metadata).resolve())], text=True
    ).strip()
    arguments = " --metadata '" + metadata_path.replace("'", "''") + "'"
    if args.book_url:
        arguments += " --book-url '" + args.book_url.replace("'", "''") + "'"
    endpoint_setting = ""
    for key in ("PLAY_BOOKS_PUBLISHER_URL", "CHROME_CDP_URL"):
        if os.environ.get(key):
            value = os.environ[key].replace("'", "''")
            endpoint_setting += f"$env:{key} = '{value}'; "
    command = (
        endpoint_setting + "$env:PYTHONIOENCODING = 'utf-8'; "
        f"& python.exe {quoted_script}{arguments}; exit $LASTEXITCODE"
    )
    result = subprocess.run(["powershell.exe", "-NoProfile", "-Command", command])
    if result.returncode:
        raise SystemExit(result.returncode)
    return True


def select_google_book_id(page):
    from playwright.sync_api import expect

    book_id_name = re.compile(r"書籍\s*ID|图书\s*ID|Book ID", re.I)
    google_id_name = re.compile(
        r"^(取得\s*Google\s*書籍\s*ID|Get a Google (?:Book|Books) ID)"
        r"(?:\s*[（(]GGKEY[）)])?\s*$", re.I,
    )
    book_id = page.get_by_role("combobox", name=book_id_name).or_(
        page.get_by_label(book_id_name)
    ).filter(visible=True).first
    book_id.wait_for(state="visible")

    if book_id.evaluate("element => element.tagName") == "SELECT":
        labels = book_id.locator("option").all_text_contents()
        label = next((text for text in labels if google_id_name.fullmatch(text.strip())), None)
        if label is None:
            raise RuntimeError(f"找不到取得 Google 書籍 ID 選項，目前選項：{labels}")
        book_id.select_option(label=label)
        expect(book_id.locator("option:checked")).to_have_text(google_id_name)
    else:
        if book_id.get_attribute("aria-expanded") != "true":
            book_id.click()
        option = page.get_by_role("option", name=google_id_name).filter(visible=True).first
        option.wait_for(state="visible")
        option.click()
        expect(book_id).to_contain_text(google_id_name)
        expect(book_id).to_have_attribute("aria-expanded", "false")


def fill_book_details(page, metadata):
    from playwright.sync_api import expect

    BOOK_TITLE = metadata["BOOK_TITLE"]
    BOOK_SUBTITLE = metadata["BOOK_SUBTITLE"]
    BOOK_DESCRIPTION = metadata["BOOK_DESCRIPTION"]
    title = page.get_by_role("textbox", name="書名", exact=True)
    title.fill(BOOK_TITLE)
    expect(title).to_have_value(BOOK_TITLE)

    # 新增副標題按鈕在書名空白時停用；先填書名再等待按鈕可用。
    subtitle = page.get_by_role("textbox", name=re.compile(r"^副標題"))
    if BOOK_SUBTITLE or subtitle.is_visible():
        if not subtitle.is_visible():
            add_subtitle = page.get_by_role("button", name="新增副標題", exact=True)
            expect(add_subtitle).to_be_enabled(timeout=30000)
            add_subtitle.click()
        subtitle.fill(BOOK_SUBTITLE)
        expect(subtitle).to_have_value(BOOK_SUBTITLE)

    description = page.get_by_role("textbox", name="說明", exact=True)
    description.fill(BOOK_DESCRIPTION)
    if description.evaluate("element => ['INPUT', 'TEXTAREA'].includes(element.tagName)"):
        expect(description).to_have_value(BOOK_DESCRIPTION)
    else:
        expect(description).to_have_text(BOOK_DESCRIPTION)

    # 實際頁面的語言下拉選單沒有 accessible name；其餘下拉選單均有名稱。
    language = page.get_by_role("combobox", name="", exact=True).filter(visible=True)
    expect(language).to_have_count(1)
    if language.evaluate("element => element.tagName") == "SELECT":
        language.select_option(label=BOOK_LANGUAGE)
        expect(language.locator("option:checked")).to_have_text(BOOK_LANGUAGE)
    else:
        language.click()
        chinese = page.get_by_role("option", name=BOOK_LANGUAGE, exact=True).filter(visible=True)
        chinese.click()
        expect(language).to_contain_text(BOOK_LANGUAGE)
        expect(language).to_have_attribute("aria-expanded", "false")

    print(f"書名：{BOOK_TITLE}")
    print(f"副標題：{BOOK_SUBTITLE}")
    print(f"說明：{BOOK_DESCRIPTION}")
    print(f"語言：{BOOK_LANGUAGE}")
    print("欄位已填妥，停在書籍資訊畫面，請檢查後自行儲存。")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--metadata", required=True, help="AI 整理的 UTF-8 JSON 檔案")
    parser.add_argument("--validate-only", action="store_true", help="只檢查資料，不連接瀏覽器")
    parser.add_argument("--dry-run", action="store_true", help="檢查資料並顯示目標，不連接或修改後台")
    parser.add_argument("--book-url", help="接續已建立的書籍資訊網址，避免重複建立書籍")
    args = parser.parse_args()
    metadata = load_metadata(args.metadata)
    if args.book_url and not re.fullmatch(
        r"https://play\.google\.com/books/publish/a/[0-9]+#book/(?!create(?:/|$))[^/?#]+/info/about", args.book_url
    ):
        raise ValueError("--book-url 必須是此出版帳戶的書籍 /info/about 頁面。")
    if args.validate_only or args.dry_run:
        print(json.dumps(metadata, ensure_ascii=False, indent=2))
        if args.dry_run:
            print(f"目標：{args.book_url or TARGET_URL or '(未設定 PLAY_BOOKS_PUBLISHER_URL)'}")
            print("dry-run：資料檢查通過；未連接瀏覽器、未建立或修改書籍。")
        else:
            print("資料檢查通過；未連接瀏覽器。")
        return
    if not re.fullmatch(r"https://play\.google\.com/books/publish/a/[0-9]+#home", TARGET_URL):
        raise ValueError("請先設定 PLAY_BOOKS_PUBLISHER_URL；或先使用 --dry-run。")
    # Windows Chrome 與 WSL 各有自己的 localhost，改由 Windows Python 連線。
    if run_on_windows(args):
        return
    from playwright.sync_api import sync_playwright, expect

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
            destination = args.book_url or TARGET_URL
            page = next((tab for tab in context.pages if tab.url == destination), None)
            if page is None:
                page = context.new_page()
                page.goto(destination, wait_until="domcontentloaded", timeout=60000)
            page.set_default_timeout(30000)
            page.bring_to_front()
            if urlparse(page.url).hostname == "accounts.google.com":
                raise RuntimeError(
                    "此 Chrome 需要重新登入。請在一般 Chrome 完成登入後再執行。"
                )
            if not args.book_url:
                # 主選單在桌面寬版可能已展開；若目錄已可見，就直接選取。
                catalog_name = re.compile(r"^(書籍目錄|图书目录|Book catalog|Book catalogue)$", re.I)
                catalog = page.get_by_role("link", name=catalog_name).or_(
                    page.get_by_role("menuitem", name=catalog_name)
                ).or_(page.get_by_role("button", name=catalog_name)).or_(
                    page.get_by_text(catalog_name, exact=True)
                ).filter(visible=True).first

                if not catalog.is_visible():
                    menu = page.get_by_role(
                        "button",
                        name=re.compile(
                            r"主選單|主要選單|開啟.*選單|導覽選單|主菜单|Main menu|Open.*menu|Navigation menu",
                            re.I,
                        ),
                    ).filter(visible=True).first
                    menu.click()
                    print("已開啟主選單", flush=True)

                catalog.click()
                print("已切換到書籍目錄", flush=True)

                add_name = re.compile(r"^(新增書籍|新增圖書|添加图书|Add book|Add a book)$", re.I)
                add_book = page.get_by_role("button", name=add_name).or_(
                    page.get_by_role("link", name=add_name)
                ).or_(page.get_by_text(add_name, exact=True)).filter(visible=True).first
                add_book.click()
                print("已點選新增書籍", flush=True)

                sale_name = re.compile(r"販售方式|銷售方式|销售方式|sell option", re.I)
                ebook_name = re.compile(
                    r"^(在\s*Google(?:\s*Play)?\s*(?:販售|銷售)電子書|Sell (?:an )?e-?book on Google Play)$",
                    re.I,
                )
                sale_method = page.get_by_role("combobox", name=sale_name).or_(
                    page.get_by_role("listbox", name=sale_name)
                ).or_(page.get_by_label(sale_name)).filter(visible=True).first
                sale_method.wait_for(state="visible")

                if sale_method.evaluate("element => element.tagName") == "SELECT":
                    # 原生下拉選單使用 select_option，避免點擊隱藏的 option。
                    labels = sale_method.locator("option").all_text_contents()
                    label = next((text for text in labels if ebook_name.fullmatch(text.strip())), None)
                    if label is None:
                        raise RuntimeError(f"找不到販售電子書選項，目前選項：{labels}")
                    sale_method.select_option(label=label)
                else:
                    sale_method.click()
                    ebook_option = page.get_by_role("option", name=ebook_name).or_(
                        page.get_by_text(ebook_name, exact=True)
                    ).filter(visible=True).first
                    ebook_option.click()

                print("已選取「在 Google Play 販售電子書」", flush=True)

                select_google_book_id(page)

                print("已選取「取得 Google 書籍 ID」", flush=True)
                save_and_continue = page.get_by_role(
                    "button", name=re.compile(r"^(儲存並繼續|保存并继续|Save (?:and|&) continue)$", re.I)
                )
                expect(save_and_continue).to_be_enabled(timeout=30000)
                save_and_continue.click()
                # 等待原本的書籍 ID 選單消失，確認已離開新增書籍的選擇步驟。
                expect(page.get_by_role(
                    "combobox", name=re.compile(r"書籍\s*ID|图书\s*ID|Book ID", re.I)
                ).first).to_be_hidden(timeout=30000)
                print("已點選「儲存並繼續」，並進入下一步。")
            print(f"BOOK_URL={page.url}", flush=True)
            fill_book_details(page, metadata)
            print(f"目前網址：{page.url}")
        except Exception:
            if 'page' in locals():
                print(f"操作失敗，請先檢查目前頁面再重試：{page.url}", file=sys.stderr, flush=True)
            raise
        finally:
            # 只中斷 CDP 控制連線，原本的 Chrome 及出版中心分頁仍保持開啟。
            browser.close()


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"執行失敗：{error}", file=sys.stderr)
        sys.exit(1)
