# Bug 修復指令 - 如何分配給其他 CLI Agents

## 📋 Bug 概覽

目前有 3 個 bug 需要修復：

| Bug ID | 問題描述 | 負責 Agent | 優先級 |
|--------|----------|-----------|--------|
| Bug 1 | 股票名稱不會更新 | Agent 2 + Agent 3 | 🔴 高 |
| Bug 2 | 收盤價不會自動更新，需存儲到 data 資料夾 | Agent 2 | 🔴 高 |
| Bug 3 | Redis 功能尚未完成 | Agent 1 + Agent 3 | 🟢 低 |

---

## 🚀 如何使用 CLI 分配任務

### 方法 1: 直接指向更新後的任務文件

每個 Agent 的任務文件已經更新完成，直接讓 Agent 閱讀對應的文件即可：

#### 給 Agent 1 的指令
```bash
# 在 CLI 中執行（如果使用多個 agent 實例）
@docs/AGENT_1_CORE.md 請查看文件中的「⚠️ BUG 修復任務」章節，並完成 Bug 3 的修復任務
```

#### 給 Agent 2 的指令
```bash
@docs/AGENT_2_DATA.md 請查看文件中的「⚠️ BUG 修復任務」章節，並依序完成 Bug 1 和 Bug 2 的修復任務。Bug 1 優先處理。
```

#### 給 Agent 3 的指令
```bash
@docs/AGENT_3_UI.md 請查看文件中的「⚠️ BUG 修復任務」章節，並完成 Bug 1 的 UI 部分修復。等 Agent 2 完成後再處理。Bug 3 可以暫時跳過。
```

#### 給 Agent 4 的指令
```bash
@docs/AGENT_4_CHARTS.md 請查看文件中的「⚠️ BUG 修復任務」章節。目前沒有 bug 需要你處理，可以照常開發圖表模組。
```

---

### 方法 2: 詳細指令（逐步說明）

如果需要更明確的指令，可以使用以下方式：

#### 🔴 優先任務：Agent 2 修復 Bug 1 和 Bug 2

**給 Agent 2 的完整指令**:
```
請修復 modules/data_fetcher.py 中的兩個 bug：

Bug 1 - 股票名稱更新問題：
1. 在 fetch_stock_data() 函數中，將股票名稱取得邏輯改為使用 data.get('company_basic_info')
2. 參考文件：https://ai.finlab.tw/database
3. 保留 TWMarket 作為備用方案

Bug 2 - 資料存儲問題：
1. 建立 data 資料夾
2. 新增三個函數：save_stock_data(), load_stock_data(), fetch_and_save_stock_data()
3. 使用 pickle 格式存儲資料，檔名格式：stock_data_YYYYMMDD.pkl
4. 將新函數加入 __all__ 匯出清單

詳細說明請參考 @docs/AGENT_2_DATA.md 的「⚠️ BUG 修復任務」章節。
```

#### 🟡 次要任務：Agent 3 修復 Bug 1 的 UI 部分

**給 Agent 3 的完整指令**:
```
等 Agent 2 完成 Bug 1 和 Bug 2 的修復後，請修復 layouts/selection_page.py：

1. 取消註解第 130-144 行的程式碼（啟用真實資料）
2. 修改第 146-158 行，將硬編碼的股票名稱改為使用 stock_data['stock_names']
3. 確保所有數值都進行 round() 處理

Bug 3（Redis）可以暫時跳過，優先完成選股評分系統的核心功能。

詳細說明請參考 @docs/AGENT_3_UI.md 的「⚠️ BUG 修復任務」章節。
```

#### 🟢 低優先級：Agent 1 和 Agent 3 修復 Bug 3

**給 Agent 1 的指令（可選）**:
```
如果要在主程式中支援 Redis，請在 app.py 中：
1. 新增 Redis 連接設定（參考 AGENT_1_CORE.md）
2. 更新 .env 檔案，加入 REDIS_HOST 和 REDIS_PORT

但主要的 Redis 實作應該在 layouts/realtime_page.py 中由 Agent 3 處理。

詳細說明請參考 @docs/AGENT_1_CORE.md 的「⚠️ BUG 修復任務」章節。
```

