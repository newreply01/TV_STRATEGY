This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:26000](http://localhost:26000) with your browser to see the result.

You can start editing the page by modifying `app/page.tsx`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Development Workflow: Strategy Replication

為了系統性地復刻 TradingView 上的優質策略，我們建立了以下自動化開發工作流：

### 1. 識別開發目標 (Management Center)
進入 [管理中心](/monitor)，查看「文章開發進度清單」。
- **優先順序**：根據 `Boosts (社區熱度)` 進行排序。
- **狀態檢查**：挑選狀態為「待開發」的項目。

### 2. 初始化開發環境
針對選定的策略（假設 Slug 為 `[SLUG]`）：
1. 在 `webapp/src/app/scripts/[SLUG]` 建立目錄。
2. 建立 `page.tsx` 使用 `TradingViewChart` 或自定義組件進行可視化。
3. 在管理中心勾選「網頁復刻」完成初始 UI 部署。

### 3. 持續性自動化 (Continuous Replication)
當前一個策略的網頁開發完成後，AI 助手將自動：
1. 將該策略在進度清單中標記為「已完成」(Web Done)。
2. 從「待開發收容池」點擊 `+ 排入開發` 取得下一個序號。
3. 自動初始化目錄結構與基礎代碼。
4. 執行「自動化驗證」確保連結與 API 正常。

## 驗證計劃 (Verification Plan)

為確保連結與 API 的準確性，每次復刻後需執行以下 `curl` 測試：

1. **監控 API 狀態**：
   ```bash
   curl -s http://localhost:26000/api/monitor | jq '.success'
   ```
2. **研發頁面可用性**：
   ```bash
   curl -I http://localhost:26000/scripts/[SLUG]
   ```
   *預期結果：HTTP/1.1 200 OK*
3. **外部來源連結正確性**：
   ```bash
   curl -L -I [SOURCE_URL]
   ```
   *預期結果：HTTP/1.1 200 OK (或跳轉至 TradingView)*

---

## 當前開發進度 (Current Development Progress)

| Serial | 策略名稱 | 狀態 | 連結 |
| :--- | :--- | :--- | :--- |
| 001 | Omni-Flow Consensus [LuxAlgo] | ✅ 已實作 | [Link](/scripts/001) |
| 002 | Supertrend Multi-Timeframe (MTF) | ✅ 已實作 | [Link](/scripts/002) |
| 003 | Market Structure Dashboard | ✅ 已實作 | [Link](/scripts/003) |
| 004 | Swing Profile [BigBeluga] | ✅ 已實作 | [Link](/scripts/004) |
| 005 | Smart Trader, Episode 03 | ✅ 已實作 | [Link](/scripts/005) |

---

## 快速啟動 (Session Quick-Start)
在新會話開始時，請使用以下指令：
> "請繼續前一個會話。根據收容池（Backlog）的排序，提取並使用 Promote API 將下一個熱門策略排入開發。接著建立動態路由組件，並在完成後切換其為『已復刻』與『已完成』狀態，最後更新文件。"

---
*上次更新日期：2026-03-22 (資料庫連接埠已修正為 5533)*
