"""
每日排行榜頁面 - 現代化設計
顯示每個交易日分數前50名
"""

from dash import html, dcc, dash_table, Input, Output, State, callback
import pandas as pd
import numpy as np

from .styles import (
    COLORS, MAIN_STYLES, CARD_STYLES, TABLE_STYLES,
    BUTTON_STYLES, BADGE_STYLES, get_score_badge_style
)


def calculate_macd(close_series, fast=12, slow=26, signal=9):
    """計算 MACD"""
    ema_fast = close_series.ewm(span=fast, adjust=False).mean()
    ema_slow = close_series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    return macd_line


def create_stat_card(value, label, color):
    """建立統計卡片"""
    return html.Div([
        html.Div(str(value), style={
            **CARD_STYLES['stat_number'],
            'color': color,
        }),
        html.Div(label, style=CARD_STYLES['stat_label']),
    ], style=CARD_STYLES['stat'])


def create_ranking_page() -> html.Div:
    """
    建立每日排行榜頁面

    Returns:
        html.Div: 每日排行榜頁面元件
    """
    return html.Div([
        # 頁面標題區
        html.Div([
            html.H1('每日排行榜', style=MAIN_STYLES['page_title']),
            html.P(
                '依據技術面與基本面綜合評分，篩選當日潛力標的',
                style=MAIN_STYLES['page_subtitle']
            )
        ]),

        # 操作區塊
        html.Div([
            # 日期選擇
            html.Div([
                html.Label('選擇交易日', style={
                    'fontSize': '13px',
                    'fontWeight': '500',
                    'color': COLORS['text_secondary'],
                    'marginBottom': '6px',
                    'display': 'block',
                }),
                dcc.DatePickerSingle(
                    id='ranking-date-picker',
                    display_format='YYYY-MM-DD',
                    style={'marginRight': '16px'}
                )
            ], style={'display': 'inline-block', 'verticalAlign': 'bottom'}),

            # 計算按鈕
            html.Button(
                '計算排行榜',
                id='ranking-calculate-btn',
                n_clicks=0,
                style={
                    **BUTTON_STYLES['primary'],
                    'verticalAlign': 'bottom',
                }
            )
        ], style={
            **CARD_STYLES['base'],
            'display': 'flex',
            'alignItems': 'flex-end',
            'gap': '16px',
        }),

        # 統計卡片區
        html.Div(id='ranking-stat-cards', style={
            'display': 'flex',
            'gap': '16px',
            'marginBottom': '24px',
            'flexWrap': 'wrap',
        }),

        # 狀態訊息
        html.Div(id='ranking-status', style={'marginBottom': '16px'}),

        # 排行榜表格卡片
        html.Div([
            html.Div([
                html.Span('📈', style={'fontSize': '18px'}),
                '評分排行榜 TOP 50',
            ], style=CARD_STYLES['title']),
            html.Div(id='ranking-table-container')
        ], style=CARD_STYLES['base'])

    ])


@callback(
    Output('ranking-date-picker', 'date'),
    Output('ranking-date-picker', 'min_date_allowed'),
    Output('ranking-date-picker', 'max_date_allowed'),
    Input('ranking-date-picker', 'id')
)
def init_date_picker(_):
    """初始化日期選擇器"""
    import app
    close = app.CACHED_DATA['close']

    min_date = close.index[60].strftime('%Y-%m-%d')
    max_date = close.index[-1].strftime('%Y-%m-%d')
    default_date = max_date

    return default_date, min_date, max_date


