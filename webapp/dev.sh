# 徹底解決 Node 版本問題與 PM2 隔離的啟動腳本

# 獲取專案根目錄，設定獨立的 PM2 家目錄
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
export PM2_HOME="$PROJECT_ROOT/.pm2"
mkdir -p "$PM2_HOME"

echo "Using isolated PM2_HOME: $PM2_HOME"

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# 如果有 .nvmrc 則使用它，否則強制使用 v24.14.0
if [ -f "$SCRIPT_DIR/.nvmrc" ]; then
    cd "$SCRIPT_DIR" && nvm use
else
    nvm use 24.14.0
fi

# 執行 PM2 啟動
NODE_PATH="/home/xg/.nvm/versions/node/v25.8.1/bin"
export PATH="$NODE_PATH:$PATH"

cd "$SCRIPT_DIR"

# 檢查是否已在 PM2 中，如果在則更新/重啟，否則啟動新行程
echo "Deploying/Restarting all services in ecosystem.config.js..."
pm2 start ecosystem.config.js --update-env

pm2 save
echo "PM2 management active for tradeview-strategy-monitor"

