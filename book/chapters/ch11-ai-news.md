# 第 11 章　今日 AI 新聞：日期篩選、內容去重與報告輸出

新聞程式和前幾章不同：它使用 Playwright 的 `APIRequestContext` 讀取 RSS，不必開啟瀏覽器。這不是少了 Playwright，而是選擇較適合結構化資料的介面。

## 11.1　RSS 是什麼

RSS 通常包含標題、連結、來源、發布時間和摘要。E06 會向中文、英文和指定公司相關 RSS 發送請求，再以台灣時區判斷今天的項目。每個來源格式可能略有差異，程式先解析共同欄位，再統一成自己的記錄。

```python
with sync_playwright() as p:
    request = p.request.new_context(extra_http_headers={"User-Agent": "playwright-exercise"})
    response = request.get(feed_url, timeout=30_000)
    response.raise_for_status()
    xml = response.text()
```

請求完成後呼叫 `request.dispose()`。不把 HTTP 請求誤寫成瀏覽器點擊，可以讓程式更快，也能清楚看出資料來源。

## 11.2　日期和時區

「今天」應以 `Asia/Taipei` 判斷，不能假定執行主機一定在台灣。RSS 時間可能帶 UTC、時區偏移或只有日期；解析失敗時，將該項標記為無法判讀並記錄原因，不要偷偷當成本日。

執行：

```bash
.venv/bin/python examples/03_data_queries/ai_news_today.py --limit 30
```

`--date` 可以指定教學或重現日期，`--limit 0` 表示不限制每個來源的結果。輸出目錄包含 JSON 和 Markdown 報告，報告中保存查詢時間、來源和篩選日期。

## 11.3　去重與排序

同一則新聞可能同時出現在中文和英文來源。優先使用規範化 URL 去重，沒有 URL 才使用標題加來源組合。排序用發布時間的新到舊；無法解析時間的項目排在最後，並保留原始字串供人工檢查。

```python
key = canonical_url or (title.strip().casefold(), source)
if key not in seen:
    seen.add(key)
    articles.append(record)
```

去重不等於判斷新聞真偽。這個範例只整理來源提供的項目，不替讀者驗證內容。

## 11.4　錯誤和限制

某一個 RSS 來源失敗時，程式可以保留其他成功來源，但報告必須列出失敗清單。若所有來源都失敗，程序應以錯誤結束。空結果可能表示今天沒有符合條件的新聞，也可能表示來源的日期格式改了，兩者需要從報告和錯誤欄位判斷。

## 11.5　練習

1. 用 `--date` 重跑一個過去日期，觀察報告的查詢條件。
2. 加入一個 RSS URL，為它寫一個最小解析測試。
3. 將報告增加「每個來源幾則」的統計，並保留失敗來源。

下一章回到需要操作表單的網站，查詢臺鐵彰化到嘉義的指定時段。

<!-- 編輯紀錄：初稿；搭配 E06、AI_NEWS 指南。 -->