@callback(
    [Output('ranking-table-container', 'children'),
     Output('ranking-status', 'children'),
     Output('ranking-stat-cards', 'children')],
    Input('ranking-calculate-btn', 'n_clicks'),
    State('ranking-date-picker', 'date'),
    prevent_initial_call=True
)
def calculate_ranking(n_clicks, selected_date):
    """計算指定日期的排行榜"""
    if not selected_date:
        return None, html.Div("請選擇日期", style={'color': COLORS['orange']}), []

    try:
        import app
        close = app.CACHED_DATA['close']
        trade_value = app.CACHED_DATA['trade_value']
        revenue_yoy = app.CACHED_DATA['revenue_yoy']
        all_stock_names = app.CACHED_DATA['stock_names']
        industry_df = app.CACHED_DATA['industry_df']

        target_date = pd.to_datetime(selected_date)
        if target_date not in close.index:
            available_dates = close.index[close.index <= target_date]
            if len(available_dates) == 0:
                return None, html.Div(
                    f"找不到 {selected_date} 或之前的資料",
                    style={'color': COLORS['up']}
                ), []
            target_date = available_dates[-1]

        target_idx = close.index.get_loc(target_date)

        # 篩選月均成交值 >= 3億
        lookback = min(20, target_idx + 1)
        avg_trade_value = trade_value.iloc[target_idx - lookback + 1:target_idx + 1].mean()
        valid_stocks = avg_trade_value[avg_trade_value >= 3e8].index.tolist()

        # 計算均線
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()

        ma_bullish = (ma10.iloc[target_idx] > ma20.iloc[target_idx]) & \
                     (ma20.iloc[target_idx] > ma60.iloc[target_idx])

        # 計算 MACD
        macd_scores = {}
        for stock in valid_stocks:
            if stock not in close.columns:
                continue
            try:
                macd_line = calculate_macd(close[stock])
                macd_today = macd_line.iloc[target_idx]
                macd_yesterday = macd_line.iloc[target_idx - 1]
                macd_scores[stock] = (macd_today > 0 and macd_today > macd_yesterday)
            except:
                macd_scores[stock] = False
        macd_bullish = pd.Series(macd_scores)

        # 營收 YoY > 20%
        revenue_latest = revenue_yoy.iloc[:target_idx+1].ffill().iloc[-1]
        revenue_good = revenue_latest > 20

        # 產業趨勢
        close_today = close.iloc[target_idx]
        close_10d_ago = close.iloc[max(0, target_idx - 10)]

        sector_returns = {}
        sector_stocks = {}
        for sector in industry_df['細產業別'].unique():
            stocks_in_sector = industry_df[industry_df['細產業別'] == sector]['代碼'].tolist()
            stocks_in_sector = [s for s in stocks_in_sector if s in close.columns]
            if len(stocks_in_sector) < 2:
                continue
            avg_price_today = close_today[stocks_in_sector].mean()
            avg_price_10d = close_10d_ago[stocks_in_sector].mean()
            if pd.notna(avg_price_today) and pd.notna(avg_price_10d) and avg_price_10d > 0:
                sector_return = (avg_price_today - avg_price_10d) / avg_price_10d * 100
                sector_returns[sector] = sector_return
                sector_stocks[sector] = stocks_in_sector

        top5_sectors = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)[:5]
        top5_sector_names = [s[0] for s in top5_sectors]
        hot_sector_stocks = set()
        for sector in top5_sector_names:
            hot_sector_stocks.update(sector_stocks.get(sector, []))

        # 成交值前30大
        top30_stocks = set()
        for i in range(max(0, target_idx - 9), target_idx + 1):
            daily_trade = trade_value.iloc[i].dropna().sort_values(ascending=False)
            top30_today = daily_trade.head(30).index.tolist()
            top30_stocks.update(top30_today)

        # 計算所有股票評分
        results = []
        for stock in valid_stocks:
            if stock not in close.columns:
                continue

            score = 0
            details = []

            if stock in ma_bullish.index and ma_bullish[stock]:
                score += 20
                details.append("均線多排")

            if stock in macd_bullish.index and macd_bullish[stock]:
                score += 20
                details.append("MACD強勢")

            if stock in revenue_good.index and revenue_good[stock]:
                score += 10
                details.append("營收成長")

            if stock in hot_sector_stocks:
                score += 10
                details.append("熱門族群")

            if stock in top30_stocks:
                score += 10
                details.append("成交熱絡")

            if score > 0:
                price = round(close_today.get(stock, 0), 2)
                amount = round(trade_value.iloc[target_idx].get(stock, 0) / 1e8, 2)

                results.append({
                    '排名': 0,
                    '代碼': stock,
                    '名稱': all_stock_names.get(stock, stock),
                    '總分': score,
                    '收盤價': price,
                    '成交金額(億)': amount,
                    '評分說明': ' / '.join(details)
                })

        # 排序並取前50
        df_result = pd.DataFrame(results)
        df_result = df_result.sort_values('總分', ascending=False).head(50).reset_index(drop=True)
        df_result['排名'] = range(1, len(df_result) + 1)

        # 現代化表格樣式
        table = dash_table.DataTable(
            id='ranking-table',
            columns=[{"name": col, "id": col} for col in df_result.columns],
            data=df_result.to_dict('records'),
            style_table={
                'overflowX': 'auto',
                'borderRadius': '8px',
                'border': 'none',
            },
            style_cell={
                'textAlign': 'left',
                'padding': '14px 16px',
                'fontFamily': '"Noto Sans TC", "Inter", -apple-system, sans-serif',
                'fontSize': '14px',
                'border': 'none',
                'borderBottom': f'1px solid {COLORS["border_light"]}',
                'backgroundColor': COLORS['bg_card'],
            },
            style_header={
                'backgroundColor': COLORS['bg_input'],
                'color': COLORS['text_primary'],
                'fontWeight': '600',
                'fontSize': '13px',
                'borderBottom': f'2px solid {COLORS["border"]}',
                'border': 'none',
            },
            style_data={
                'backgroundColor': COLORS['bg_card'],
                'color': COLORS['text_primary'],
            },
            style_cell_conditional=[
                {'if': {'column_id': '排名'}, 'width': '60px', 'textAlign': 'center', 'fontWeight': '600', 'color': COLORS['accent']},
                {'if': {'column_id': '代碼'}, 'width': '80px', 'fontWeight': '600'},
                {'if': {'column_id': '名稱'}, 'width': '100px'},
                {'if': {'column_id': '總分'}, 'width': '80px', 'textAlign': 'center'},
                {'if': {'column_id': '收盤價'}, 'width': '100px', 'textAlign': 'right'},
                {'if': {'column_id': '成交金額(億)'}, 'width': '110px', 'textAlign': 'right'},
                {'if': {'column_id': '評分說明'}, 'color': COLORS['text_secondary'], 'fontSize': '13px'},
            ],
            style_data_conditional=[
                # 滿分 70 分
                {
                    'if': {'filter_query': '{總分} = 70', 'column_id': '總分'},
                    'backgroundColor': COLORS['up_bg'],
                    'color': COLORS['up'],
                    'fontWeight': '700',
                    'borderRadius': '4px',
                },
                # 60 分以上
                {
                    'if': {'filter_query': '{總分} >= 60 && {總分} < 70', 'column_id': '總分'},
                    'backgroundColor': '#EFF6FF',
                    'color': COLORS['accent_dark'],
                    'fontWeight': '600',
                },
                # 50 分以上
                {
                    'if': {'filter_query': '{總分} >= 50 && {總分} < 60', 'column_id': '總分'},
                    'backgroundColor': COLORS['purple_bg'],
                    'color': COLORS['purple'],
                    'fontWeight': '600',
                },
                # Hover 效果 (選中行)
                {
                    'if': {'state': 'selected'},
                    'backgroundColor': COLORS['bg_page'],
                    'border': 'none',
                },
            ],
            page_size=50,
            style_as_list_view=True,  # 移除垂直線
        )

        # 統計資訊
        full_score = len(df_result[df_result['總分'] == 70])
        score_60_plus = len(df_result[df_result['總分'] >= 60])
        score_50_plus = len(df_result[df_result['總分'] >= 50])
        total_scored = len(results)

        stat_cards = [
            create_stat_card(full_score, '滿分 (70分)', COLORS['up']),
            create_stat_card(score_60_plus, '60分以上', COLORS['accent']),
            create_stat_card(score_50_plus, '50分以上', COLORS['purple']),
            create_stat_card(total_scored, '總評分股票', COLORS['text_secondary']),
        ]

        status = html.Div([
            html.Span(
                f"{target_date.strftime('%Y-%m-%d')} 排行榜計算完成",
                style={
                    'color': COLORS['down'],
                    'fontWeight': '500',
                    'fontSize': '14px',
                }
            ),
        ])

        return table, status, stat_cards

    except Exception as e:
        import traceback
        traceback.print_exc()
        return None, html.Div(
            f"計算失敗: {str(e)}",
            style={'color': COLORS['up']}
        ), []


__all__ = ['create_ranking_page']
