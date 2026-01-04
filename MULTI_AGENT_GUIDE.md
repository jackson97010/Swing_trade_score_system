# Multi-Agent 開發指南 - 選股評分系統

## 概述

本指南說明如何使用 Git Worktree + Multi-Agent 策略來並行開發選股評分系統。我們將專案拆分為 4 個獨立模組，每個模組由一個 Agent 負責開發。

---

## 為什麼需要多個 Claude CLI？

**答案：是的，你需要開啟 4 個 Claude CLI 終端。**

### 多 CLI 的優勢
1. **並行開發**：4 個 Agent 可同時開發不同模組，大幅縮短開發時間
2. **模組隔離**：每個 Agent 專注於自己的模組，減少衝突
3. **獨立測試**：各模組可獨立測試後再整合
4. **清晰分工**：每個 Agent 有明確的任務範圍

---

## Agent 分工架構

```
主分支 (main)
    │
    ├─ feature/core-infrastructure  → Agent 1 (核心架構)
    ├─ feature/data-scoring         → Agent 2 (資料與評分)
    ├─ feature/ui-layouts           → Agent 3 (UI 佈局)
    └─ feature/charts               → Agent 4 (圖表模組)
```

### Agent 1 - Core Infrastructure (核心架構)
**分支**: `feature/core-infrastructure`
**Worktree 路徑**: `../worktree-core`
**負責模組**:
- `app.py` - 主程式入口與應用設定
- `modules/__init__.py` - 模組初始化
- `layouts/__init__.py` - UI 佈局初始化
- `.env` 環境變數設定

**任務文件**: `AGENT_1_CORE.md`

---

### Agent 2 - Data & Scoring (資料與評分引擎)
**分支**: `feature/data-scoring`
**Worktree 路徑**: `../worktree-data`
**負責模組**:
- `modules/data_fetcher.py` - Finlab 資料取得邏輯
- `modules/scoring.py` - 評分計算引擎

**任務文件**: `AGENT_2_DATA.md`

---

### Agent 3 - UI Layouts (使用者介面)
**分支**: `feature/ui-layouts`
**Worktree 路徑**: `../worktree-ui`
**負責模組**:
- `layouts/sidebar.py` - 側邊導航欄
- `layouts/selection_page.py` - 選股評分頁面
- `layouts/realtime_page.py` - 即時戰情室頁面

**任務文件**: `AGENT_3_UI.md`

---

### Agent 4 - Charts (圖表視覺化)
**分支**: `feature/charts`
**Worktree 路徑**: `../worktree-charts`
**負責模組**:
- `modules/charts.py` - Plotly 圖表繪製模組

**任務文件**: `AGENT_4_CHARTS.md`

---

## 開始前的準備工作

### Step 1: 建立 Git Worktree 環境

在**主終端**執行以下命令（只需執行一次）：

```bash
# 確認當前在主專案目錄
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system

# 建立 4 個 worktree 工作區
git worktree add ../worktree-core feature/core-infrastructure
git worktree add ../worktree-data feature/data-scoring
git worktree add ../worktree-ui feature/ui-layouts
git worktree add ../worktree-charts feature/charts

# 查看 worktree 列表
git worktree list
```

**預期輸出**:
```
C:/Users/User/Documents/_05_看盤波段/Swing_trade_score_system       377daae [main]
C:/Users/User/Documents/_05_看盤波段/worktree-core                  xxxxx [feature/core-infrastructure]
C:/Users/User/Documents/_05_看盤波段/worktree-data                  xxxxx [feature/data-scoring]
C:/Users/User/Documents/_05_看盤波段/worktree-ui                    xxxxx [feature/ui-layouts]
C:/Users/User/Documents/_05_看盤波段/worktree-charts                xxxxx [feature/charts]
```

---

### Step 2: 開啟 4 個 Claude CLI 終端

在 4 個不同的終端視窗中執行：

**終端 1 - Agent 1 (Core)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-core
conda activate my_project
# 然後啟動 Claude CLI
```

**終端 2 - Agent 2 (Data)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-data
conda activate my_project
# 然後啟動 Claude CLI
```

**終端 3 - Agent 3 (UI)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-ui
conda activate my_project
# 然後啟動 Claude CLI
```

**終端 4 - Agent 4 (Charts)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-charts
conda activate my_project
# 然後啟動 Claude CLI
```

---

### Step 3: 為每個 Agent 分配任務

在每個 Claude CLI 中，輸入對應的任務指令：

