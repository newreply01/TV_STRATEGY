# TradeView Strategy 專案管理手冊

本專案旨在將 TradingView 的優質策略轉換為 Python 實作，並提供網頁化管理介面與數據盤點功能。

## 🚀 快速啟動提示詞 (下次對話用)
> 「我們正在進行 TradeView Strategy 專案。目前已完成『管理中心 (Management Center)』的重新命名與佈局優化。請讀取 `/webapp/src/app/monitor/MonitorPageClient.tsx` 與 `/webapp/src/app/api/monitor/route.ts` 以了解最新的數據分流邏輯（開發進度 vs 系統監控）。

## 🛠️ 目前專案狀態
- **管理中心**: 已區分為「開發進度」與「系統管理」兩大區塊。
- **數據分類**: 
  - `TradingView_Scripts`: 屬於系統基礎數據，已移至系統監控分頁。
  - `Strategy_001` ~ `Strategy_004`: 屬於具體開發進度。
- **超連結功能**: 開發進度清單已整合「**系統內部跳轉連結**」，點擊「**進入開發頁面**」即可直接抵達對應的策略實作頁（如 `/scripts/004`）。
- **當前復刻進度**:
  - `001`: Omni-Flow Consensus (已有頁面預定)
  - `002`: Supertrend Multi-Timeframe (MTF) - [NEW]
  - `003`: Market Structure Dashboard (Flux Charts) - [EXISTING]
  - `004`: Swing Profile [BigBeluga] - [NEW]
- **技術棧**: Next.js 14 (App Router), Prisma, PostgreSQL, Tailwind CSS.

## 📝 自動化開發與狀態同步流程 (必讀)
為確保 **「管理中心」** 的開發進度清單與庫存收容池保持一致，請在挑選新策略與開發過程中嚴格遵守以下自動化派發與雙開關確認流程：

1. **從收容池排入開發**：
   - 系統初始收容的策略皆存於「待開發收容池」內，尚未配發開發專屬序號 (`serial_id`)。
   - 請直接在管理中心的「待開發收容池 (按讚數排名)」列表內，點選目標策略後方的 **`+ 排入開發`** 按鈕。
   - 點擊後，系統的 Promote API 將自動產生下一個流水號（例如自動給予 `s005`），並將該策略即時移入下方的「開發進度清單」主表中，正式成為開發專案。
2. **開發中與復刻完成**：
   - 當系統自動化代碼轉換或初步 UI 實作完成時，系統應自動將該記錄的 `is_implemented` 設為 `true`。
   - 此時管理中心的狀態欄會在此策略亮起**綠色的「已復刻」開關**，代表該策略已進入可測試階段。
3. **人工驗收與最終完成**：
   - 當您親自確認該策略的功能、畫面與數據皆符合預期，可正式對外發布時，**請在管理中心的狀態欄直接點擊下方藍色的「未確認 / 已完成」開關**。
   - 點擊後將會同步將資料表中的 `is_web_done` 屬性標記為 `true`，代表該策略的所有開發生命週期已透過人工驗收真正結束。

## 🏗️ 架構說明：`strategies/` vs `webapp/api/py/`

本專案包含兩個存放 Python 策略邏輯的目錄，其用途與修改規則如下：

### 1. `strategies/` 目錄 (主要開發區)
- **用途**：這是目前本地系統正在運行的「實時」邏輯所在地。
- **運行機制**：PM2 服務 `tradeview-chart-engine` 直接執行此目錄下的 `chart_engine.py` (監聽 Port 26001)。
- **修改規則**：**後續開發與功能調整，應以此目錄為主。** 修改後需重啟 PM2 服務 (`pm2 restart tradeview-chart-engine`) 才能生效。

### 2. `webapp/api/py/` 目錄 (Vercel 部署區)
- **用途**：這是 Next.js 框架內部的 Python API 目錄，專為 Vercel Serverless Functions 部署而設計。
- **運行機制**：當專案部署至 Vercel 時，雲端環境會執行此處的腳本。
- **修改規則**：**除非因為 Vercel 部署發生錯誤或有特定雲端需求，否則不宜隨意修改此目錄。** 若在此處進行了修正，建議同步檢查 `strategies/` 是否也需要對應更新。

---

## 📁 重要路徑與端口
- **前端頁面 (Next.js)**: [http://localhost:26000](http://localhost:26000)
- **圖表引擎 (Flask)**: [http://localhost:26001](http://localhost:26001)
- **資料庫 (Postgres)**: `localhost:5533`
- **前端原始碼**: `webapp/src/app/monitor/MonitorPageClient.tsx`
- **主要運行引擎**: `strategies/chart_engine.py` (由 PM2 管理)
- **Prisma Schema**: `webapp/prisma/schema.prisma`

---

## 🚀 進程管理 (PM2 獨立隔離)

本專案採用 **獨立的 PM2 執行環境** (`PM2_HOME`)，以確保不會與 `Stock Screener` 等其他專案的進程混淆。

### 1. 啟動服務
請使用專屬腳本啟動，它會自動處理 Node 版本與環境隔離：
```bash
./webapp/dev.sh
```

### 2. 查看進程狀況
由於環境隔離，直接執行 `pm2 list` 將看不到本專案進程。請使用以下方式查看：
```bash
# 進入 webapp 目錄使用其環境變數
cd webapp
export PM2_HOME=$(pwd)/../.pm2
pm2 list
pm2 logs tradeview-chart-engine
```

### 3. 進程資訊
- **進程名稱**: `tradeview-chart-engine` (Python Flask 服務)
- **進程名稱**: `tradeview-strategy-monitor` (Next.js 服務)
- **環境目錄**: `project_root/.pm2`

---

> [!TIP]
> 為了避免版本衝突，各專案皆配有 `./dev.sh` 啟動腳本，會自動切換至正確的 Node 版本並套用隔離環境。

---
*最後更新時間: 2026-03-25 (新增策略目錄架構說明與 X 軸緩衝優化)*
