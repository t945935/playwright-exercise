# 第 5 章　找到網頁元素：文字、角色與 CSS 定位

瀏覽器自動化的核心不是「點座標」，而是找到代表意義的元素。座標在視窗大小改變或版面改版後很容易失效；角色、文字與穩定的屬性則能表達你真正想操作的對象。

## 5.1　從可讀的定位器開始

如果頁面有「書籍列表」連結，優先使用角色和名稱：

```python
page.get_by_role("link", name="書籍列表", exact=True).click()
```

按鈕、標題、輸入框和連結通常都有可辨識角色。`exact=True` 可避免「書籍列表說明」等相似文字被誤選。這種寫法也能直接讀出程式意圖。

文字定位適合靜態標籤：`page.get_by_text("AI Agent", exact=True)`。如果文字會隨數字改變，使用正規表示式或先定位容器，再讀取容器文字。

## 5.2　CSS 與範圍定位

有時頁面沒有合適的角色名稱，需要使用 CSS：

```python
cards = page.locator("article.book-card")
first = cards.nth(0)
title = first.locator("h3").inner_text()
```

先取得所有書卡，再在每張卡片內找標題和連結，比直接在整頁找第一個 `h3` 安全。定位器可以串接，範圍越小，意外選到其他區塊的機會越低。

## 5.3　數量與迴圈

不要把網站目前顯示的 28 本寫死。若頁面有 `data-books-count`，先讀取摘要，再點擊「顯示更多書籍」直到顯示數等於總數：

```python
summary = page.locator("[data-books-count]")
cards = page.locator("article.book-card")
while True:
    shown, total = read_count(summary.inner_text())
    if shown == total:
        break
    page.get_by_role("button", name=re.compile("顯示更多書籍")).click()
    expect(cards.nth(shown)).to_be_attached()
```

點擊後等待新卡片附加到 DOM，而不是固定 `sleep(2)`。如果總數讀不到或卡片數最後不一致，應停止並保存錯誤資訊，不能把部分結果當完整清單。

## 5.4　選擇器的維護順序

優先順序可以是：可見的角色與名稱、標籤或 placeholder、穩定的 data attribute、元件內 CSS，最後才是很長的 XPath 或層層 `nth()`。定位器是程式和網站之間的契約；網站改版時，先更新契約的這一層。

用瀏覽器開發者工具檢查元素時，記下它的語意與附近結構，不要直接複製整條自動產生的 XPath。若只能用 class，確認 class 是元件名稱而不是隨機樣式名稱。

## 5.5　練習

1. 在 E05 找出首頁、書籍列表連結、AI Agent 按鈕和「更多資訊」連結各自的定位器。
2. 將書卡標題由 `inner_text()` 改成 `text_content()`，比較兩者對空白和隱藏文字的差異。
3. 故意把角色名稱改錯，觀察 Playwright 等待逾時訊息；再使用 `page.locator("body").inner_text()` 確認頁面是否真的有該文字。

完成條件是你能先說出要找的語意，再選擇定位器；並能在定位失敗時區分頁面未載入、文字改變和 CSS 結構改變。下一章把定位器接到輸入、選擇和等待。

<!-- 編輯紀錄：初稿；搭配 E05、E07、E08。 -->
