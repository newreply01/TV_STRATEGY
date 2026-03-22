module.exports = {
  apps: [
    {
      name: "tradeview-strategy-monitor",
      script: "npm",
      args: "run dev",
      env: {
        NODE_ENV: "development",
        PORT: 26000
      }
    },
    {
      name: "tradeview-chart-engine",
      script: "/home/xg/tradeview-strategy/strategies/venv/bin/python",
      args: "chart_engine.py",
      cwd: "/home/xg/tradeview-strategy/strategies",
      env: {
        PYTHONUNBUFFERED: "1"
      }
    }
  ]
};
