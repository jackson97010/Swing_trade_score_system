# Agent 任務指令 - 複製貼上版

## 使用說明

設置好 4 個 Claude CLI 終端後，**直接複製以下對應的指令貼到每個終端中**。

---

## 終端 1 - Agent 1 (Core Infrastructure)

### 工作目錄確認
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-core
```

### 給 Claude 的指令（複製貼上）

```
你是 Agent 1 - Core Infrastructure Agent。

你的身份：
- Agent ID: Agent 1
- 負責模組: 核心架構 (Core Infrastructure)
- 分支: feature/core-infrastructure
- 工作目錄: C:\Users\User\Documents\_05_看盤波段\worktree-core

你的任務：
請參考 AGENT_1_CORE.md 文件，完成以下開發任務：
1. 建立 app.py (Dash 應用主程式)
2. 建立 .env (環境變數設定)
3. 建立 modules/__init__.py (模組初始化)
4. 建立 layouts/__init__.py (佈局初始化)
5. 建立 .gitignore

重要提醒：
- 你不依賴其他 Agent，可以獨立開發
- 完成後進行基礎測試（執行 python app.py）
- 其他 Agent 會依賴你建立的初始化檔案
- 完成後提交 commit：[Agent-1] Core: 建立 Dash 應用基礎架構

現在請開始執行任務。
```

---

## 終端 2 - Agent 2 (Data & Scoring)

### 工作目錄確認
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-data
```

### 給 Claude 的指令（複製貼上）

```
你是 Agent 2 - Data & Scoring Agent。

你的身份：
- Agent ID: Agent 2
- 負責模組: 資料取得與評分引擎
- 分支: feature/data-scoring
- 工作目錄: C:\Users\User\Documents\_05_看盤波段\worktree-data

你的任務：
請參考 AGENT_2_DATA.md 文件，完成以下開發任務：
1. 建立 modules/data_fetcher.py (Finlab 資料取得與技術指標計算)
2. 建立 modules/scoring.py (評分邏輯引擎)
3. 實作以下功能：
   - 取得股票價格、成交量、營收、EPS
   - 計算 MA10/MA20/MA60、MACD
   - 計算產業趨勢
   - 評分邏輯 (技術面 40分 + 基本面 30分)

重要提醒：
- 你不依賴其他 Agent，可以獨立開發與測試
- 使用 Finlab API Key: Y8qx8Zs1zTnNk7McQPGpR4Lb9jv29EMQpiOMAxyBpmcIK4mYc2vODIvD8PuXLctw
- 完成後建立 test_data_scoring.py 進行單元測試
- 完成後提交 commit：[Agent-2] Data & Scoring: 實作資料取得與評分引擎

現在請開始執行任務。
```

---

## 終端 3 - Agent 3 (UI Layouts)

### 工作目錄確認
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-ui
```

### 給 Claude 的指令（複製貼上）

```
你是 Agent 3 - UI Layouts Agent。

你的身份：
- Agent ID: Agent 3
- 負責模組: 使用者介面佈局
- 分支: feature/ui-layouts
- 工作目錄: C:\Users\User\Documents\_05_看盤波段\worktree-ui

你的任務：
請參考 AGENT_3_UI.md 文件，完成以下開發任務：
1. 建立 layouts/sidebar.py (側邊導航欄)
2. 建立 layouts/selection_page.py (選股評分頁面 - 主要功能)
3. 建立 layouts/realtime_page.py (即時戰情室頁面 - 可簡化為佔位符)
4. 實作 Dash Callbacks 處理使用者互動

重要提醒：
- 你依賴 Agent 2 (資料模組) 和 Agent 4 (圖表模組)
- 開發時先使用模擬資料，保留註解的 import
- 等 Agent 2 和 Agent 4 完成後再取消註解整合
- 參考 sample.png 設計 UI 佈局
- 完成後提交 commit：[Agent-3] UI Layouts: 實作所有頁面佈局元件

現在請開始執行任務。
```

---

## 終端 4 - Agent 4 (Charts)

### 工作目錄確認
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-charts
```

### 給 Claude 的指令（複製貼上）

```
你是 Agent 4 - Charts Agent。

你的身份：
- Agent ID: Agent 4
- 負責模組: 圖表視覺化
- 分支: feature/charts
- 工作目錄: C:\Users\User\Documents\_05_看盤波段\worktree-charts

你的任務：
請參考 AGENT_4_CHARTS.md 文件，完成以下開發任務：
1. 建立 modules/charts.py (Plotly 圖表繪製模組)
2. 實作以下圖表功能：
   - K線圖 (含均線 MA10/MA20/MA60)
   - MACD 指標圖
   - 成交量柱狀圖
   - 評分分布圖
   - 簡易折線圖

重要提醒：
- 你依賴 Agent 2 (資料模組)
- 開發時先使用模擬資料測試圖表
- 使用 Plotly 建立互動式圖表
- 完成後建立 test_charts.py 進行測試
- 完成後提交 commit：[Agent-4] Charts: 實作圖表視覺化模組

現在請開始執行任務。
```

---

## 驗證每個 Agent 的工作目錄

在給指令前，先在每個終端執行以下命令確認：

```bash
# 查看當前分支
git branch

# 查看當前目錄
pwd  # Linux/Mac
cd   # Windows

# 確認 conda 環境
conda info --envs
```

**預期結果**:
- 終端 1: 分支應為 `feature/core-infrastructure`
- 終端 2: 分支應為 `feature/data-scoring`
- 終端 3: 分支應為 `feature/ui-layouts`
- 終端 4: 分支應為 `feature/charts`

---

## 監控進度

在主專案目錄（不是 worktree）執行：

```bash
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system

# 查看所有分支的最新提交
git log --all --oneline --graph --decorate -20

# 查看各 worktree 狀態
git worktree list
```

---

## 整合時機

當所有 Agent 都完成後：

1. 在主專案目錄執行合併：
```bash
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system
git checkout main
git merge feature/core-infrastructure
git merge feature/data-scoring
git merge feature/ui-layouts
git merge feature/charts
```

2. 執行整合測試：
```bash
python app.py
```

3. 建立 PR

---

## 快速複製區（精簡版）

如果你想要更簡潔的指令：

### Agent 1
```
你是 Agent 1 - Core Infrastructure。參考 AGENT_1_CORE.md 完成 app.py、.env、__init__.py 等核心架構。你不依賴其他 Agent，可以獨立開發。
```

### Agent 2
```
你是 Agent 2 - Data & Scoring。參考 AGENT_2_DATA.md 完成 data_fetcher.py 和 scoring.py，實作資料取得與評分邏輯。你不依賴其他 Agent，可以獨立開發。
```

### Agent 3
```
你是 Agent 3 - UI Layouts。參考 AGENT_3_UI.md 完成 sidebar.py、selection_page.py 等 UI 元件。你依賴 Agent 2 和 Agent 4，開發時先用模擬資料。
```

### Agent 4
```
你是 Agent 4 - Charts。參考 AGENT_4_CHARTS.md 完成 charts.py，實作 K線圖、MACD、成交量等圖表。你依賴 Agent 2，開發時先用模擬資料。
```

---

**建議**: 使用完整版指令，讓 Agent 有更清楚的上下文。
