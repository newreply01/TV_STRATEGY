# TradeView Strategy 專案管理手冊

本專案旨在將 TradingView 的優質策略轉換為 Python 實作，並提供網頁化管理介面與數據盤點功能。

## 🚀 快速啟動提示詞 (下次對話用)
> 「我們正在進行 TradeView Strategy 專案。目前已完成『管理中心 (Management Center)』的重新命名與佈局優化。請讀取 `/webapp/src/app/monitor/MonitorPageClient.tsx` 與 `/webapp/src/app/api/monitor/route.ts` 以了解最新的數據分流邏輯（文章開發進度 vs 系統監控）。

## 🛠️ 目前專案狀態
- **管理中心**: 已區分為「文章開發進度」與「系統管理」兩大區塊。
- **數據分類**: 
  - `TradingView_Scripts`: 屬於系統基礎數據，已移至系統監控分頁。
  - `Strategy_001` ~ `Strategy_004`: 屬於具體文章開發進度。
- **超連結功能**: 開發進度清單已整合「**系統內部跳轉連結**」，點擊「**進入開發頁面**」即可直接抵達對應的策略實作頁（如 `/scripts/004`）。
- **當前復刻進度**:
  - `001`: Omni-Flow Consensus (已有頁面預定)
  - `002`: Supertrend Multi-Timeframe (MTF) - [NEW]
  - `003`: Market Structure Dashboard (Flux Charts) - [EXISTING]
  - `004`: Swing Profile [BigBeluga] - [NEW]
- **技術棧**: Next.js 14 (App Router), Prisma, PostgreSQL, Tailwind CSS.

## 📝 自動化開發與狀態同步流程 (必讀)
為確保 **「管理中心」** 的文章開發進度清單與庫存收容池保持一致，請在挑選新策略與開發過程中嚴格遵守以下自動化派發與雙開關確認流程：

1. **從收容池排入開發**：
   - 系統初始收容的策略皆存於「待開發收容池」內，尚未配發開發專屬序號 (`serial_id`)。
   - 請直接在管理中心的「待開發收容池 (按讚數排名)」列表內，點選目標策略後方的 **`+ 排入開發`** 按鈕。
   - 點擊後，系統的 Promote API 將自動產生下一個流水號（例如自動給予 `s005`），並將該策略即時移入下方的「文章開發進度清單」主表中，正式成為開發專案。
2. **開發中與復刻完成**：
   - 當系統自動化代碼轉換或初步 UI 實作完成時，系統應自動將該記錄的 `is_implemented` 設為 `true`。
   - 此時管理中心的狀態欄會在此策略亮起**綠色的「已復刻」開關**，代表該策略已進入可測試階段。
3. **人工驗收與最終完成**：
   - 當您親自確認該策略的功能、畫面與數據皆符合預期，可正式對外發布時，**請在管理中心的狀態欄直接點擊下方藍色的「未確認 / 已完成」開關**。
   - 點擊後將會同步將資料表中的 `is_web_done` 屬性標記為 `true`，代表該策略的所有開發生命週期已透過人工驗收真正結束。

## 📁 重要路徑與端口
- **前端頁面 (Next.js)**: [http://localhost:26000](http://localhost:26000)
- **圖表引擎 (Flask)**: [http://localhost:26001](http://localhost:26001)
- **資料庫 (Postgres)**: `localhost:5533`
- **前端原始碼**: `webapp/src/app/monitor/MonitorPageClient.tsx`
- **監控 API**: `webapp/src/app/api/monitor/route.ts`
- **Prisma Schema**: `webapp/prisma/schema.prisma`
- **抓取腳本**: `strategies/sync_progress_from_supabase.py` (開發中)

## 🗂️ 跨專案資源參考 (開發必備)
| 專案 | 服務 Port | 資料庫 Port | 資料庫名稱 | Node 版本 |
| :--- | :--- | :--- | :--- | :--- |
| **Tradeview Strategy** | **26000** | **5533** | `tradeview_strategy` | v25.8.1 |
| **Stock Screener** | **31000** | **5433** | `stock_screener` | v25.8.1 |

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
pm2 logs tradeview-strategy-monitor
```

### 3. 進程資訊
- **進程名稱**: `tradeview-strategy-monitor`
- **運行端口**: `26000` (Next.js Dev Server)
- **環境目錄**: `project_root/.pm2`

---

> [!TIP]
> 為了避免版本衝突，各專案皆配有 `./dev.sh` 啟動腳本，會自動切換至正確的 Node 版本並套用隔離環境。

---
*最後更新時間: 2026-03-22 (資料庫 Port 切換完成 - 5533)*
