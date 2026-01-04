# Agent 1 - Core Infrastructure 任務說明

## 身份識別
- **Agent ID**: Agent 1
- **負責模組**: 核心架構 (Core Infrastructure)
- **分支名稱**: `feature/core-infrastructure`
- **Worktree 路徑**: `C:\Users\User\Documents\_05_看盤波段\worktree-core`

---

## 任務目標

建立選股評分系統的核心架構，包括：
1. Dash 應用程式主入口 (`app.py`)
2. 模組與佈局初始化檔案
3. 環境變數設定
4. 導航與頁面路由邏輯

---

## 必須完成的檔案

### 1. `app.py` - 主程式入口
**優先級**: 🔴 最高

#### 功能需求
- 初始化 Dash 應用
- 設定 Finlab 登入
- 整合所有 layouts 模組
- 設定頁面路由 (URL routing)
- 設定 callback 邏輯處理導航切換

#### 參考程式碼結構
```python
from dash import Dash, dcc, html, Input, Output, State
from finlab import login
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 初始化 Dash 應用
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)
app.title = "台股戰情室 - 選股評分系統"

# Finlab 登入
FINLAB_API_KEY = os.getenv('FINLAB_API_KEY')
login(FINLAB_API_KEY)

# 導入 layouts (等其他 Agent 完成後取消註解)
# from layouts.sidebar import create_sidebar
# from layouts.selection_page import create_selection_page
# from layouts.realtime_page import create_realtime_page

# 主佈局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div([
        # 側邊導航欄 (左側)
        html.Div(
            id='sidebar-container',
            style={
                'width': '250px',
                'position': 'fixed',
                'left': '0',
                'top': '0',
                'bottom': '0',
                'background-color': '#1e1e1e',
                'padding': '20px',
                'overflow-y': 'auto'
            }
        ),
        # 主內容區 (右側)
        html.Div(
            id='page-content',
            style={
                'margin-left': '250px',
                'padding': '20px',
                'background-color': '#f5f5f5',
                'min-height': '100vh'
            }
        )
    ])
])

# Callback: 更新側邊欄
@app.callback(
    Output('sidebar-container', 'children'),
    Input('url', 'pathname')
)
def update_sidebar(pathname):
    """更新側邊導航欄"""
    # 暫時返回基礎版本，等 Agent 3 完成 sidebar.py 後替換
    return html.Div([
        html.H2("台股戰情室", style={'color': 'white', 'margin-bottom': '30px'}),
        html.Hr(style={'border-color': '#444'}),

        # 導航按鈕
        dcc.Link(
            html.Button(
                "即時戰情室",
                id='btn-realtime',
                style={
                    'width': '100%',
                    'padding': '12px',
                    'margin-bottom': '10px',
                    'background-color': '#d32f2f' if pathname == '/realtime' else '#444',
                    'color': 'white',
                    'border': 'none',
                    'border-radius': '5px',
                    'cursor': 'pointer',
                    'font-size': '16px'
                }
            ),
            href='/realtime'
        ),

        dcc.Link(
            html.Button(
                "選股評分系統",
                id='btn-selection',
                style={
                    'width': '100%',
                    'padding': '12px',
                    'background-color': '#1976d2' if pathname == '/selection' else '#444',
                    'color': 'white',
                    'border': 'none',
                    'border-radius': '5px',
                    'cursor': 'pointer',
                    'font-size': '16px'
                }
            ),
            href='/selection'
        )
    ])

# Callback: 路由處理
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """根據 URL 顯示對應頁面"""
    if pathname == '/realtime':
        # return create_realtime_page()  # 等 Agent 3 完成後取消註解
        return html.Div([
            html.H1("即時戰情室"),
            html.P("此頁面由 Agent 3 開發中...")
        ])
    elif pathname == '/selection' or pathname == '/':
        # return create_selection_page()  # 等 Agent 3 完成後取消註解
        return html.Div([
            html.H1("選股評分系統"),
            html.P("此頁面由 Agent 3 開發中...")
        ])
    else:
        return html.Div([
            html.H1("404 - 頁面不存在"),
            html.P("請使用側邊導航欄選擇頁面")
        ])

# 啟動應用
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
```

---

### 2. `.env` - 環境變數設定
**優先級**: 🔴 最高

建立 `.env` 檔案並加入 Finlab API Key：

