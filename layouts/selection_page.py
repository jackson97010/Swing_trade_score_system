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

        # 使用真實資料（Agent 2 完成 ✅）
        from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators, load_industry_data, calculate_industry_trend, get_top_industries
        from modules.scoring import calculate_batch_scores

        # 取得資料
        stock_data = fetch_stock_data(stock_codes)
        if stock_data is None:
            return None, html.Div("❌ 無法取得股票資料", style={'color': 'red'})

        tech_indicators = calculate_technical_indicators(stock_data['close'])

        # 計算產業趨勢
        industry_df = load_industry_data()
        industry_trend = calculate_industry_trend(stock_data['close'], industry_df)
        top_industries = get_top_industries(industry_trend)

        # 計算評分
        score_results = calculate_batch_scores(stock_codes, stock_data, tech_indicators, industry_df, top_industries)

        # 組合完整的表格資料（使用真實股票名稱）
        scores_df = pd.DataFrame({
            '代碼': score_results['stock_code'],
            '名稱': [stock_data['stock_names'].get(code, code) for code in score_results['stock_code']],
            '總分': score_results['total_score'],
            '參考價': [round(stock_data['close'][code].iloc[-1], 2) if code in stock_data['close'].columns else 0
                       for code in score_results['stock_code']],
            '成交金額(億)': [round(stock_data['amount'][code].iloc[-1] / 100000000, 2) if code in stock_data['amount'].columns else 0
                          for code in score_results['stock_code']],
            '月營收YoY%': [round(stock_data['revenue_yoy'][code].iloc[-1], 2) if code in stock_data['revenue_yoy'].columns and not pd.isna(stock_data['revenue_yoy'][code].iloc[-1]) else 0
                        for code in score_results['stock_code']],
            'EPS(季)': [round(stock_data['eps'][code].iloc[-1], 2) if code in stock_data['eps'].columns and not pd.isna(stock_data['eps'][code].iloc[-1]) else 0
                    for code in score_results['stock_code']],
            '評分說明': score_results['details']
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
