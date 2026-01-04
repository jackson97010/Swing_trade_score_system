# Agent 3 - UI Layouts 任務說明

## 身份識別
- **Agent ID**: Agent 3
- **負責模組**: 使用者介面佈局 (UI Layouts)
- **分支名稱**: `feature/ui-layouts`
- **Worktree 路徑**: `C:\Users\User\Documents\_05_看盤波段\worktree-ui`

---

## 任務目標

建立選股評分系統的所有 UI 元件，包括：
1. 側邊導航欄
2. 選股評分頁面 (主要功能)
3. 即時戰情室頁面 (次要，可簡化)

---

## 必須完成的檔案

### 1. `layouts/sidebar.py` - 側邊導航欄
**優先級**: 🟡 中等

#### 功能需求
- 顯示應用標題
- 提供導航按鈕 (即時戰情室、選股評分系統)
- 根據當前路徑高亮對應按鈕

#### 程式碼範本

```python
"""
側邊導航欄元件
"""

from dash import html, dcc


def create_sidebar(current_path: str = '/') -> html.Div:
    """
    建立側邊導航欄

    Args:
        current_path: 當前頁面路徑

    Returns:
        html.Div: 側邊導航欄元件
    """
    return html.Div([
        # 標題
        html.H2(
            "台股戰情室",
            style={
                'color': '#ffffff',
                'margin-bottom': '30px',
                'text-align': 'center',
                'font-weight': 'bold'
            }
        ),

        html.Hr(style={'border-color': '#444', 'margin': '20px 0'}),

        # 導航按鈕組
        html.Div([
            # 即時戰情室按鈕
            dcc.Link(
                html.Button(
                    [
                        html.Span("🔴 ", style={'font-size': '18px'}),
                        html.Span("即時戰情室")
                    ],
                    style={
                        'width': '100%',
                        'padding': '15px',
                        'margin-bottom': '15px',
                        'background-color': '#d32f2f' if current_path == '/realtime' else '#424242',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '8px',
                        'cursor': 'pointer',
                        'font-size': '16px',
                        'font-weight': 'bold' if current_path == '/realtime' else 'normal',
                        'transition': 'all 0.3s',
                        'box-shadow': '0 2px 4px rgba(0,0,0,0.2)' if current_path == '/realtime' else 'none'
                    }
                ),
                href='/realtime',
                style={'text-decoration': 'none'}
            ),

            # 選股評分系統按鈕
            dcc.Link(
                html.Button(
                    [
                        html.Span("📊 ", style={'font-size': '18px'}),
                        html.Span("選股評分系統")
                    ],
                    style={
                        'width': '100%',
                        'padding': '15px',
                        'background-color': '#1976d2' if current_path in ['/selection', '/'] else '#424242',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '8px',
                        'cursor': 'pointer',
                        'font-size': '16px',
                        'font-weight': 'bold' if current_path in ['/selection', '/'] else 'normal',
                        'transition': 'all 0.3s',
                        'box-shadow': '0 2px 4px rgba(0,0,0,0.2)' if current_path in ['/selection', '/'] else 'none'
                    }
                ),
                href='/selection',
                style={'text-decoration': 'none'}
            )
        ], style={'margin-top': '20px'}),

        # 版本資訊
        html.Div([
            html.Hr(style={'border-color': '#444', 'margin': '40px 0 20px 0'}),
            html.P(
                "v1.0.0 | 2026",
                style={
                    'color': '#888',
                    'font-size': '12px',
                    'text-align': 'center',
                    'margin-top': '40px'
                }
            )
        ], style={'position': 'absolute', 'bottom': '20px', 'width': 'calc(100% - 40px)'})

    ], style={
        'position': 'relative',
        'height': '100%'
    })


# 匯出函數
__all__ = ['create_sidebar']
```

---

### 2. `layouts/selection_page.py` - 選股評分頁面
**優先級**: 🔴 最高 (主要功能)

#### 功能需求
- 股票代碼輸入框
- 計算評分按鈕
- 評分結果表格
- 個股走勢圖 (點擊表格顯示)

