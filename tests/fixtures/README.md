# 本機互動 fixture

活動提醒可用這個固定頁面離線練習。專案根目錄執行：

```bash
python3 -m http.server 8000 --directory tests/fixtures
```

另開終端機執行：

```bash
.venv/bin/python examples/04_tracking/event_registration_watch.py \
  http://127.0.0.1:8000/event.html --selector '#register-button' \
  --open-text '立即報名' --name '本機活動' --output-dir /tmp/event-demo
```

編輯 `event.html`，將按鈕文字改為「已額滿」即可測試關閉狀態。這個 fixture 不連線外部網站，也不會提交報名資料。
