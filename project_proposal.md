# TradeView Strategy 專案開發提案 (v4 微服務版)

本專案旨在打造「Premium 級別」的策略追蹤與分析平台，復刻 TradingView 社群腳本並結合 Python 精確回測。
**本次修訂採用現代化微服務架構：Next.js 全端展示層 + Python 獨立爬蟲與策略引擎。**

## 🎨 介面視覺提案 (UI/UX)

採用 **雙主題設計 (Dual-Theme)**，支持一鍵切換暗色/明亮模式。

---

## 🛠️ 技術架構 (微服務分離設計)

| 層級 | 技術 | 用途 |
|------|------|------|
| 展示與 API | **Next.js + Node.js + Prisma** | Premium 圖文排版、API 接口、資料庫讀取展示 |
| 爬蟲服務 | **Python (Playwright)** | 定期無頭瀏覽器抓取 TradingView 代碼、翻譯與同步 |
| 策略引擎 | **Python (Pandas/TA-Lib)** | 定時拉取 DB 數據進行指標計算、信號追蹤、回測 |
| 共享資料庫 | **PostgreSQL** | 本地開發端 (WSL) / 雲端生產端 (Supabase) |
| 部署方式 | **Vercel** (前端) + **Render/Railway** (Python 後台排程) | 完美契合各自特性的雲端部署 |

---

## 📄 頁面規劃

### 頁面 A：策略文章總覽 `/scripts`
- 卡片式圖文列表（含預覽圖、標題、作者、來源標籤）
- 篩選器：熱門 / 編輯精選 / 全部
- 每張卡片標註「來源」與「翻譯狀態」

### 頁面 B：文章詳情 `/scripts/[slug]`
- 頂部大圖 → 繁中描述 → Pine Script 代碼區塊
- **參考來源區**：明確標示原始 TradingView 連結、作者 Profile、授權資訊
- Python 實作狀態與回測結果（若已實作）

### 頁面 C：策略執行監控看板 `/monitor`
- 展示每個 Python 策略的執行記錄
- 欄位：執行時間、策略名稱、狀態 (✅/❌)、信號結果、錯誤日誌

### 頁面 D：系統追蹤總覽 `/tracker` (簡易取代原生 Admin)
- 利用 Next.js 打造簡易的內部管理頁面
- 所有腳本的生命週期管理看板
- 欄位：爬取狀態、翻譯進度、Python 實作進度、錯誤狀態、更新時間

---

## 📊 共享 PostgreSQL 資料庫結構

- **User / Admin**: (供後續擴充登入系統使用)
- **Script**: 存放 slug, title, descriptions, author, pine_code, is_translated, is_implemented 等腳本資訊。
- **Execution_Log**: 關聯 Script，存放 python 執行每一次的回測成功與否、log 紀錄、績效指標。

---

## 🚀 執行里程碑

| 階段 | 內容 | 驗證標準 |
|------|------|----------|
| M1 | Next.js 初始化 + Prisma Schema + Tailwind | 成功套用 DB Schema，建立基本專案結構 |
| M2 | Python Playwright 獨立爬蟲完成 | DB 成功寫入 ≥20 筆 TradingView 熱門/精選資料 |
| M3 | 前端：文章總覽 + 文章詳情頁 + Tracker 看板 | 可順利於 localhost:3000 瀏覽圖文與狀態 |
| M4 | Python 獨立策略引擎原型 | 第一個策略跑完回測並將 Log 寫回 DB |
| M5 | 整合：前端 Monitor 儀表板連接 Log | Monitor 頁面成功展示 Python 執行結果 |
| M6 | Vercel (Front) + Render/Railway (Python) | 專案雙軌上雲佈署完成 |

---

## 💡 架構優勢重點
- **速度極致化**：Next.js 直接透過 Prisma/Node.js 跟資料庫溝通，享有即時的資料渲染與極快的使用者體驗。
- **爬蟲不干擾運營**：Python 腳本完全獨立運行在背景，即使爬蟲出錯或卡住，也不會導致主網站當機。
- **最強雲端適配**：百分之百貼合同樣微服務架構的領先雲端提供商 (Vercel / Supabase)，部署過程幾乎零痛點。
