# 第 4 章　必備 Python 基礎：函式、資料結構、檔案與例外處理

Playwright 只負責瀏覽器和 HTTP 操作；資料整理仍是 Python 的工作。本章不試圖教完 Python，而是集中在 16 個範例反覆使用的語法，讓你看懂後續程式，也能把需求拆成可測試的小函式。

## 4.1　用函式切開責任

一個函式應該有清楚的輸入和輸出。例如把書卡整理成字典：

```python
def book_record(title: str, url: str) -> dict[str, str]:
    return {"title": title.strip(), "url": url}
```

函式不直接開瀏覽器、不寫檔案，因此容易用固定資料測試。瀏覽器函式只負責取得資料，`main()` 再決定輸出路徑和顯示方式。當網站改版時，修改定位邏輯不會同時影響報告格式。

## 4.2　清單、字典與型別

書單是清單，清單中的每一筆是字典：

```python
books = [
    {"title": "A", "url": "https://example.com/a"},
    {"title": "B", "url": "https://example.com/b"},
]
urls = {book["url"] for book in books}
```

集合用來快速去重，字典用欄位名稱表達意義。`list[dict[str, str]]` 這類型別標註不會替你驗證資料，但能讓編輯器和讀者知道預期形狀。若來源可能缺欄位，先用明確例外拒絕不完整資料，比在後面出現難懂的 `KeyError` 好。

## 4.3　Path 與 JSON

`pathlib.Path` 比手動串接斜線更適合跨平台：

```python
import json
from pathlib import Path

output = Path("outputs/books.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(books, ensure_ascii=False, indent=2) + "\\n",
    encoding="utf-8",
)
```

`ensure_ascii=False` 保留中文，`indent=2` 方便人工檢查。讀取時使用 `json.loads(path.read_text(encoding="utf-8"))`，並檢查回傳值確實是清單或字典。新書雷達和電子書 metadata 範例都把 JSON 當作程式之間的清楚界面。

## 4.4　參數與預設值

命令列參數讓同一支程式可以查不同日期或輸出目錄：

```python
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=30)
parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
args = parser.parse_args()
```

預設值適合教學，但不能藏住環境差異。與登入、帳號相關的值應使用環境變數或必要參數；本書讀者版已把 Blogger 與 Play Books 帳號改為這種設定。

## 4.5　例外不是零筆資料

把「查詢失敗」和「成功但沒有結果」分開：

```python
try:
    response = page.goto(url, wait_until="domcontentloaded")
    if response is None or not response.ok:
        raise RuntimeError("頁面沒有成功回應")
except Exception as error:
    raise RuntimeError(f"查詢失敗：{error}") from error
```

捕捉例外後要補上上下文，再交給最外層顯示或記錄。不要寫成 `except Exception: return []`，那會把網路中斷、選擇器錯誤和真正的空結果混在一起。

## 4.6　以資料模型思考

每個案例先定義最小記錄：新聞需要標題、連結、來源和時間；班次需要車次、出發、抵達；行情需要成交價、來源時間和查詢時間。欄位先定義清楚，才知道頁面缺少哪項資料，以及報告應該如何呈現。

練習：為活動提醒設計一個字典，至少包含 `name`、`url`、`checked_at`、`available` 四個欄位。接著寫一個函式，把字典轉成一行 JSON。下一章會把這些資料結構接到 Locator，讀取真正的網頁元素。

<!-- 編輯紀錄：初稿；範例語法取自 E05、E06、E10、E12、E16。 -->
