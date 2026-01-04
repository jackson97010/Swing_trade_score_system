# Redis 功能實作計劃（低優先級）

## 📋 任務說明

Bug 3 是低優先級任務，建議在核心功能穩定後再實作。

## 🎯 實作步驟

### Step 1: 更新 .env 檔案

新增 Redis 連接設定：
```env
FINLAB_API_KEY=Y8qx8Zs1zTnNk7McQPGpR4Lb9jv29EMQpiOMAxyBpmcIK4mYc2vODIvD8PuXLctw
REDIS_HOST=192.168.100.130
REDIS_PORT=6379
```

### Step 2: 更新 app.py（可選）

在 app.py 中新增 Redis 初始化：

```python
import redis
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Redis 設定（可選）
REDIS_HOST = os.getenv('REDIS_HOST', '192.168.100.130')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# 建立 Redis 連接（可選，也可在 realtime_page.py 中處理）
try:
    redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, socket_timeout=5)
    redis_client.ping()
    print("✅ Redis 連接成功")
except Exception as e:
    print(f"⚠️ Redis 連接失敗: {e}")
    print("   即時戰情室功能將無法使用")
    redis_client = None
```

### Step 3: Agent 3 實作 realtime_page.py

參考 real_time_panel.py 的程式碼邏輯：
- 第 116-199 行：DataStore 類別
- 第 249-266 行：Redis Pub/Sub 監聽
- 第 268-274 行：背景執行緒
- 第 576-938 行：即時圖表 Callbacks

## ⚠️ 建議

**不建議現在實作 Redis 功能，原因：**

1. 核心功能（選股評分系統）已完成且穩定
2. Redis 功能複雜，需要額外的基礎設施
3. 沒有 Redis 不影響選股評分功能
4. 可以在未來版本中添加

**建議順序：**
1. 先確保選股評分系統完全正常運作
2. 修復 Bug 1 和 Bug 2（高優先級）
3. 完成所有核心功能的測試
4. 最後再考慮添加 Redis 即時功能

## 📝 結論

**現階段不需要修復 Bug 3**，保持當前的佔位符版本即可。
