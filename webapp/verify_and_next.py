import requests
import json

try:
    response = requests.get('http://localhost:26000/api/monitor')
    data = response.json()
    
    if not data.get('success'):
        print(f"API Error: {data.get('error')} - {data.get('details')}")
        exit(1)
        
    sync_progress = data.get('sync_progress', [])
    
    # 1. 驗證 #002
    s002 = next((item for item in sync_progress if item.get('serialId') == '002'), None)
    if s002:
        print(f"S002 verified: {s002['dataset']}")
        print(f"S002 Target URL: {s002['target_url']}")
        print(f"S002 External URL: {s002['external_url']}")
        print(f"S002 Web Done: {s002.get('isWebDone')}")
    else:
        print("S002 not found in sync_progress!")
        
    # 2. 識別 #003 (下一個待開發項，且不是 System 分類)
    pending = [item for item in sync_progress if not item.get('is_implemented') and item.get('category') != 'System']
    pending_sorted = sorted(pending, key=lambda x: x.get('likesCount', 0), reverse=True)
    
    if pending_sorted:
        next_strategy = pending_sorted[0]
        print(f"NEXT STRATEGY IDENTIFIED: {next_strategy['dataset']} (Boosts: {next_strategy['likesCount']})")
        print(f"ID: {next_strategy['id']}")
        # 提取 serialId 以命名為 #003
    else:
        print("No pending strategies found.")

except Exception as e:
    print(f"Verification Script Error: {e}")