#### 程式碼範本

```python
"""
選股評分頁面 - 主要功能頁面
"""

from dash import html, dcc, dash_table, Input, Output, State, callback
import pandas as pd

# 注意：這些函數由 Agent 2 提供
# from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators, load_industry_data, calculate_industry_trend, get_top_industries
# from modules.scoring import calculate_batch_scores


def create_selection_page() -> html.Div:
    """
    建立選股評分頁面

    Returns:
        html.Div: 選股評分頁面元件
    """
    return html.Div([
        # 頁面標題
        html.Div([
            html.H1(
                "📋 每日選股評分",
                style={'color': '#1976d2', 'margin-bottom': '10px'}
            ),
            html.P(
                "輸入觀察清單，系統依據技術面與基本面進行評分",
                style={'color': '#666', 'font-size': '14px'}
            )
        ], style={'margin-bottom': '30px'}),

        # 輸入區塊
        html.Div([
            html.Div([
                html.Label(
                    "股票代碼（多檔請用逗號分隔）",
                    style={'font-weight': 'bold', 'margin-bottom': '10px', 'display': 'block'}
                ),
                dcc.Input(
                    id='stock-input',
                    type='text',
                    placeholder='例如: 2330, 2454, 3008, 2603',
                    value='2330, 2454, 2603',
                    style={
                        'width': '100%',
                        'padding': '12px',
                        'font-size': '16px',
                        'border': '2px solid #ddd',
                        'border-radius': '5px',
                        'box-sizing': 'border-box'
                    }
                )
            ], style={'flex': '1', 'margin-right': '20px'}),

            html.Div([
                html.Button(
                    "🚀 開始計算評分",
                    id='calculate-btn',
                    n_clicks=0,
                    style={
                        'padding': '12px 30px',
                        'font-size': '16px',
                        'background-color': '#1976d2',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '5px',
                        'cursor': 'pointer',
                        'font-weight': 'bold',
                        'margin-top': '28px'
                    }
                )
            ])
        ], style={'display': 'flex', 'align-items': 'flex-start', 'margin-bottom': '20px'}),

        # 狀態訊息
        html.Div(id='status-message', style={'margin-bottom': '20px'}),

        # 評分結果表格
        html.Div([
            html.H3("評分結果", style={'color': '#333', 'margin-bottom': '15px'}),
            html.Div(id='score-table-container')
        ], style={
            'background-color': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            'margin-bottom': '30px'
        }),

        # 個股走勢圖區塊
        html.Div([
            html.H3("📈 個股走勢", style={'color': '#333', 'margin-bottom': '15px'}),
            html.P(
                "點擊表格中的股票查看走勢圖",
                style={'color': '#666', 'font-size': '14px', 'margin-bottom': '15px'}
            ),
            dcc.Graph(id='stock-chart', style={'height': '500px'})
        ], style={
            'background-color': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
        })

    ], style={'padding': '20px'})


# Callback: 計算評分
@callback(
    [Output('score-table-container', 'children'),
     Output('status-message', 'children')],
    Input('calculate-btn', 'n_clicks'),
    State('stock-input', 'value'),
    prevent_initial_call=True
)
def calculate_scores(n_clicks, stock_input):
    """
    計算股票評分

    注意：此函數需要 Agent 2 的模組完成後才能正常運作
    """
    if not stock_input:
        return None, html.Div("⚠️ 請輸入股票代碼", style={'color': 'orange'})

    try:
        # 解析股票代碼
        stock_codes = [code.strip() for code in stock_input.split(',')]

        # TODO: 取消註解以下程式碼（等 Agent 2 完成）
        # from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators, load_industry_data, calculate_industry_trend, get_top_industries
        # from modules.scoring import calculate_batch_scores

        # # 取得資料
        # stock_data = fetch_stock_data(stock_codes)
        # tech_indicators = calculate_technical_indicators(stock_data['close'])
        #
        # # 計算產業趨勢
        # industry_df = load_industry_data()
        # industry_trend = calculate_industry_trend(stock_data['close'], industry_df)
        # top_industries = get_top_industries(industry_trend)
        #
        # # 計算評分
        # scores_df = calculate_batch_scores(stock_codes, stock_data, tech_indicators, industry_df, top_industries)

        # 暫時使用模擬資料
        scores_df = pd.DataFrame({
            '代碼': stock_codes,
            '名稱': ['台積電', '聯發科', '大立光'][:len(stock_codes)],
            '總分': [60, 50, 40][:len(stock_codes)],
            '參考價': [580.0, 980.0, 2500.0][:len(stock_codes)],
            '成交金額(億)': [250.5, 25.4, 15.2][:len(stock_codes)],
            '月營收YoY%': [15.5, 25.4, -5.2][:len(stock_codes)],
            'EPS(季)': [8.5, 15.2, 25.8][:len(stock_codes)],
            '評分說明': ['均線多排(+20), MACD多頭(+20), 營收強勁(+10), 強勢族群(+10)',
                         'MACD多頭(+20), 營收強勁(+10), 成交活絡(+10)',
                         '無符合條件'][:len(stock_codes)]
        })

        # 建立表格
        table = dash_table.DataTable(
            id='score-table',
            columns=[{"name": col, "id": col} for col in scores_df.columns],
            data=scores_df.to_dict('records'),
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Arial, sans-serif'
            },
            style_header={
                'backgroundColor': '#1976d2',
                'color': 'white',
                'fontWeight': 'bold',
                'fontSize': '14px'
            },
            style_data_conditional=[
                {
                    'if': {'row_index': 'odd'},
                    'backgroundColor': '#f9f9f9'
                },
                {
                    'if': {'column_id': '總分'},
                    'fontWeight': 'bold',
                    'color': '#1976d2'
                }
            ],
            row_selectable='single',
            selected_rows=[]
        )

        status = html.Div(
            f"✅ 計算完成！共 {len(stock_codes)} 檔股票",
            style={'color': 'green', 'font-weight': 'bold'}
        )

        return table, status

    except Exception as e:
        return None, html.Div(
            f"❌ 計算失敗: {str(e)}",
            style={'color': 'red'}
        )


# Callback: 顯示個股走勢圖
@callback(
    Output('stock-chart', 'figure'),
    Input('score-table', 'selected_rows'),
    State('score-table', 'data'),
    prevent_initial_call=True
)
def display_stock_chart(selected_rows, table_data):
    """
    顯示選中股票的走勢圖

    注意：此函數需要 Agent 4 的圖表模組完成後才能正常運作
    """
    if not selected_rows or not table_data:
        return {}

    selected_stock = table_data[selected_rows[0]]
    stock_code = selected_stock['代碼']

    # TODO: 使用 Agent 4 的圖表模組
    # from modules.charts import create_candlestick_chart
    # return create_candlestick_chart(stock_code)

    # 暫時返回空圖表
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.add_annotation(
        text=f"圖表模組開發中... (股票: {stock_code})",
        xref="paper", yref="paper",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, color="gray")
    )
    fig.update_layout(
        title=f"{selected_stock['名稱']} ({stock_code}) 走勢圖",
        xaxis_title="日期",
        yaxis_title="價格",
        height=500
    )
    return fig


# 匯出函數
__all__ = ['create_selection_page']
```

