"""
族群熱力圖頁面 - 顯示族群每日漲跌幅熱力圖
"""

from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def create_sector_page() -> html.Div:
    """
    建立族群熱力圖頁面

    Returns:
        html.Div: 族群熱力圖頁面元件
    """
    return html.Div([
        # 頁面標題
        html.Div([
            html.H1(
                "🔥 族群熱力圖",
                style={'color': '#9c27b0', 'margin-bottom': '10px'}
            ),
            html.P(
                "查看族群每日漲跌幅與成交金額分布",
                style={'color': '#666', 'font-size': '14px'}
            )
        ], style={'margin-bottom': '30px'}),

        # 控制區
        html.Div([
            html.Div([
                html.Label("顯示天數", style={'font-weight': 'bold', 'margin-right': '10px'}),
                dcc.Dropdown(
                    id='sector-days-dropdown',
                    options=[
                        {'label': '10 天', 'value': 10},
                        {'label': '20 天', 'value': 20},
                        {'label': '30 天', 'value': 30},
                        {'label': '60 天', 'value': 60}
                    ],
                    value=20,
                    style={'width': '120px', 'display': 'inline-block'}
                )
            ], style={'display': 'inline-block', 'margin-right': '30px'}),

            html.Div([
                html.Label("顯示族群數", style={'font-weight': 'bold', 'margin-right': '10px'}),
                dcc.Dropdown(
                    id='sector-count-dropdown',
                    options=[
                        {'label': '15 個', 'value': 15},
                        {'label': '20 個', 'value': 20},
                        {'label': '25 個', 'value': 25},
                        {'label': '30 個', 'value': 30}
                    ],
                    value=20,
                    style={'width': '120px', 'display': 'inline-block'}
                )
            ], style={'display': 'inline-block', 'margin-right': '30px'}),

            html.Button(
                "🔄 更新圖表",
                id='sector-refresh-btn',
                n_clicks=0,
                style={
                    'padding': '10px 20px',
                    'background-color': '#9c27b0',
                    'color': 'white',
                    'border': 'none',
                    'border-radius': '5px',
                    'cursor': 'pointer',
                    'font-weight': 'bold'
                }
            )
        ], style={'margin-bottom': '30px'}),

        # 族群漲跌幅熱力圖
        html.Div([
            html.H3("📈 族群每日漲跌幅", style={'color': '#333', 'margin-bottom': '15px'}),
            html.P("紅色 = 上漲 / 綠色 = 下跌（台股配色）", style={'color': '#666', 'font-size': '12px'}),
            dcc.Loading(
                dcc.Graph(id='sector-returns-heatmap', style={'height': '600px'}),
                type='circle'
            )
        ], style={
            'background-color': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            'margin-bottom': '30px'
        }),

        # 族群成交金額比重熱力圖
        html.Div([
            html.H3("💰 族群成交金額比重", style={'color': '#333', 'margin-bottom': '15px'}),
            html.P("顏色越深 = 成交金額占比越高", style={'color': '#666', 'font-size': '12px'}),
            dcc.Loading(
                dcc.Graph(id='sector-volume-heatmap', style={'height': '600px'}),
                type='circle'
            )
        ], style={
            'background-color': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)',
            'margin-bottom': '30px'
        }),

        # 當日族群排行
        html.Div([
            html.H3("📊 今日族群漲跌幅排行", style={'color': '#333', 'margin-bottom': '15px'}),
            html.Div(id='sector-today-ranking')
        ], style={
            'background-color': 'white',
            'padding': '20px',
            'border-radius': '8px',
            'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'
        })

    ], style={'padding': '20px'})


def calculate_sector_returns(close, industry_df):
    """計算族群每日漲跌幅"""
    daily_returns = (close - close.shift(1)) / close.shift(1)

    sector_returns = {}
    for sector, group in industry_df.groupby('細產業別'):
        stock_ids = group['代碼'].astype(str).tolist()
        valid_ids = [s for s in stock_ids if s in daily_returns.columns]
        if len(valid_ids) >= 2:
            sector_returns[sector] = daily_returns[valid_ids].mean(axis=1)

    return pd.DataFrame(sector_returns)


def calculate_sector_volume(trade_value, industry_df):
    """計算族群成交金額"""
    sector_money = {}
    for sector, group in industry_df.groupby('細產業別'):
        stock_ids = group['代碼'].astype(str).tolist()
        valid_ids = [s for s in stock_ids if s in trade_value.columns]
        if len(valid_ids) >= 2:
            sector_money[sector] = trade_value[valid_ids].sum(axis=1)

    df = pd.DataFrame(sector_money)
    # 計算比重
    total = df.sum(axis=1)
    return df.div(total, axis=0)


