# 🚀 微服務並行混沌測試場

📌 **專案簡介**

本專案是一個用於驗證高併發情境下「斷路器」與「重試狀態機」協同運作的測試沙盒。
透過模擬不穩定的雲端服務與非同步並行攻擊，重現微服務架構中常見的 Race Condition（競爭狀態），並驗證系統的降級與自我保護機制。

---

## 🏗️ 核心架構與技術棧

本專案由三大組件構成：
1. **API 網關**：核心守門員。外層封裝斷路器，內層封裝具備 Full Jitter 的重試狀態機。
2. **外部服務模擬器**：模擬不穩定的雲端環境，隨時可以被手動關閉。
3. **並行攻擊腳本**：在同一毫秒送出 4 筆並行請求，在網關內部創造協程交織競爭的戰場。

### 技術棧
- **Python** 3.10+
- **FastAPI** (網頁框架)
- **httpx** (非同步 HTTP 客戶端)
- **aiobreaker** (原生支援 async 的斷路器套件)
- **asyncio** (並發控制)

---

## 📁 目錄結構

```text
concurrent-chaos-playground/
├── gateway/
│   ├── __init__.py
│   ├── breaker.py         # 斷路器初始化與監聽器設置
│   ├── retry.py           # 重試狀態機 (Full Jitter + 主動終止)
│   └── cloud_client.py    # 底層 httpx 網路呼叫
├── simulator/
│   └── main.py            # 外部服務模擬器 (Port 8001)
├── tests/
│   └── test_concurrent.py # 並行混沌攻擊腳本
├── main.py                # Gateway 入口 (Port 8000)
├── requirements.txt
└── README.txt

```

---

## 💻 環境安裝

1. 確認已安裝 **Python 3.10** 以上版本。
2. 建立虛擬環境 (可選但建議)。
3. 安裝依賴套件：

```bash
pip install -r requirements.txt

```

---

## 🎬 混沌測試操作指南

本測試需要開啟三個終端機 (Terminal) 來模擬分散式環境。

### 1. 啟動外部服務模擬器

在 **[終端機 1]** 執行：

```bash
python -m simulator.main

```

> 💡 確認服務跑在 `http://127.0.0.1:8001`

### 2. 啟動 API 網關

在 **[終端機 2]** 執行：

```bash
python main.py

```

> 💡 確認網關跑在 `http://127.0.0.1:8000`

### 3. 製造災難：關閉外部服務

回到 **[終端機 1]**，按下 `Ctrl + C` 關閉 simulator，模擬雲端服務突然掛掉。

### 4. 發動混沌攻擊

在 **[終端機 3]** 執行：

```bash
python -m tests.test_concurrent

```

> 💡 對網關同時發射 4 筆並行請求。

---

## 📜 預期日誌觀測 (黃金畫面)

當你執行攻擊腳本後，在 **[終端機 2]** (Gateway) 將會看到以下交織的並發日誌：
*(注意：由於 Full Jitter 演算法，退避秒數與協程甦醒順序每次執行都會不同)*

```text
🚪 [Gateway] API 網關啟動於 [http://127.0.0.1:8000](http://127.0.0.1:8000)
INFO:      Started server process [22444]
INFO:      Waiting for application startup.
INFO:      Application startup complete.
INFO:      Uvicorn running on [http://127.0.0.1:8000](http://127.0.0.1:8000) (Press CTRL+C to quit)
🔄 [Req 1] 正在執行第 1 次嘗試...
🔄 [Req 2] 正在執行第 1 次嘗試...
🔄 [Req 3] 正在執行第 1 次嘗試...
🔄 [Req 4] 正在執行第 1 次嘗試...
⚠️ [Req 1] 第 1 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 1] 進入退避，預計等待 0.48 秒...
⚠️ [Req 2] 第 1 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 2] 進入退避，預計等待 0.29 秒...
⚠️ [Req 3] 第 1 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 3] 進入退避，預計等待 0.22 秒...
⚠️ [Req 4] 第 1 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 4] 進入退避，預計等待 0.12 秒...
🔄 [Req 4] 正在執行第 2 次嘗試...
🔄 [Req 3] 正在執行第 2 次嘗試...
⚠️ [Req 4] 第 2 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 4] 進入退避，預計等待 0.48 秒...
🔄 [Req 2] 正在執行第 2 次嘗試...
⚠️ [Req 3] 第 2 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 3] 進入退避，預計等待 0.30 秒...
⚠️ [Req 2] 第 2 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 2] 進入退避，預計等待 0.02 秒...
🔄 [Req 2] 正在執行第 3 次嘗試...
🔄 [Req 1] 正在執行第 2 次嘗試...
⚠️ [Req 2] 第 3 次嘗試失敗 原因: ConnectTimeout
❌ [Req 2] 已達最大重試次數，宣告整筆請求失敗。
INFO:      127.0.0.1:6884 - "GET /api/v1/cloud-data?req_id=2 HTTP/1.1" 200 OK
⚠️ [Req 1] 第 2 次嘗試失敗 原因: ConnectTimeout
⏳ [Req 1] 進入退避，預計等待 0.71 秒...
🔄 [Req 3] 正在執行第 3 次嘗試...
🔄 [Req 4] 正在執行第 3 次嘗試...
⚠️ [Req 3] 第 3 次嘗試失敗 原因: ConnectTimeout
❌ [Req 3] 已達最大重試次數，宣告整筆請求失敗。
INFO:      127.0.0.1:6885 - "GET /api/v1/cloud-data?req_id=3 HTTP/1.1" 200 OK
⚠️ [Req 4] 第 3 次嘗試失敗 原因: ConnectTimeout
❌ [Req 4] 已達最大重試次數，宣告整筆請求失敗。

🚨 [🚨 SYSTEM ALERT] 斷路器狀態切換: CLOSED ➡ OPEN (Time: 12:46:54)
INFO:      127.0.0.1:6886 - "GET /api/v1/cloud-data?req_id=4 HTTP/1.1" 200 OK

(此時，睡了最久的 Req 1 剛好從 0.71 秒的退避中醒來...)
🛑 [Req 1] 睡醒後發現斷路器已變更為 OPEN！拒絕第 3 次嘗試，直接終止。
INFO:      127.0.0.1:6887 - "GET /api/v1/cloud-data?req_id=1 HTTP/1.1" 200 OK

```

---

## 🧠 核心設計解析

1. **斷路器計點邏輯**：
斷路器包裹在「整套重試狀態機」的外層。因此，即使內部重試了 3 次，只要最終失敗外拋，斷路器只算 **「1 次」** 失敗。這避免了重試機制加速斷路器熔斷的副作用。
2. **Full Jitter (AWS 標準演算法)**：
退避時間採用 `random.uniform(0, base_delay * (2  attempt))`，避免了多個協程在同一時間點同時醒來引發「驚群效應」，也造就了每次執行都不一樣的協程交織順序。
3. **主動終止機制**：
在協程睡覺（退避）的前後，都會檢查斷路器狀態。一旦發現狀態變為 **`OPEN`**，協程會立刻自我了斷，不再浪費網路資源進行無意義的重試（如最後的 `Req 1`）。

---

## 📄 License

Copyright © 2026 hanwu910514.

詳情請參閱 [Apache License 2.0](LICENSE) 檔案。

```