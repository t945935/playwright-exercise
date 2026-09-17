# 活動報名提醒（Python + Playwright）

監看指定活動頁的報名按鈕或狀態區塊；偵測到開放報名時，在終端機提醒、寫入提醒紀錄，並嘗試送出 Linux 桌面通知。沒有登入或自動報名功能。

需要先指定**實際活動網址**、**該頁唯一的報名按鈕 CSS 選取器**及**開放時的文字**。這些須依網站確認，不能直接套用下方示意值。程式尚未啟動持續監看。

```bash
python -m pip install playwright
python -m playwright install chromium
```

執行範例（請替換網址和選取器）：

```bash
python examples/04_tracking/event_registration_watch.py 'https://example.com/event' --selector '#register-button' --open-text '立即報名' --name '我的講座'
```

確認單次查詢正確後，加上 `--watch` 即每五分鐘查詢一次；`--interval 120` 可改成每兩分鐘；`--count 3` 可在監看三次後結束。`--headed` 顯示瀏覽器，Ctrl+C 結束監看。

## 實際活動範例（2026-09-17 查核）

[連結台灣專題講座：全資客志業的堅持 -以公務生涯為例](https://technologyandlife.kktix.cc/events/18-09-26?locale=zh-TW)，2026/09/18 10:10–11:45，免費線上 WebEx 講座。查核時活動頁顯示「下一步」報名入口，票券報名期限為 2026/09/18 11:45。狀態依網站當時回應為準；本範例偵測入口，不代表已完成報名或保證尚有名額。

```bash
.venv/bin/python examples/04_tracking/event_registration_watch.py 'https://technologyandlife.kktix.cc/events/18-09-26?locale=zh-TW' --selector '.tickets > .btn-point' --open-text '下一步' --name '連結台灣專題講座：資客志業的堅持'
```

此選取器使用票券區內的按鈕，避開頁面另一個手機版按鈕。活動結束後，按鈕若被移除會回報查詢失敗，需換成新的活動實例。首次開放提醒會保存；使用相同指令再次查詢，持續開放時不重複提醒。

預設關閉文字為尚未開放、尚未開始、額滿、已結束、截止及售完；可重複使用 `--closed-text` 自訂並取代預設列表。按鈕被停用也視為未開放。遇到未知文字、登入頁、選取器失效或連線失敗，不把它當成開放。

首次發現已開放會提醒；之後持續開放不會重複提醒。偵測到關閉後再次開放，會再提醒一次，可用於額滿後釋出名額的情況。這是依網站顯示狀態判斷，不保證購票流程中仍有名額。

`outputs/events/` 保存各組網址及條件的狀態 JSON，`alerts.jsonl` 保存提醒紀錄；下次執行沿用。不同條件使用不同狀態檔。同一組條件請只執行一個監看程序。

桌面通知使用環境已有的 `notify-send`；若未安裝、無桌面工作階段或 Windows/WSL 無法顯示，仍會提供終端機提醒和紀錄。程式不會安裝作業系統排程，電腦休眠或程式結束後不會繼續查詢。

所有相對程式路徑均從專案根目錄執行。預設輸出位置固定在專案的 `outputs/`；自訂 `--output-dir` 的相對路徑則以執行時的工作目錄為準。
