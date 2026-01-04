# 快速啟動指南 - Multi-Agent 開發

## 一鍵設置 Git Worktree

複製並執行以下命令來設置所有 worktree：

```bash
# 切換到專案目錄
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system

# 建立 4 個 worktree（一次執行）
git worktree add ../worktree-core feature/core-infrastructure && ^
git worktree add ../worktree-data feature/data-scoring && ^
git worktree add ../worktree-ui feature/ui-layouts && ^
git worktree add ../worktree-charts feature/charts

# 確認 worktree 建立成功
git worktree list
```

**預期輸出**:
```
C:/Users/User/Documents/_05_看盤波段/Swing_trade_score_system       [main]
C:/Users/User/Documents/_05_看盤波段/worktree-core                  [feature/core-infrastructure]
C:/Users/User/Documents/_05_看盤波段/worktree-data                  [feature/data-scoring]
C:/Users/User/Documents/_05_看盤波段/worktree-ui                    [feature/ui-layouts]
C:/Users/User/Documents/_05_看盤波段/worktree-charts                [feature/charts]
```

---

## 開啟 4 個 Claude CLI 終端

### 方法 1: 使用 Windows Terminal（推薦）

在 Windows Terminal 中：
1. 開啟第一個終端，執行：
   ```bash
   cd C:\Users\User\Documents\_05_看盤波段\worktree-core
   conda activate my_project
   ```

2. 按 `Ctrl + Shift + D` 新增第二個分頁，執行：
   ```bash
   cd C:\Users\User\Documents\_05_看盤波段\worktree-data
   conda activate my_project
   ```

3. 重複步驟 2，分別切換到 `worktree-ui` 和 `worktree-charts`

### 方法 2: 使用 CMD/PowerShell

開啟 4 個獨立的 CMD 視窗，分別執行：

**終端 1 (Agent 1)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-core
conda activate my_project
claude
```

**終端 2 (Agent 2)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-data
conda activate my_project
claude
```

**終端 3 (Agent 3)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-ui
conda activate my_project
claude
```

**終端 4 (Agent 4)**:
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-charts
conda activate my_project
claude
```

---

## 分配任務給 Agent

在每個 Claude CLI 中輸入對應指令：

| 終端 | Agent | 指令 |
|------|-------|------|
| 終端 1 | Agent 1 | `參考 AGENT_1_CORE.md 完成核心架構開發` |
| 終端 2 | Agent 2 | `參考 AGENT_2_DATA.md 完成資料與評分模組` |
| 終端 3 | Agent 3 | `參考 AGENT_3_UI.md 完成 UI 佈局模組` |
| 終端 4 | Agent 4 | `參考 AGENT_4_CHARTS.md 完成圖表模組` |

---

## 監控開發進度

### 查看各 Agent 狀態

在主專案目錄執行：

```bash
# 查看所有分支狀態
git branch -a

# 查看各分支最新 commit
git log --oneline --graph --all --decorate -10
```

### 查看檔案修改

```bash
# 查看 Agent 1 的修改
cd ../worktree-core && git status

# 查看 Agent 2 的修改
cd ../worktree-data && git status

# 查看 Agent 3 的修改
cd ../worktree-ui && git status

# 查看 Agent 4 的修改
cd ../worktree-charts && git status
```

---

## 整合與測試

### 階段 1: 各 Agent 獨立測試

每個 Agent 完成開發後，在各自的 worktree 中測試：

```bash
# 在對應的 worktree 目錄執行
python test_xxx.py
```

### 階段 2: 提交代碼

在每個 worktree 中：

```bash
git add .
git commit -m "[Agent-N] 模組名稱: 簡短描述

Co-Authored-By: Claude <noreply@anthropic.com>"
```

### 階段 3: 合併分支

**重要**: 在主專案目錄執行（不是 worktree）

```bash
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system

# 切換到 main 分支
git checkout main

# 依序合併各分支
git merge feature/core-infrastructure
git merge feature/data-scoring
git merge feature/ui-layouts
git merge feature/charts

# 解決衝突（如有）
# 編輯衝突檔案後執行：
git add .
git commit -m "Merge: 整合所有模組"
```