**給 Agent 3 的指令（可選）**:
```
如果要實作完整的 Redis 即時戰情室功能：
1. 參考 real_time_panel.py 的 DataStore 類別（第 116-199 行）
2. 實作 Redis Pub/Sub 監聽機制（第 249-266 行）
3. 建立背景執行緒處理資料（第 268-274 行）
4. 實作即時圖表 Callbacks（第 576-938 行）

或者使用簡化版本（建議）：保留佔位符頁面，優先完成選股評分系統。

詳細說明請參考 @docs/AGENT_3_UI.md 的「⚠️ BUG 修復任務」章節。
```

---

## 📊 執行順序建議

### Phase 1: 核心功能修復（必須完成）
1. **Agent 2** 先處理 Bug 1 和 Bug 2
2. **Agent 3** 等 Agent 2 完成後，處理 Bug 1 的 UI 部分
3. **Agent 4** 同時可以開發圖表模組（不受影響）

### Phase 2: 整合測試
1. Agent 1 整合所有模組
2. 測試選股評分系統是否正常運作
3. 確認股票名稱正確顯示
4. 確認資料存儲功能正常

### Phase 3: Redis 功能（可選，低優先級）
1. Agent 1 新增 Redis 設定
2. Agent 3 實作即時戰情室功能
3. 整合測試 Redis 即時資料串流

---

## 🔍 驗證方式

### Bug 1 驗證
```bash
# 執行 app.py 後，在選股評分頁面輸入不同股票代碼
# 例如：2330, 2454, 2603
# 檢查表格中的「名稱」欄位是否正確顯示為「台積電」、「聯發科」、「聯詠」
```

### Bug 2 驗證
```bash
# 檢查專案根目錄是否出現 data 資料夾
# 檢查資料夾內是否有 stock_data_YYYYMMDD.pkl 檔案
# 第二次執行時應該看到「✅ 使用快取資料」訊息
```

### Bug 3 驗證（如果實作）
```bash
# 確認 Redis 連接成功（看到「✅ Redis 連接成功」訊息）
# 訪問 /realtime 頁面，檢查即時圖表是否正常顯示
```

---

## 💡 簡化版指令（最簡潔）

如果你只想要最簡單的指令：

### 給 Agent 2
```
@docs/AGENT_2_DATA.md 修復 Bug 1 和 Bug 2
```

### 給 Agent 3
```
@docs/AGENT_3_UI.md 等 Agent 2 完成後修復 Bug 1 的 UI 部分
```

### 給 Agent 4
```
@docs/AGENT_4_CHARTS.md 繼續開發圖表模組，無需等待
```

---

## 📝 注意事項

1. **依賴關係**：Agent 3 必須等待 Agent 2 完成 Bug 1 和 Bug 2 才能開始修復 UI 部分
2. **優先級**：Bug 3（Redis）可以暫時跳過，優先完成選股評分系統的核心功能
3. **測試**：每個 Agent 完成後應該自行測試功能是否正常
4. **Commit**：每個 bug 修復完成後應該建立一個 commit

---

## 🎯 快速開始

**最建議的執行方式**：

1. 先讓 **Agent 2** 閱讀 `docs/AGENT_2_DATA.md` 並修復 Bug 1 和 Bug 2
2. Agent 2 完成後，讓 **Agent 3** 閱讀 `docs/AGENT_3_UI.md` 並修復 Bug 1 的 UI 部分
3. 同時讓 **Agent 4** 閱讀 `docs/AGENT_4_CHARTS.md` 並繼續開發圖表模組
4. Bug 3（Redis）可以等核心功能完成後再處理

---

**文件版本**: v1.0
**建立日期**: 2026-01-04
**最後更新**: 2026-01-04
