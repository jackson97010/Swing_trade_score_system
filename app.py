"""
台股戰情室 - 選股評分系統
現代化 UI 設計
"""

from dash import Dash, dcc, html, Input, Output, State
from finlab import login, data
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import pandas as pd

# 載入環境變數
load_dotenv()

# Finlab 登入
FINLAB_TOKEN = os.getenv('FINLAB_TOKEN')
login(FINLAB_TOKEN)

# ========== 啟動時載入資料 ==========
print("[INFO] 正在載入 Finlab 資料...")
data.set_universe('TSE_OTC')
data.truncate_start = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')

# 載入並快取資料
CACHED_DATA = {
    'close': data.get('price:收盤價'),
    'trade_value': data.get('price:成交金額'),
    'revenue_yoy': data.get('monthly_revenue:去年同月增減(%)'),
}

# 載入股票名稱
from finlab.markets.tw import TWMarket
market = TWMarket()
CACHED_DATA['stock_names'] = market.get_asset_id_to_name()

# 載入產業分類
INDUSTRY_CSV = r'C:\Users\user\Documents\_12_BO_strategy\產業分類資料庫.csv'
CACHED_DATA['industry_df'] = pd.read_csv(INDUSTRY_CSV)
CACHED_DATA['industry_df']['代碼'] = CACHED_DATA['industry_df']['代碼'].astype(str)

print(f"[DONE] 資料載入完成！最新交易日: {CACHED_DATA['close'].index[-1].strftime('%Y-%m-%d')}")

# 載入樣式
from layouts.styles import COLORS, MAIN_STYLES, SIDEBAR_STYLES

# 初始化 Dash 應用
app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1.0'}]
)
app.title = "台股戰情室 - 選股評分系統"

# 導入 layouts
from layouts.sidebar import create_sidebar
from layouts.selection_page import create_selection_page
from layouts.realtime_page import create_realtime_page
from layouts.ranking_page import create_ranking_page
from layouts.sector_page import create_sector_page

# 主佈局
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),

    # 側邊導航欄 (左側)
    html.Div(id='sidebar-container'),

    # 主內容區 (右側)
    html.Div(
        id='page-content',
        style=MAIN_STYLES['container']
    )
], style={
    'display': 'flex',
    'minHeight': '100vh',
    'backgroundColor': COLORS['bg_page'],
    'fontFamily': '"Noto Sans TC", "Inter", -apple-system, BlinkMacSystemFont, sans-serif',
})

# 自訂 CSS (內嵌)
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Noto Sans TC', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
                background-color: #F3F4F6;
            }

            /* 滾動條樣式 */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }

            ::-webkit-scrollbar-track {
                background: #F3F4F6;
            }

            ::-webkit-scrollbar-thumb {
                background: #D1D5DB;
                border-radius: 4px;
            }

            ::-webkit-scrollbar-thumb:hover {
                background: #9CA3AF;
            }

            /* 按鈕 hover 效果 */
            button:hover {
                opacity: 0.9;
                transform: translateY(-1px);
            }

            button:active {
                transform: translateY(0);
            }

            /* 日期選擇器樣式 */
            .DateInput_input {
                font-family: 'Noto Sans TC', 'Inter', sans-serif !important;
                font-size: 14px !important;
                padding: 10px 12px !important;
                border-radius: 8px !important;
                border: 1px solid #E5E7EB !important;
            }

            .DateInput_input__focused {
                border-color: #3B82F6 !important;
                box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
            }

            .SingleDatePickerInput {
                border-radius: 8px !important;
                border: none !important;
            }

            .CalendarDay__selected {
                background: #3B82F6 !important;
                border: 1px solid #3B82F6 !important;
            }

            /* DataTable 樣式覆蓋 */
            .dash-table-container .dash-spreadsheet-container {
                border-radius: 8px;
                overflow: hidden;
            }

            .dash-table-container .dash-spreadsheet-inner th {
                border: none !important;
            }

            .dash-table-container .dash-spreadsheet-inner td {
                border: none !important;
                border-bottom: 1px solid #F3F4F6 !important;
            }

            /* 導航連結樣式 */
            a {
                text-decoration: none !important;
            }

            /* 側邊欄 hover 效果 */
            .nav-item:hover {
                background-color: #334155 !important;
                color: #FFFFFF !important;
            }

            /* 統計卡片動畫 */
            .stat-card {
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            .stat-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Callback: 更新側邊欄
@app.callback(
    Output('sidebar-container', 'children'),
    Input('url', 'pathname')
)
def update_sidebar(pathname):
    """更新側邊導航欄"""
    return create_sidebar(pathname)

# Callback: 路由處理
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    """根據 URL 顯示對應頁面"""
    if pathname == '/realtime':
        return create_realtime_page()
    elif pathname == '/selection':
        return create_selection_page()
    elif pathname == '/ranking' or pathname == '/':
        return create_ranking_page()
    elif pathname == '/sector':
        return create_sector_page()
    else:
        return html.Div([
            html.H1("404 - 頁面不存在", style={'color': COLORS['text_primary']}),
            html.P("請使用側邊導航欄選擇頁面", style={'color': COLORS['text_secondary']})
        ], style={'padding': '40px'})

# 啟動應用
if __name__ == '__main__':
    print("\n" + "="*50)
    print("  台股戰情室 - 選股評分系統")
    print("="*50)
    print(f"\n  本機連線: http://127.0.0.1:8050/")
    print(f"  內網連線: http://192.168.x.x:8050/")
    print("\n" + "="*50 + "\n")

    app.run(debug=True, host='0.0.0.0', port=8050)
