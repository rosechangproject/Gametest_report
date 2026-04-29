## 遊戲自動化測試監控與回測工具組 (Game QA Monitoring & Analysis Suite)

本專案是一個整合性的自動化測試解決方案，專為遊戲開發中的數據監控與數值回測需求而設計。透過自動化流程替代人工查核，實現從 API 抓取、風險分析到多平台報表同步的完整閉環。

### 🚀 專案核心亮點

* **自動化資料流水線 (Data Pipeline)**：從即時 API 抓取資料，經由邏輯層清洗與分析，最終同步至雲端與本地端。
* **專業風險判定邏輯**：針對遊戲「追殺局」設計異常偵測機制，自動標示勝率異常（>5%）與樣本數不足之風險。
* **工程化架構重構**：全案經過架構解耦（Decoupling），實現「單一事實來源（Single Source of Truth）」，提升系統維護性與可擴充性。
* **多維度視覺化產出**：支援響應式 HTML 儀表板、PDF 報告下載以及 Google Sheets 雲端即時同步。

### 📂 專案模組說明

#### 題目一：遊戲追殺局風險監控與雲端同步
這是一個高度自動化的監控模組，確保營運數據符合預期邏輯。
* **技術實現**：
    * 使用 `Requests` 進行多來源 API 資料抓取。
    * 核心運算模組 (`data_analyzer.py`) 處理複雜的業務邏輯與資料翻譯。
    * 整合 `Google Sheets API` 實作自動化雲端資料更新。
* **特色**：具備強韌的路徑處理機制，支援在任何執行目錄下穩定運行。

#### 題目二：遊戲數值回測監控 Dashboard
針對遊戲回測數據進行長期監控與比對。
* **技術實現**：
    * 結構化報表呈現，提供清晰的導覽介面。
    * 整合 Allure 或自定義 HTML 報表，確保測試結果具備可追蹤性。

### 🏗️ 系統架構與技術細節

本專案遵循軟體工程最佳實踐進行開發：

```text
Gametest_report/
├── index.html               # 專案入口 (作品集主頁)
├── scripts/                 # 核心邏輯層
│   ├── config.py            # 中央設定管理 (一鍵控管標題、路徑與門檻值)
│   ├── data_analyzer.py     # 資料處理大腦 (運算、過濾、排序與翻譯)
│   ├── report_gen.py        # 報表生成模組 (HTML 渲染與 PDF 整合)
│   ├── cloud_sync.py        # 雲端同步模組 (Google API 對接)
│   └── main.py              # 執行指揮官 (帶有專業 Logging 系統)
├── reports/                 # 自動生成之報表存放區
└── service_account.json     # 安全性憑證 (不進入版本控管)

技術棧 (Tech Stack)
Language: Python 3.x

Libraries: Pandas, Requests, Google API Python Client, Jinja2

DevOps: Git (Conventional Commits), Logging (系統日誌紀錄)

Frontend: HTML5, CSS3 (Responsive Design)

🛠️ 快速開始
#### 1. 安裝必要環境
```bash
pip install pandas requests google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

#### 2. 設定憑證
將 Google Service Account 憑證放入 scripts/ 並更名為 service_account.json。

#### 3. 執行分析
```bash
python scripts/main.py
```

📈 優化歷程 (Engineering Mindset)

作為 QA 工程師，我對程式碼品質有著與產品品質相同的堅持。本專案經歷了從「功能實作」到「系統重構」的演進：

路徑強韌化：導入動態絕對路徑處理，徹底解決環境變遷導致的執行錯誤。

邏輯去重 (DRY)：將分散的運算邏輯收斂至中央模組，確保 HTML、PDF 與雲端數據的 100% 一致性。

在地化與標準化：全案採用台灣開發術語（如：資料、佈署、變數），並遵循 PEP 8 命名規範。

Maintainer: CHANG YENJU (張雁茹)