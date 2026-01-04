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
