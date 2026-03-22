import requests
import json
import time

def check_link(url, name):
    try:
        # 使用 requests 模擬 curl -I
        response = requests.head(url, timeout=10, allow_redirects=True)
        status = response.status_code
        print(f"VERIFY {name}: {url} -> Status {status}")
        return status == 200
    except Exception as e:
        print(f"VERIFY {name}: {url} -> FAILED: {e}")
        return False

# 等待 Next.js 啟動
time.sleep(15)

# 1. 驗證 Monitor API
api_url = 'http://localhost:26000/api/monitor'
try:
    res = requests.get(api_url)
    data = res.json()
    if data.get('success'):
        print("SUCCESS: Monitor API is UP and returns data.")
        # 檢查 S002
        sync = data.get('sync_progress', [])
        s002 = next((i for i in sync if i.get('serialId') == '002'), None)
        if s002:
            print(f"S002 Title: {s002['dataset']}")
            # 2. 驗證內部開發連結
            dev_url = f"http://localhost:26000{s002['target_url']}"
            check_link(dev_url, "S002 Internal Dev Page")
            
            # 3. 驗證外部來源連結
            check_link(s002['external_url'], "S002 External Source")
        else:
            print("ERROR: S002 not found in API!")
    else:
        print(f"ERROR: API returned failure: {data.get('error')}")
except Exception as e:
    print(f"ERROR: Failed to connect to Monitor API: {e}")

# Identify #003
# (同之前邏輯)
