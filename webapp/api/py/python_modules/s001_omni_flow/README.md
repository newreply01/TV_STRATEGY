# Omni-Flow 專業策略圖表系統 交付手冊 (#001)

本目錄包含 Omni-Flow Consensus 策略的完整實作與維護資源。

## 📁 資料夾結構說明

### 1. [web/](./web/) (前端展示用程式)
- **功能**：存放目前 Web 介面（26001 埠）調用的「生產環境」核心演算邏輯。
- **入口**：\web/indicator.py
### 2. [backtest/](./backtest/) (回測研究層)
- **功能**：存放本地回測腳本。
- **工具**：已提供 \minimal_backtest.py\，可用於快速驗證邏輯與數據核對。

### 3. [v1_stable/](./v1_stable/) (首版開發備份)
- **功能**：存放開發完成後的首個穩定標竿版本。
- **備註**：當 web 版進行重大的實驗性修改前，建議參考此處進行比對。

---

## 🚀 核心成就 (V2 升級版)

- **序號系統**：已定址為 **#001**。
- **動態個股**：後端已支援從 UI 動態切換 AAPL, TSLA, NVDA 等標的。
- **物理分區**：圖表已實現價格與指標的雙窗格 (Dual Pane) 解析。

---

## 🛠️ 維護指南

### 重啟服務
若更新了 \web/indicator.py\，請重啟後端 API：
\\ash
pkill -9 python3
nohup ./venv/bin/python3 chart_engine.py > /tmp/api.log 2>&1 &
\
### 執行回測
\\ash
cd s001_omni_flow
python3 backtest/minimal_backtest.py
\
---
**專案狀態：已就緒。**