---

### 3. `layouts/realtime_page.py` - 即時戰情室頁面
**優先級**: 🟢 低 (可簡化或使用佔位符)

#### 功能需求
- 簡單的佔位符頁面
- 說明此功能需要 Redis 整合

#### 程式碼範本

```python
"""
即時戰情室頁面 - 佔位符版本
"""

from dash import html


def create_realtime_page() -> html.Div:
    """
    建立即時戰情室頁面（簡化版）

    Returns:
        html.Div: 即時戰情室頁面元件
    """
    return html.Div([
        # 頁面標題
        html.Div([
            html.H1(
                "🔴 即時戰情室",
                style={'color': '#d32f2f', 'margin-bottom': '10px'}
            ),
            html.P(
                "即時監控台股市場動態",
                style={'color': '#666', 'font-size': '14px'}
            )
        ], style={'margin-bottom': '30px'}),

        # 提示訊息
        html.Div([
            html.Div([
                html.H3("⚠️ 功能開發中", style={'color': '#ff9800', 'margin-bottom': '15px'}),
                html.P([
                    "此功能需要 Redis 即時資料串流支援。",
                    html.Br(),
                    "目前 Redis 資料源尚未啟用，請先使用「選股評分系統」功能。"
                ], style={'color': '#666', 'line-height': '1.8'}),

                html.Hr(style={'margin': '20px 0'}),

                html.H4("參考功能：", style={'color': '#333', 'margin-bottom': '10px'}),
                html.Ul([
                    html.Li("即時 Tick 資料串流"),
                    html.Li("族群成交金額占比"),
                    html.Li("族群漲跌幅分布"),
                    html.Li("個股即時走勢圖")
                ], style={'color': '#666', 'line-height': '2'}),

                html.P([
                    html.Br(),
                    "詳細說明請參考 ",
                    html.Code("real_time_panel.py"),
                    " 範例程式。"
                ], style={'color': '#999', 'font-size': '14px', 'margin-top': '20px'})
            ])
        ], style={
            'background-color': '#fff3e0',
            'padding': '30px',
            'border-radius': '8px',
            'border-left': '5px solid #ff9800',
            'max-width': '800px'
        })

    ], style={'padding': '20px'})


# 匯出函數
__all__ = ['create_realtime_page']
```

