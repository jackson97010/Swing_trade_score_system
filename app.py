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