**Agent 1**: `參考 AGENT_1_CORE.md 完成核心架構開發`
**Agent 2**: `參考 AGENT_2_DATA.md 完成資料與評分模組`
**Agent 3**: `參考 AGENT_3_UI.md 完成 UI 佈局模組`
**Agent 4**: `參考 AGENT_4_CHARTS.md 完成圖表模組`

---

## 開發流程

### Phase 1: 並行開發 (Day 1-2)
1. 4 個 Agent 同時開發各自模組
2. 每個 Agent 完成後在各自分支提交 commit
3. 遇到依賴問題時，在對應的任務文件中記錄

### Phase 2: 整合測試 (Day 3)
1. Agent 1 負責整合所有模組
2. 依序合併分支：
   ```bash
   git checkout main
   git merge feature/core-infrastructure
   git merge feature/data-scoring
   git merge feature/ui-layouts
   git merge feature/charts
   ```
3. 解決衝突（如有）
4. 執行整合測試

### Phase 3: 建立 PR (Day 3)
1. 推送到遠端倉庫（如果有）
2. 建立 Pull Request
3. Code Review
4. 合併至 main

---

## 協作規範

### Git Commit 訊息格式
```
[Agent-N] 模組名稱: 簡短描述

詳細說明（可選）

Co-Authored-By: Claude <noreply@anthropic.com>
```

**範例**:
```
[Agent-1] Core: 建立 Dash 應用基礎架構

- 設定 app.py 主程式
- 配置 Finlab 登入
- 建立模組與佈局初始化檔案
```

### 分支命名規則
- `feature/core-infrastructure` - 核心架構
- `feature/data-scoring` - 資料評分
- `feature/ui-layouts` - UI 佈局
- `feature/charts` - 圖表模組

### 檔案所有權
| Agent | 檔案 | 禁止修改的檔案 |
|-------|------|----------------|
| Agent 1 | app.py, */\__init__.py | modules/*.py (除 __init__.py), layouts/*.py (除 __init__.py) |
| Agent 2 | modules/data_fetcher.py, modules/scoring.py | app.py, layouts/*, modules/charts.py |
| Agent 3 | layouts/*.py (除 __init__.py) | app.py, modules/* |
| Agent 4 | modules/charts.py | app.py, layouts/*, modules/data_fetcher.py, modules/scoring.py |

---

## 依賴關係圖

```
app.py (Agent 1)
    ├─ 依賴 → modules/data_fetcher.py (Agent 2)
    ├─ 依賴 → modules/scoring.py (Agent 2)
    ├─ 依賴 → modules/charts.py (Agent 4)
    ├─ 依賴 → layouts/sidebar.py (Agent 3)
    ├─ 依賴 → layouts/selection_page.py (Agent 3)
    └─ 依賴 → layouts/realtime_page.py (Agent 3)

layouts/selection_page.py (Agent 3)
    ├─ 依賴 → modules/data_fetcher.py (Agent 2)
    ├─ 依賴 → modules/scoring.py (Agent 2)
    └─ 依賴 → modules/charts.py (Agent 4)
```

---

## 常見問題 Q&A

### Q1: 我需要同時開 4 個電腦嗎？
**A**: 不需要。在同一台電腦開啟 4 個終端視窗即可。

### Q2: 如果某個 Agent 遇到問題卡住了怎麼辦？
**A**: 其他 Agent 可以繼續開發。完成的模組可以先提交，問題模組稍後處理。

### Q3: Worktree 會不會互相干擾？
**A**: 不會。每個 worktree 是獨立的工作目錄，但共享同一個 .git 資料庫。

### Q4: 如何確保各 Agent 的程式碼風格一致？
**A**: 所有 Agent 都需參考 `CLAUDE.md` 和 `real_time_panel.py`。

### Q5: 整合時發生衝突怎麼辦？
**A**: 按照檔案所有權原則，優先保留該檔案負責 Agent 的版本。

---

## 清理 Worktree

專案完成後，清理 worktree：

```bash
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system

git worktree remove ../worktree-core
git worktree remove ../worktree-data
git worktree remove ../worktree-ui
git worktree remove ../worktree-charts

# 刪除遠端分支（如果已推送）
git branch -d feature/core-infrastructure
git branch -d feature/data-scoring
git branch -d feature/ui-layouts
git branch -d feature/charts
```

---

## 聯絡資訊

- 主專案說明: `CLAUDE.md`
- Agent 1 任務: `AGENT_1_CORE.md`
- Agent 2 任務: `AGENT_2_DATA.md`
- Agent 3 任務: `AGENT_3_UI.md`
- Agent 4 任務: `AGENT_4_CHARTS.md`

---

**文件版本**: v1.0
**建立日期**: 2026-01-04
**適用專案**: 選股評分系統 (Swing Trade Score System)
