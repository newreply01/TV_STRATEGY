import psycopg2
from psycopg2 import sql
import os

def run_automation():
    try:
        conn = psycopg2.connect(host='localhost', user='postgres', password='postgres123', dbname='tradeview_strategy', port='5433')
        cur = conn.cursor()
        
        # 1. Finalize S003 with safe identifier quoting
        query = sql.SQL('UPDATE tradingview_scripts SET is_implemented = %s, {web} = %s, {script} = %s WHERE serial_id = %s').format(
            web=sql.Identifier('isWebDone'),
            script=sql.Identifier('isScriptDone')
        )
        cur.execute(query, (True, True, True, '003'))
        print("SUCCESS: Strategy 003 marked as DONE.")
        
        # 2. Identify S004
        cur.execute("SELECT serial_id, title, slug, url, boosts_count FROM tradingview_scripts WHERE is_implemented = false ORDER BY boosts_count DESC LIMIT 1")
        row = cur.fetchone()
        
        if not row:
            print("NO_PENDING_STRATEGY")
            conn.commit()
            return

        serial_id = "004"
        title = row[1]
        slug = row[2]
        url = row[3]
        
        # 3. Update S004 serial_id
        cur.execute("UPDATE tradingview_scripts SET serial_id = %s WHERE slug = %s", (serial_id, slug))
        conn.commit()
        print(f"IDENTIFIED: {serial_id} - {title}")
        
        # 4. Initialize Folder
        target_dir = f"/home/xg/tradeview-strategy/webapp/src/app/scripts/{serial_id}"
        os.makedirs(target_dir, exist_ok=True)
        
        # 5. page.tsx
        page_content = f"""'use client';
import React from 'react';
import TradingViewChart from '@/components/TradingViewChart';

export default function Strategy{serial_id}Page() {{
  return (
    <div className="flex flex-col min-h-screen bg-slate-950 text-slate-100 p-6">
      <div className="max-w-7xl mx-auto w-full space-y-8">
        <div className="space-y-2">
          <div className="flex items-center space-x-3">
            <span className="px-3 py-1 text-xs font-bold uppercase tracking-wider bg-blue-600/20 text-blue-400 border border-blue-500/30 rounded-full">Strategy #{serial_id}</span>
            <h1 className="text-4xl font-extrabold tracking-tight text-white sm:text-5xl">{title}</h1>
          </div>
        </div>
        <div className="bg-slate-900/50 rounded-2xl border border-slate-800 p-1 overflow-hidden shadow-2xl backdrop-blur-sm">
          <div className="h-[700px] w-full bg-slate-950 rounded-xl overflow-hidden relative group">
            <TradingViewChart slug="{slug}" />
            <div className="absolute inset-0 flex items-center justify-center bg-slate-950/60 transition-opacity duration-300 pointer-events-none">
              <span className="px-6 py-2 bg-slate-900 border border-slate-700 rounded-full text-sm font-medium">數據串接中 (Automated Setup)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}}
"""
        with open(f"{target_dir}/page.tsx", "w") as f:
            f.write(page_content)
        print(f"INITIALIZED: {serial_id} development folder.")
        
        conn.close()
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    run_automation()
