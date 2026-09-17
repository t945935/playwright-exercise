# 第 6 章　操作表單：輸入、點擊、下拉選單與等待

查詢車次的工作流程很適合學習表單：選日期、選出發站、選抵達站、設定時間，再按查詢。每個動作都可能觸發頁面更新，因此要同時處理輸入方式和等待條件。

## 本章目標

完成後，你能填寫表單、等待結果，並分辨表單錯誤、查無資料和成功查詢。

## 執行前準備

需要第 2 章的環境；臺鐵與高鐵命令會連線官方網站，固定資料練習請先使用第 12、13 章的輸出檔。

## 6.1　輸入與選擇

文字輸入使用 `fill()`，它會先清除原值再填入；按鈕使用 `click()`；原生 `<select>` 使用 `select_option()`：

```python
page.get_by_label("出發站").select_option(label="彰化")
page.get_by_label("抵達站").select_option(label="嘉義")
page.get_by_label("出發時間").select_option("08:00")
page.get_by_role("button", name="查詢", exact=True).click()
```

如果元件是自製下拉選單，它可能不是 `select`。先點擊 combobox，再等待可見的 `option` 或清單項目，選完後檢查顯示值。E15／E16 的 Google 書籍 ID 選單就是這種需要先辨識元件類型的案例。

## 6.2　等待一個狀態

點擊查詢後，等待結果標題、表格或「查無資料」訊息：

```python
page.get_by_role("button", name="查詢").click()
result = page.locator(".result-table")
empty = page.get_by_text("查無資料", exact=True)
expect(result.or_(empty)).to_be_visible()
```

更常見的寫法是先等待 URL 變化，再等待結果容器：

```python
page.wait_for_url("**/result**")
expect(page.locator(".result-table")).to_be_visible()
```

等待的目標要與下一步資料讀取直接相關。`wait_for_timeout(5000)` 只能暫時掩蓋問題，網路變慢時仍可能不足，網路變快時又浪費時間。

## 6.3　無資料不是失敗

查詢成功但時段沒有班次，與表單驗證失敗不同。先檢查 HTTP 和頁面錯誤，再判斷結果列數：

```python
from playwright.sync_api import expect

def classify_result(page):
    """回傳表單查詢的狀態；這是一個可嵌入既有流程的片段。"""
    if page.get_by_text("請選擇出發站").is_visible():
        raise ValueError("表單尚未完成")
    rows = page.locator(".result-table tbody tr")
    if rows.count() == 0:
        return {"status": "ok", "trains": []}
    return {"status": "ok", "trains": rows.all_inner_texts()}
```

`rows.count()` 是同步 API 的實際寫法；若網站使用分頁，應先切換或展開所有結果，再計算列數。選擇器需依該網站實際 HTML 調整。

報告中保留 `status`，讀者才知道程式真的查過，只是沒有符合條件的結果。交通與行情範例都遵守這個區分。

## 6.4　時間和日期的規格

把 `08:00` 當成字串顯示，把日期用 `datetime.date` 驗證。命令列輸入先檢查 `HH:MM` 格式，再確認它是官網提供的選項。台灣時間應使用 `zoneinfo.ZoneInfo("Asia/Taipei")` 產生「今天」，不要直接依執行主機時區判斷日期。

## 6.5　提交前的檢查

表單提交前把使用者可見的條件印出：

```python
print(f"查詢：{date} {start}–{end}，{origin} → {destination}")
```

這一行在回報問題時非常有用，也能防止複製上一個查詢的站點。E07 和 E08 會在結果中保存查詢條件，讓 CSV 或 JSON 不只是無法解釋的班次列表。

## 6.6　練習

1. 將臺鐵範例的時間改成 `09:00–10:00`，確認輸出檔名和查詢欄位一起改變。
2. 加入一個表單錯誤的明確例外，測試錯誤文字是否告訴讀者如何修正。
3. 將固定等待改成等待結果容器，並在結果容器出現前截一張錯誤畫面。

下一章會把這些等待和頁面狀態用在手機、平板與電腦版截圖，並保存可以重複查看的報告。

<!-- 編輯紀錄：初稿；搭配 E07、E08、E13。 -->