---

## 測試方式

### 階段 1: UI 元件測試（不依賴其他 Agent）

建立測試檔案 `test_ui.py`:

```python
from dash import Dash
from layouts.sidebar import create_sidebar
from layouts.selection_page import create_selection_page
from layouts.realtime_page import create_realtime_page

app = Dash(__name__)

# 測試側邊欄
sidebar = create_sidebar('/selection')
print("✅ 側邊欄元件建立成功")

# 測試選股評分頁面
selection = create_selection_page()
print("✅ 選股評分頁面建立成功")

# 測試即時戰情室頁面
realtime = create_realtime_page()
print("✅ 即時戰情室頁面建立成功")
```

### 階段 2: 整合測試（與 Agent 1 整合）

與 Agent 1 的 `app.py` 整合後，訪問：
- `http://127.0.0.1:8050/selection` - 測試選股評分頁面
- `http://127.0.0.1:8050/realtime` - 測試即時戰情室頁面

---

## Commit 訊息範例

```
[Agent-3] UI Layouts: 實作所有頁面佈局元件

- 實作 sidebar.py: 側邊導航欄
- 實作 selection_page.py: 選股評分頁面（含表格與圖表）
- 實作 realtime_page.py: 即時戰情室頁面（佔位符版本）
- 新增 Dash callback 處理評分計算與圖表顯示

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 依賴關係

**依賴模組**:
- Agent 2 的 `modules/data_fetcher.py` 和 `modules/scoring.py` (用於資料處理)
- Agent 4 的 `modules/charts.py` (用於圖表顯示)

**開發策略**:
1. 先建立 UI 框架與佔位符
2. 等 Agent 2 和 Agent 4 完成後，取消註解相關 import

---

## 注意事項

1. ⚠️ **保留模擬資料**：在其他 Agent 完成前，使用模擬資料測試 UI
2. ⚠️ **參考 sample.png**：確保 UI 配置符合設計稿
3. ⚠️ **參考 real_time_panel.py**：保持程式碼風格一致
4. ⚠️ **響應式設計**：確保表格和圖表在不同螢幕尺寸下正常顯示

---

## 參考資料

- 主專案說明: `CLAUDE.md`
- UI 設計參考: `sample.png`
- 參考程式碼: `real_time_panel.py`
- 協調文件: `MULTI_AGENT_GUIDE.md`

---

**任務文件版本**: v1.0
**建立日期**: 2026-01-04
**預計完成時間**: 3-4 小時