@callback(
    [Output('sector-returns-heatmap', 'figure'),
     Output('sector-volume-heatmap', 'figure'),
     Output('sector-today-ranking', 'children')],
    [Input('sector-refresh-btn', 'n_clicks'),
     Input('sector-days-dropdown', 'value'),
     Input('sector-count-dropdown', 'value')]
)
def update_sector_heatmaps(n_clicks, days, top_n):
    """更新熱力圖"""
    import app
    close = app.CACHED_DATA['close']
    trade_value = app.CACHED_DATA['trade_value']
    industry_df = app.CACHED_DATA['industry_df']

    # 計算族群漲跌幅
    sector_returns = calculate_sector_returns(close, industry_df)
    sector_volume = calculate_sector_volume(trade_value, industry_df)

    # 取最近 N 天
    returns_recent = sector_returns.tail(days)
    volume_recent = sector_volume.tail(days)

    # 依波動度排序選取前 N 個族群
    avg_abs_returns = returns_recent.abs().mean().sort_values(ascending=False)
    top_sectors = avg_abs_returns.head(top_n).index.tolist()

    # ========== 漲跌幅熱力圖 ==========
    returns_plot = returns_recent[top_sectors] * 100  # 轉換為百分比

    # 台股配色：紅色=上漲，綠色=下跌
    fig_returns = go.Figure(data=go.Heatmap(
        z=returns_plot.T.values,
        x=[d.strftime('%m/%d') for d in returns_plot.index],
        y=returns_plot.columns.tolist(),
        colorscale=[
            [0, '#00c853'],      # 深綠（大跌）
            [0.3, '#69f0ae'],    # 淺綠（小跌）
            [0.5, '#ffffff'],    # 白色（平盤）
            [0.7, '#ff8a80'],    # 淺紅（小漲）
            [1, '#d50000']       # 深紅（大漲）
        ],
        zmid=0,
        text=np.round(returns_plot.T.values, 1),
        texttemplate='%{text}',
        textfont={'size': 9},
        hovertemplate='族群: %{y}<br>日期: %{x}<br>漲跌幅: %{z:.2f}%<extra></extra>',
        colorbar=dict(title='漲跌幅(%)')
    ))

    fig_returns.update_layout(
        title=f'族群每日漲跌幅熱力圖（最近 {days} 天）',
        xaxis_title='日期',
        yaxis_title='族群',
        height=max(400, top_n * 25),
        margin=dict(l=150)
    )

    # ========== 成交金額比重熱力圖 ==========
    # 依平均成交金額比重排序
    avg_volume = volume_recent.mean().sort_values(ascending=False)
    top_volume_sectors = avg_volume.head(top_n).index.tolist()
    volume_plot = volume_recent[top_volume_sectors] * 100  # 轉換為百分比

    fig_volume = go.Figure(data=go.Heatmap(
        z=volume_plot.T.values,
        x=[d.strftime('%m/%d') for d in volume_plot.index],
        y=volume_plot.columns.tolist(),
        colorscale='YlOrRd',
        text=np.round(volume_plot.T.values, 1),
        texttemplate='%{text}',
        textfont={'size': 9},
        hovertemplate='族群: %{y}<br>日期: %{x}<br>成交占比: %{z:.2f}%<extra></extra>',
        colorbar=dict(title='占比(%)')
    ))

    fig_volume.update_layout(
        title=f'族群成交金額比重熱力圖（最近 {days} 天）',
        xaxis_title='日期',
        yaxis_title='族群',
        height=max(400, top_n * 25),
        margin=dict(l=150)
    )

    # ========== 今日排行 ==========
    today_returns = returns_recent.iloc[-1].sort_values(ascending=False) * 100
    today_date = returns_recent.index[-1].strftime('%Y-%m-%d')

    # 漲幅前5
    top5_up = today_returns.head(5)
    # 跌幅前5
    top5_down = today_returns.tail(5).sort_values()

    ranking_div = html.Div([
        html.P(f"日期: {today_date}", style={'font-weight': 'bold', 'margin-bottom': '15px'}),

        html.Div([
            # 漲幅前5
            html.Div([
                html.H4("🔴 漲幅前5", style={'color': '#d50000'}),
                html.Ul([
                    html.Li(f"{sector}: {ret:.2f}%", style={'color': '#d50000'})
                    for sector, ret in top5_up.items()
                ])
            ], style={'display': 'inline-block', 'width': '45%', 'vertical-align': 'top'}),

            # 跌幅前5
            html.Div([
                html.H4("🟢 跌幅前5", style={'color': '#00c853'}),
                html.Ul([
                    html.Li(f"{sector}: {ret:.2f}%", style={'color': '#00c853'})
                    for sector, ret in top5_down.items()
                ])
            ], style={'display': 'inline-block', 'width': '45%', 'vertical-align': 'top'})
        ])
    ])

    return fig_returns, fig_volume, ranking_div


__all__ = ['create_sector_page']