### 階段 4: 執行整合測試

```bash
conda activate my_project
python app.py
```

訪問 `http://127.0.0.1:8050/` 測試所有功能。

---

## 建立 Pull Request

### 方法 1: 使用 GitHub CLI

```bash
# 推送到遠端
git push origin main

# 或推送各分支
git push origin feature/core-infrastructure
git push origin feature/data-scoring
git push origin feature/ui-layouts
git push origin feature/charts

# 建立 PR
gh pr create --title "完成選股評分系統開發" --body "$(cat <<'EOF'
## 變更摘要
- Agent 1: 完成核心架構與應用入口
- Agent 2: 完成資料取得與評分引擎
- Agent 3: 完成所有 UI 佈局元件
- Agent 4: 完成圖表視覺化模組

## 測試結果
- [x] 單元測試通過
- [x] 整合測試通過
- [x] UI 顯示正常

## 截圖
（如有，請附上截圖）

🤖 Generated with Multi-Agent Development
EOF
)"
```

### 方法 2: 使用 Git 命令

```bash
# 推送所有分支
git push origin main
git push origin feature/core-infrastructure
git push origin feature/data-scoring
git push origin feature/ui-layouts
git push origin feature/charts
```

然後在 GitHub 網頁介面手動建立 PR。

---

## 清理 Worktree

專案完成後：

```bash
cd C:\Users\User\Documents\_05_看盤波段\Swing_trade_score_system

# 移除所有 worktree
git worktree remove ../worktree-core
git worktree remove ../worktree-data
git worktree remove ../worktree-ui
git worktree remove ../worktree-charts

# 刪除本地分支（可選）
git branch -d feature/core-infrastructure
git branch -d feature/data-scoring
git branch -d feature/ui-layouts
git branch -d feature/charts

# 刪除遠端分支（可選）
git push origin --delete feature/core-infrastructure
git push origin --delete feature/data-scoring
git push origin --delete feature/ui-layouts
git push origin --delete feature/charts
```

---

## 常見問題

### Q: 如果某個 worktree 建立失敗？

**A**: 手動建立該分支，然後再建立 worktree：
```bash
git checkout -b feature/core-infrastructure
git checkout main
git worktree add ../worktree-core feature/core-infrastructure
```

### Q: 如何切換到某個 Agent 的分支查看？

**A**: 直接切換到對應的 worktree 目錄：
```bash
cd C:\Users\User\Documents\_05_看盤波段\worktree-core
```

### Q: 合併時發生衝突怎麼辦？

**A**:
1. 查看衝突檔案：`git status`
2. 手動編輯衝突檔案，選擇保留哪個版本
3. 標記為已解決：`git add <file>`
4. 完成合併：`git commit`

### Q: 如何查看所有 Agent 的進度？

**A**:
```bash
git log --all --oneline --graph --decorate
```

---

## 檔案清單

開發完成後，專案結構應如下：

```
Swing_trade_score_system/
├── app.py                      ✅ Agent 1
├── .env                        ✅ Agent 1
├── .gitignore                  ✅ Agent 1
│
├── modules/
│   ├── __init__.py            ✅ Agent 1
│   ├── data_fetcher.py        ✅ Agent 2
│   ├── scoring.py             ✅ Agent 2
│   └── charts.py              ✅ Agent 4
│
├── layouts/
│   ├── __init__.py            ✅ Agent 1
│   ├── sidebar.py             ✅ Agent 3
│   ├── selection_page.py      ✅ Agent 3
│   └── realtime_page.py       ✅ Agent 3
│
└── 文件/
    ├── CLAUDE.md              📄 專案說明
    ├── MULTI_AGENT_GUIDE.md   📄 多 Agent 協調指南
    ├── AGENT_1_CORE.md        📄 Agent 1 任務
    ├── AGENT_2_DATA.md        📄 Agent 2 任務
    ├── AGENT_3_UI.md          📄 Agent 3 任務
    ├── AGENT_4_CHARTS.md      📄 Agent 4 任務
    └── QUICK_START.md         📄 本文件
```

---

**文件版本**: v1.0
**建立日期**: 2026-01-04
