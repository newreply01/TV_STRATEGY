# TradingView 腳本重疊分析計畫

本計畫旨在分析 TradingView "編輯精選" (Editor's Picks) 中的腳本是否頻繁出現在 "熱門" (Scripts) 列表中，以協助了解編輯點評與市場趨勢的相關度。

## 預計異動

計畫不涉及對現有代碼的修改，而是執行一系列資料收集與分析步驟：

### 1. 資料收集
- **收集地點 A (熱門)**：[https://tw.tradingview.com/scripts/](https://tw.tradingview.com/scripts/)
- **收集地點 B (編輯精選)**：[https://tw.tradingview.com/scripts/editors-picks/](https://tw.tradingview.com/scripts/editors-picks/)
- **抓取欄位**：
    - 腳本標題 (Name)
    - 腳本連結 (URL/Slug)
    - 作者名稱 (Author)

### 2. 資料分析
- **比對機制**：使用 URL Slug 作為唯一識別碼 (Unique ID)。
- **計算指標**：
    - 編輯精選當前有多少腳本也在熱門列表前 50 名？
    - 重疊百分比分析。

## 驗證與報告
- 產出 `walkthrough.md` 分析報告。
- 視覺化展示重疊程度 (如有需要)。
