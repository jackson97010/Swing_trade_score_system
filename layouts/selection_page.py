"""
選股評分頁面 - 主要功能頁面
"""

from dash import html, dcc, dash_table, Input, Output, State, callback
import pandas as pd
import numpy as np


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


def calculate_macd(close_series, fast=12, slow=26, signal=9):
    """計算 MACD"""
    ema_fast = close_series.ewm(span=fast, adjust=False).mean()
    ema_slow = close_series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    return macd_line


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
    計算股票評分（使用啟動時快取的資料）
    """
    if not stock_input:
        return None, html.Div("⚠️ 請輸入股票代碼", style={'color': 'orange'})

    try:
        # 解析股票代碼
        stock_codes = [code.strip() for code in stock_input.split(',')]

        # 從 app.py 取得快取資料
        import app
        close = app.CACHED_DATA['close']
        trade_value = app.CACHED_DATA['trade_value']
        revenue_yoy = app.CACHED_DATA['revenue_yoy']
        all_stock_names = app.CACHED_DATA['stock_names']
        industry_df = app.CACHED_DATA['industry_df']

        print(f"📊 計算 {len(stock_codes)} 檔股票評分（使用快取資料）")

        # 目標日期 = 最新交易日
        target_idx = len(close) - 1

        # 計算均線
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()

        # 均線多頭排列: MA10 > MA20 > MA60
        ma_bullish = (ma10.iloc[target_idx] > ma20.iloc[target_idx]) & \
                     (ma20.iloc[target_idx] > ma60.iloc[target_idx])

        # 計算 MACD
        macd_scores = {}
        for stock in stock_codes:
            if stock not in close.columns:
                macd_scores[stock] = False
                continue
            try:
                macd_line = calculate_macd(close[stock])
                macd_today = macd_line.iloc[target_idx]
                macd_yesterday = macd_line.iloc[target_idx - 1]
                macd_scores[stock] = (macd_today > 0 and macd_today > macd_yesterday)
            except:
                macd_scores[stock] = False
        macd_bullish = pd.Series(macd_scores)

        # 營收成長 YoY > 20%
        revenue_latest = revenue_yoy.iloc[:target_idx+1].ffill().iloc[-1]
        revenue_good = revenue_latest > 20

        # 產業趨勢 - 過去10天漲幅前五大族群
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

        # 成交值前30大 (過去10天任一天)
        top30_stocks = set()
        for i in range(max(0, target_idx - 9), target_idx + 1):
            daily_trade = trade_value.iloc[i].dropna().sort_values(ascending=False)
            top30_today = daily_trade.head(30).index.tolist()
            top30_stocks.update(top30_today)

        # 計算評分
        results = []
        for stock in stock_codes:
            if stock not in close.columns:
                results.append({
                    '代碼': stock,
                    '名稱': all_stock_names.get(stock, stock),
                    '總分': 0,
                    '參考價': 0,
                    '成交金額(億)': 0,
                    '月營收YoY%': 0,
                    '評分說明': '無資料'
                })
                continue

            score = 0
            details = []

            # 技術面: 均線多頭 (+20)
            if stock in ma_bullish.index and ma_bullish[stock]:
                score += 20
                details.append("均線多排(+20)")

            # 技術面: MACD (+20)
            if stock in macd_bullish.index and macd_bullish[stock]:
                score += 20
                details.append("MACD強勢(+20)")

            # 基本面: 營收 YoY > 20% (+10)
            if stock in revenue_good.index and revenue_good[stock]:
                score += 10
                details.append("營收強(+10)")

            # 基本面: 熱門族群 (+10)
            if stock in hot_sector_stocks:
                score += 10
                stock_sectors = industry_df[industry_df['代碼'] == stock]['細產業別'].tolist()
                hot_sectors = [s for s in stock_sectors if s in top5_sector_names]
                details.append(f"熱門族群(+10)")

            # 基本面: 成交值前30 (+10)
            if stock in top30_stocks:
                score += 10
                details.append("成交熱絡(+10)")

            # 取得資料
            price = round(close_today.get(stock, 0), 2)
            amount = round(trade_value.iloc[target_idx].get(stock, 0) / 1e8, 2)
            rev_yoy = round(revenue_latest.get(stock, 0), 2) if stock in revenue_latest.index else 0

            results.append({
                '代碼': stock,
                '名稱': all_stock_names.get(stock, stock),
                '總分': score,
                '參考價': price,
                '成交金額(億)': amount,
                '月營收YoY%': rev_yoy,
                '評分說明': ', '.join(details) if details else '無符合條件'
            })

        scores_df = pd.DataFrame(results)
        scores_df = scores_df.sort_values('總分', ascending=False).reset_index(drop=True)

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
        import traceback
        traceback.print_exc()
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
    顯示選中股票的走勢圖（使用 Agent 4 的圖表模組 ✅）
    """
    if not selected_rows or not table_data:
        return {}

    selected_stock = table_data[selected_rows[0]]
    stock_code = selected_stock['代碼']
    stock_name = selected_stock['名稱']

    # 使用 Agent 4 的圖表模組
    try:
        from modules.charts import create_candlestick_chart
        return create_candlestick_chart(stock_code)
    except Exception as e:
        # 如果圖表生成失敗，顯示錯誤訊息
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_annotation(
            text=f"圖表生成失敗: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="red")
        )
        fig.update_layout(
            title=f"{stock_name} ({stock_code}) 走勢圖",
            xaxis_title="日期",
            yaxis_title="價格",
            height=500
        )
        return fig


# 匯出函數
__all__ = ['create_selection_page']