```env
FINLAB_API_KEY=Y8qx8Zs1zTnNk7McQPGpR4Lb9jv29EMQpiOMAxyBpmcIK4mYc2vODIvD8PuXLctw
```

**重要**: 確保 `.env` 已加入 `.gitignore`

---

### 3. `modules/__init__.py` - 模組初始化
**優先級**: 🟡 中等

```python
"""
選股評分系統 - 功能模組

此套件包含以下模組：
- data_fetcher: 資料取得模組 (Agent 2)
- scoring: 評分計算引擎 (Agent 2)
- charts: 圖表繪製模組 (Agent 4)
"""

__version__ = '1.0.0'
__author__ = 'Claude AI Agents'

# 模組載入 (等其他 Agent 完成後取消註解)
# from .data_fetcher import *
# from .scoring import *
# from .charts import *

__all__ = [
    # 'fetch_stock_data',
    # 'calculate_score',
    # 'create_candlestick_chart'
]
```

---

### 4. `layouts/__init__.py` - UI 佈局初始化
**優先級**: 🟡 中等

```python
"""
選股評分系統 - UI 佈局模組

此套件包含以下 UI 元件：
- sidebar: 側邊導航欄 (Agent 3)
- selection_page: 選股評分頁面 (Agent 3)
- realtime_page: 即時戰情室頁面 (Agent 3)
"""

__version__ = '1.0.0'

# UI 元件載入 (等 Agent 3 完成後取消註解)
# from .sidebar import create_sidebar
# from .selection_page import create_selection_page
# from .realtime_page import create_realtime_page

__all__ = [
    # 'create_sidebar',
    # 'create_selection_page',
    # 'create_realtime_page'
]
```

---

### 5. `.gitignore` - Git 忽略清單
**優先級**: 🟡 中等

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/

# 環境變數
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Finlab Cache
.finlab/

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db
```

---

## 整合檢查清單

完成基礎開發後，需要等待其他 Agent：

### 等待 Agent 2 (Data & Scoring)
- [ ] `modules/data_fetcher.py` 完成
- [ ] `modules/scoring.py` 完成
- [ ] 更新 `modules/__init__.py` 的 import 語句

### 等待 Agent 3 (UI Layouts)
- [ ] `layouts/sidebar.py` 完成
- [ ] `layouts/selection_page.py` 完成
- [ ] `layouts/realtime_page.py` 完成
- [ ] 更新 `layouts/__init__.py` 的 import 語句
- [ ] 在 `app.py` 中啟用 layout import

### 等待 Agent 4 (Charts)
- [ ] `modules/charts.py` 完成
- [ ] 更新 `modules/__init__.py` 的 import 語句

---

## 測試方式

### 階段 1: 基礎架構測試（不依賴其他 Agent）
```bash
conda activate my_project
python app.py
```

訪問 `http://127.0.0.1:8050/` 應看到：
- 側邊導航欄正常顯示
- 點擊按鈕可切換 URL
- 頁面顯示「開發中」的佔位符內容

### 階段 2: 整合測試（所有 Agent 完成後）
1. 取消 `app.py` 中所有註解的 import
2. 重新執行程式
3. 測試所有功能是否正常運作

---

## Commit 訊息範例

```
[Agent-1] Core: 建立 Dash 應用基礎架構

- 設定 app.py 主程式與路由邏輯
- 建立 .env 環境變數設定
- 建立 modules 與 layouts 初始化檔案
- 設定 .gitignore

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 依賴關係

**此模組不依賴其他 Agent**，可以獨立開發。

但其他 Agent 會依賴此模組：
- Agent 2 需要 `modules/__init__.py` 的結構
- Agent 3 需要 `layouts/__init__.py` 的結構
- Agent 4 需要 `modules/__init__.py` 的結構

---

## 注意事項

1. ⚠️ **不要修改其他 Agent 的檔案**：僅能建立 `__init__.py` 和 `app.py`
2. ⚠️ **保留註解的 import**：等其他 Agent 完成後再取消註解
3. ⚠️ **確保 .env 不被追蹤**：檢查 `.gitignore` 設定
4. ⚠️ **參考 real_time_panel.py**：保持程式碼風格一致

---

## 參考資料

- 主專案說明: `CLAUDE.md`
- 參考程式碼: `real_time_panel.py`
- 協調文件: `MULTI_AGENT_GUIDE.md`

---

**任務文件版本**: v1.0
**建立日期**: 2026-01-04
**預計完成時間**: 2-3 小時
