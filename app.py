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
print("🚀 正在載入 Finlab 資料...")
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

print(f"✅ 資料載入完成！最新交易日: {CACHED_DATA['close'].index[-1].strftime('%Y-%m-%d')}")

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
    elif pathname == '/selection' or pathname == '/':
        return create_selection_page()
    else:
        return html.Div([
            html.H1("404 - 頁面不存在"),
            html.P("請使用側邊導航欄選擇頁面")
        ])

# 啟動應用
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=8050)
