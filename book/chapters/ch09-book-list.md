# 第 9 章　書籍清單蒐集：取得 Happy eBook 的 AI Agent 書單

本章把定位器、等待和 JSON 組合成第一個完整資料擷取案例。目標不是只印出目前看到的幾張書卡，而是確認 AI Agent 分類的完整列表，再保存書名、副標題和連結。

## 9.1　把人工流程寫成規格

人工步驟是：開啟 Happy eBook 首頁、點「書籍列表」、選 AI Agent、按「顯示更多書籍」直到全部出現，逐張讀取資訊。程式的完成條件是卡片數等於網站顯示總數，且每筆都有標題和有效的詳細頁網址。

執行：

```bash
.venv/bin/python examples/03_data_queries/happyebook_ai_agent.py --headless
```

預設輸出是專案 `outputs/books/ai_agent_books.json`。也可以指定自己的檔案：

```bash
.venv/bin/python examples/03_data_queries/happyebook_ai_agent.py --output /tmp/ai-agent.json
```

預期輸出會列出書名與詳細頁網址，最後顯示類似：

```text
AI Agent 分類共 28 筆書目：
...
已儲存至：/tmp/ai-agent.json
```

筆數會隨網站變動；請以 JSON 是否包含 `title`、`url` 和 `reading_url` 為成功判斷。

## 9.2　展開直到完整

E05 先讀取 `[data-books-count]` 摘要，從文字解析「目前顯示／總數」。每次點擊後等待原本未附加的下一張卡片，再重新讀取摘要。它不假設總數永遠是 28，因為網站可能增加或移除書籍。

```python
shown, total = map(int, re.search(r"(\d+)\s*/\s*(\d+)", summary.inner_text()).groups())
while shown < total:
    more.click()
    expect(cards.nth(shown)).to_be_attached()
    shown, total = read_count(summary.inner_text())
expect(cards).to_have_count(total)
```

這裡有兩個檢查：摘要宣稱的總數，以及 DOM 實際卡片數。只檢查其中一個，仍可能把載入不完整當成成功。

## 9.3　保存可用的欄位

每張卡片讀取 `h3` 標題、副標題、更多資訊網址和封面連結。網址使用 `evaluate("link => link.href")` 取得瀏覽器解析後的絕對網址，避免讀者在不同工作目錄執行時得到難以使用的相對路徑。

輸出 JSON 前先確認網址不重複。若同名書籍有不同詳細頁，保留兩筆；辨識一本書的鍵是詳細頁 URL，而不是書名。這個決定會影響第 10 章的比較結果。

## 9.4　結果驗證與失敗處理

頁面載入失敗、摘要文字改版、卡片數不一致和空書單都要報錯。程式不應把這些情況寫成空 JSON，否則讀者會誤以為網站當天沒有書。若網站改版，先保存錯誤頁面，再更新定位器；不要直接放寬所有檢查。

## 9.5　練習

1. 執行程式後讀取 JSON，確認每筆至少有 `title` 和 `url`。
2. 將輸出改成 `/tmp/books.json`，比較絕對輸出路徑和預設輸出。
3. 修改程式使它同時輸出書卡總數和查詢時間，並在 JSON 頂層加入 metadata。

下一章會保留這份完整書單，第二次執行時找出相較上次新增的書籍。

<!-- 編輯紀錄：初稿；搭配 E05、happyebook_ai_agent.py。網站內容會隨日期變動，書中不固定宣稱筆數。 -->
