"""
族群熱力圖頁面 - 顯示族群每日漲跌幅熱力圖
全屏設計，讓熱力圖充滿整個頁面
"""

from dash import html, dcc, Input, Output, callback
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from .styles import COLORS, MAIN_STYLES, CARD_STYLES, BUTTON_STYLES


def create_sector_page() -> html.Div:
    """
    建立族群熱力圖頁面 - 全屏設計

    Returns:
        html.Div: 族群熱力圖頁面元件
    """
    return html.Div([
        # 頂部控制列
        html.Div([
            # 標題
            html.Div([
                html.Span('🔥', style={'fontSize': '24px', 'marginRight': '12px'}),
                html.Span('族群熱力圖', style={
                    'fontSize': '20px',
                    'fontWeight': '600',
                    'color': COLORS['text_primary'],
                }),
            ], style={'display': 'flex', 'alignItems': 'center'}),

            # 控制項
            html.Div([
                # 顯示天數
                html.Div([
                    html.Label('顯示天數', style={
                        'fontSize': '13px',
                        'color': COLORS['text_secondary'],
                        'marginRight': '8px',
                    }),
                    dcc.Input(
                        id='sector-days-input',
                        type='number',
                        value=20,
                        min=5,
                        max=60,
                        style={
                            'width': '70px',
                            'padding': '8px 12px',
                            'borderRadius': '8px',
                            'border': f'1px solid {COLORS["border"]}',
                            'fontSize': '14px',
                        }
                    ),
                    html.Span('天', style={
                        'marginLeft': '4px',
                        'color': COLORS['text_secondary'],
                        'fontSize': '13px',
                    }),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '24px'}),

                # 顯示族群數
                html.Div([
                    html.Label('顯示族群數', style={
                        'fontSize': '13px',
                        'color': COLORS['text_secondary'],
                        'marginRight': '8px',
                    }),
                    dcc.Input(
                        id='sector-count-input',
                        type='number',
                        value=20,
                        min=10,
                        max=50,
                        style={
                            'width': '70px',
                            'padding': '8px 12px',
                            'borderRadius': '8px',
                            'border': f'1px solid {COLORS["border"]}',
                            'fontSize': '14px',
                        }
                    ),
                    html.Span('個', style={
                        'marginLeft': '4px',
                        'color': COLORS['text_secondary'],
                        'fontSize': '13px',
                    }),
                ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '24px'}),

                # 更新按鈕
                html.Button(
                    [
                        html.Span('🔄', style={'marginRight': '6px'}),
                        '更新圖表',
                    ],
                    id='sector-refresh-btn',
                    n_clicks=0,
                    style={
                        **BUTTON_STYLES['primary'],
                        'display': 'flex',
                        'alignItems': 'center',
                    }
                ),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ], style={
            **CARD_STYLES['base'],
            'display': 'flex',
            'justifyContent': 'space-between',
            'alignItems': 'center',
            'padding': '16px 24px',
            'marginBottom': '16px',
        }),

        # 熱力圖卡片 - 全屏設計
        html.Div([
            # 標題列
            html.Div([
                html.Div([
                    html.Span('📈', style={'fontSize': '18px', 'marginRight': '8px'}),
                    html.Span('族群每日漲跌幅', style={
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'color': COLORS['text_primary'],
                    }),
                ], style={'display': 'flex', 'alignItems': 'center'}),

                html.Span('紅色 = 上漲 / 綠色 = 下跌（台股配色）', style={
                    'fontSize': '12px',
                    'color': COLORS['text_secondary'],
                }),
            ], style={
                'display': 'flex',
                'justifyContent': 'space-between',
                'alignItems': 'center',
                'marginBottom': '16px',
            }),

            # 熱力圖 - 充滿頁面
            dcc.Loading(
                dcc.Graph(
                    id='sector-returns-heatmap',
                    style={'height': 'calc(100vh - 280px)', 'width': '100%'},
                    config={
                        'displayModeBar': True,
                        'displaylogo': False,
                        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
                    }
                ),
                type='circle',
                color=COLORS['accent'],
            ),
        ], style={
            **CARD_STYLES['base'],
            'padding': '20px',
            'marginBottom': '0',
            'height': 'calc(100vh - 180px)',
            'display': 'flex',
            'flexDirection': 'column',
        }),

    ], style={
        'padding': '0',
        'height': 'calc(100vh - 48px)',
        'display': 'flex',
        'flexDirection': 'column',
    })


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


@callback(
    Output('sector-returns-heatmap', 'figure'),
    [Input('sector-refresh-btn', 'n_clicks'),
     Input('sector-days-input', 'value'),
     Input('sector-count-input', 'value')]
)
def update_sector_heatmap(n_clicks, days, top_n):
    """更新熱力圖"""
    import app
    close = app.CACHED_DATA['close']
    industry_df = app.CACHED_DATA['industry_df']

    # 預設值
    days = days or 20
    top_n = top_n or 20

    # 計算族群漲跌幅
    sector_returns = calculate_sector_returns(close, industry_df)

    # 取最近 N 天
    returns_recent = sector_returns.tail(days)

    # 依波動度排序選取前 N 個族群
    avg_abs_returns = returns_recent.abs().mean().sort_values(ascending=False)
    top_sectors = avg_abs_returns.head(top_n).index.tolist()

    # 漲跌幅熱力圖
    returns_plot = returns_recent[top_sectors] * 100  # 轉換為百分比

    # 台股配色：紅色=上漲，綠色=下跌
    fig = go.Figure(data=go.Heatmap(
        z=returns_plot.T.values,
        x=[d.strftime('%m/%d') for d in returns_plot.index],
        y=returns_plot.columns.tolist(),
        colorscale=[
            [0, '#10B981'],      # 翠綠（大跌）
            [0.35, '#6EE7B7'],   # 淺綠（小跌）
            [0.5, '#FFFFFF'],    # 白色（平盤）
            [0.65, '#FCA5A5'],   # 淺紅（小漲）
            [1, '#EF4444']       # 紅色（大漲）
        ],
        zmid=0,
        zmin=-5,
        zmax=5,
        text=np.round(returns_plot.T.values, 2),
        texttemplate='%{text}',
        textfont={'size': 10, 'color': '#374151'},
        hovertemplate='<b>%{y}</b><br>日期: %{x}<br>漲跌幅: %{z:.2f}%<extra></extra>',
        colorbar=dict(
            title=dict(text='漲跌幅(%)', font=dict(size=12)),
            thickness=15,
            len=0.6,
            tickfont=dict(size=10),
        ),
        xgap=1,
        ygap=1,
    ))

    fig.update_layout(
        title=dict(
            text=f'族群每日漲跌幅熱力圖（最近 {days} 天）',
            font=dict(size=16, color=COLORS['text_primary']),
            x=0,
            xanchor='left',
        ),
        xaxis=dict(
            title='',
            tickfont=dict(size=11),
            side='top',
            tickangle=0,
        ),
        yaxis=dict(
            title='',
            tickfont=dict(size=12),
            autorange='reversed',  # 讓排名高的在上面
        ),
        margin=dict(l=140, r=60, t=60, b=20),
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family='"Noto Sans TC", "Inter", sans-serif',
        ),
    )

    return fig


__all__ = ['create_sector_page']
