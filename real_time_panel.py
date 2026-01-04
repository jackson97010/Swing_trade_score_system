import redis
import threading
import math
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import dash
from dash import Dash, dcc, html, ctx, State
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
from collections import defaultdict
import os
import json # 用來處理 Store 資料

from finlab import data, login
from finlab.markets.tw import TWMarket
from finlab.dataframe import FinlabDataFrame
#finlab token 
login('Y8qx8Zs1zTnNk7McQPGpR4Lb9jv29EMQpiOMAxyBpmcIK4mYc2vODIvD8PuXLctw')

def get_tick(price: float) -> float:
    if price < 10:
        return 0.01
    elif price < 50:
        return 0.05
    elif price < 100:
        return 0.1
    elif price < 500:
        return 0.5
    elif price < 1000:
        return 1.0
    else:
        return 5.0

def limit_up_price(today_price: float, factor=1.1) -> float:
    if today_price>0:
        limit_up = today_price * factor
        tick = get_tick(limit_up)
        # 向下取整至 tick 的倍數
        adjusted = math.floor(limit_up / tick) * tick if factor>1 else math.ceil(limit_up / tick) * tick
        return round(adjusted, 2)
    return today_price

REDIS_HOST = '192.168.100.130'

LOG_DIR = "D:/pub_sub_data"  # <--- 設定 Log 路徑

# (原本的 Finlab 資料撈取邏輯保持不變)
data.set_universe('TSE_OTC')
data.truncate_start = (datetime.now()-timedelta(days=14)).strftime('%Y-%m-%d')

close = data.get('price:收盤價')
vol = data.get('price:成交股數')/1000
stock_trades = data.get('price:成交金額')

CHANNELS = list(vol.columns)

yesterday_limit_up_price = close.shift(1).map(limit_up_price)
limited_up = yesterday_limit_up_price==close
YESTERDAY_CLOSE = close[vol.gt(500)|stock_trades.gt(3*10**8)].iloc[-1].dropna()
TARGET_STOCKS = YESTERDAY_CLOSE.index

cats_df = pd.read_csv('stock_category.csv')
cats_df['代碼'] = cats_df['代碼'].astype(str)

cats_df = cats_df.query('代碼 in @TARGET_STOCKS')

mask = cats_df.groupby("細產業別")["代碼"].transform("nunique") > 2
cats_df = cats_df[mask]

selected_show = YESTERDAY_CLOSE.index
STOCK_CATEGORIES = cats_df.query('代碼 in @selected_show')[['代碼','細產業別']].drop_duplicates().groupby(['代碼'])['細產業別'].agg(list).to_dict()
STOCK_CATEGORIES = defaultdict(lambda: [], STOCK_CATEGORIES)

for s in limited_up[limited_up&(vol.gt(500)|stock_trades.gt(2*10**8))].iloc[-1].dropna().index:
    STOCK_CATEGORIES[s].append('前日漲停')

TWM = TWMarket()
STOCK_NAME = TWM.get_asset_id_to_name()


LIMITED_UP_PRICE = close.map(limit_up_price).iloc[-1]
LIMITED_DOWN_PRICE = close.map(lambda x: limit_up_price(x, 0.9)).iloc[-1]



def get_label(symbol):
    name = STOCK_NAME.get(symbol, '')
    return f"{symbol} {name}" if name else symbol

CATEGORY_TO_STOCKS = {}
for stock, categories in STOCK_CATEGORIES.items():
    for cat in categories:
        if cat not in CATEGORY_TO_STOCKS: 
            CATEGORY_TO_STOCKS[cat] = []
        CATEGORY_TO_STOCKS[cat].append(stock)

sorted_categories = sorted(list(CATEGORY_TO_STOCKS.keys()))
default_category = sorted_categories[0] if sorted_categories else "無類別"

# 全市場股票列表
all_stocks_list = sorted(list(set(TARGET_STOCKS) | set(STOCK_CATEGORIES.keys())))
all_stocks_set = set(all_stocks_list)

def parse_time_str_varlen(t):
    s = str(t).strip()
    if len(s) <= 6: return None
    prefix = s[:-6].zfill(6)
    return f"{prefix[0:2]}:{prefix[2:4]}"

# ==========================================
# 2. 全域資料管理
# ==========================================
class DataStore:
    def __init__(self):
        self.lock = threading.Lock()
        self.raw_data = {}
        self.df_trend = pd.DataFrame()
        self.df_treemap = pd.DataFrame()
        self.last_update = datetime.now()

    def update_raw(self, symbol, time_str, price, volume):
        if symbol not in self.raw_data:
            self.raw_data[symbol] = {
                'history': [], 'latest': None, 'snapshot': {'volume': 0, 'price': 0}
            }
        
        stock_data = self.raw_data[symbol]
        stock_data['snapshot']['price'] = price
        stock_data['snapshot']['volume'] += volume

        latest = stock_data['latest']
        if latest and latest['ts'] != time_str:
            stock_data['history'].append(latest.copy())
            if len(stock_data['history']) > 600: 
                stock_data['history'] = stock_data['history'][-600:] 
            latest = None

        if latest is None:
            stock_data['latest'] = {'ts': time_str, 'close': price}
        else:
            stock_data['latest']['close'] = price

    def process_dataframes(self):
        try:
            current_data = list(self.raw_data.items())
        except RuntimeError:
            return

        if not current_data: return

        # 1. Treemap Data
        tm_records = []
        for stock, data in current_data:
            snap = data.get('snapshot')
            if not snap or snap['volume'] == 0: continue
            
            cat_list = STOCK_CATEGORIES.get(stock, []) 
            
            current_price = snap['price']
            ref_price = YESTERDAY_CLOSE.get(stock, current_price)
            pct = (current_price - ref_price) / ref_price * 100 if ref_price else 0
            display_name = get_label(stock)

            for cat in cat_list:
                tm_records.append({
                    'category2': cat, 'symbol': stock, 'display_name': display_name, 
                    'pct': pct, 'volume': snap['volume']
                })
        
        if tm_records:
            new_df_treemap = pd.DataFrame(tm_records)
        else:
            new_df_treemap = pd.DataFrame(columns=['category2', 'symbol', 'display_name', 'pct', 'volume'])

        # 2. Trend Data
        trend_records = []
        for stock, data in current_data:
            rows = data['history'].copy()
            if data['latest']: rows.append(data['latest'])
            for row in rows:
                trend_records.append({'time': row['ts'], 'stock': stock, 'close': row['close']})
        
        if trend_records:
            df = pd.DataFrame(trend_records)
            df = df.drop_duplicates(subset=['time', 'stock'], keep='last')
            new_df_trend = df.pivot(index='time', columns='stock', values='close').sort_index()
            if not new_df_trend.empty: 
                new_df_trend = new_df_trend.ffill()
        else:
            new_df_trend = pd.DataFrame()

        with self.lock:
            self.df_treemap = new_df_treemap
            self.df_trend = new_df_trend
            self.last_update = datetime.now()

store = DataStore()

# ==========================================
# 3. 資料處理與載入
# ==========================================

def process_line_data(line):
    try:
        parts = [x.strip() for x in line.split(',')]
        if len(parts) < 6: return
        if parts[0].lower() != 'trade': return
        if int(parts[3]) == 1: return 
        
        symbol = parts[1]
        if symbol not in all_stocks_set: return 

        time_str = parse_time_str_varlen(parts[2])
        if not time_str: return
        
        price = float(parts[4]) / 10000.0
        volume = int(parts[5])
        
        store.update_raw(symbol, time_str, price, volume)
    except Exception:
        pass

def preload_data_from_logs():
    print(f"📥 開始從 {LOG_DIR} 載入歷史 Log...")
    start_time = time.time()
    count = 0
    target_stocks = all_stocks_list
    
    for stock in target_stocks:
        file_path = os.path.join(LOG_DIR, f"{stock}.log")
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line in f:
                        process_line_data(line)
                        count += 1
            except Exception as e:
                print(f"Error reading {stock}.log: {e}")
                
    store.process_dataframes()
    print(f"✅ 歷史資料載入完成! 處理了 {count} 筆資料，耗時 {time.time()-start_time:.2f} 秒")

# ==========================================
# 4. 背景執行緒
# ==========================================
def redis_worker():
    try:
        r = redis.Redis(host=REDIS_HOST, port=6379, db=0, socket_timeout=5)
        p = r.pubsub(ignore_subscribe_messages=True)
        p.subscribe(all_stocks_list)
    except Exception as e:
        print(f"❌ Redis 連線失敗: {e}")
        return

    print("📡 Redis 監聽啟動中...")
    for message in p.listen():
        if message['type'] != 'message': continue
        try:
            line = message['data'].decode('utf-8', errors='ignore')
            process_line_data(line)
        except Exception:
            continue

def processing_worker():
    while True:
        try:
            store.process_dataframes()
        except Exception as e:
            print(f"Processing Error: {e}")
        time.sleep(2)

# 啟動流程
preload_data_from_logs()
t1 = threading.Thread(target=redis_worker, daemon=True)
t1.start()
t2 = threading.Thread(target=processing_worker, daemon=True)
t2.start()

# ==========================================
# 5. Dash App Layout
# ==========================================
app = Dash(__name__)

# 自定義樣式：彈出視窗 (Modal)
modal_style = {
    'position': 'fixed', 'zIndex': '1050', 'left': '0', 'top': '0', 'width': '100%', 'height': '100%',
    'overflow': 'auto', 'backgroundColor': 'rgba(0,0,0,0.4)', 'display': 'none',
    'justifyContent': 'center', 'alignItems': 'center'
}
modal_content_style = {
    'backgroundColor': '#fefefe', 'margin': '10% auto', 'padding': '20px', 'border': '1px solid #888',
    'width': '500px', 'borderRadius': '8px', 'boxShadow': '0 4px 8px 0 rgba(0,0,0,0.2)'
}

app.layout = html.Div([
    dcc.Store(id='custom-groups-store', storage_type='local'), 
    
    # 🔥 Modal 改版
    html.Div(id='group-modal', style=modal_style, children=[
        html.Div(style=modal_content_style, children=[
            html.H3("🛠️ 管理自訂族群", style={'marginTop': 0}),
            
            # 🔥 新增: 載入現有族群下拉選單
            html.Label("📂 編輯現有族群 (若要新增請留空):", style={'color': '#666', 'fontWeight': 'bold'}),
            dcc.Dropdown(id='modal-group-select', placeholder="選擇要載入的族群...", style={'marginBottom': '15px'}),
            
            html.Hr(style={'margin': '20px 0'}),
            
            html.Label("族群名稱:", style={'fontWeight': 'bold'}),
            dcc.Input(id='new-group-name', type='text', placeholder="例如: 我的AI概念股", style={'width': '100%', 'marginBottom': '10px', 'padding': '5px'}),
            
            html.Label("選擇成分股:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='new-group-stocks',
                options=[{'label': get_label(s), 'value': s} for s in all_stocks_list],
                multi=True, placeholder="搜尋並加入股票...", style={'marginBottom': '20px'}
            ),
            
            html.Div([
                html.Button('💾 儲存/更新', id='btn-save-group', n_clicks=0, style={'backgroundColor': '#28a745', 'color': 'white', 'padding': '8px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'marginRight': '10px'}),
                html.Button('🗑️ 刪除此族群', id='btn-delete-group', n_clicks=0, style={'backgroundColor': '#dc3545', 'color': 'white', 'padding': '8px 15px', 'border': 'none', 'borderRadius': '4px', 'cursor': 'pointer', 'marginRight': 'auto'}),
                html.Button('關閉', id='btn-close-modal', n_clicks=0, style={'padding': '8px 15px', 'cursor': 'pointer'})
            ], style={'display': 'flex', 'justifyContent': 'flex-end'})
        ])
    ]),

    # Header
    html.Div([
        html.H2("全市場即時戰情室", style={'margin': '0 20px 0 0', 'fontSize': '24px'}),
        
        html.Div([
            html.Label("族群:", style={'fontWeight': 'bold', 'marginRight': '5px'}),
            dcc.Dropdown(
                id='category-dropdown',
                options=[], 
                value=default_category, clearable=False, style={'width': '180px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '10px'}),

        html.Button("⚙️", id='btn-open-modal', n_clicks=0, 
                   title="管理自訂族群",
                   style={'marginRight': '10px', 'cursor': 'pointer', 'fontSize': '16px', 'padding': '5px 10px'}),

        html.Button("⛶", id='btn-toggle-view', n_clicks=0, 
                   title="專注模式 (隱藏右側)",
                   style={'marginRight': '20px', 'cursor': 'pointer', 'fontSize': '16px', 'padding': '5px 10px'}),

        html.Div([
            html.Label("反查:", style={'fontWeight': 'bold', 'marginRight': '5px', 'color': '#d62728'}),
            dcc.Dropdown(
                id='stock-search-dropdown',
                options=[{'label': get_label(s), 'value': s} for s in all_stocks_list],
                value=None, placeholder="輸入代號跳轉...", style={'width': '160px'}
            ),
            dcc.RadioItems(
                id='multi-category-selector', options=[], value=None, inline=True,
                style={'marginLeft': '10px', 'fontSize': '14px', 'display': 'none'},
                labelStyle={'marginRight': '10px', 'fontWeight': 'bold', 'cursor': 'pointer'}
            )
        ], style={'display': 'flex', 'alignItems': 'center', 'marginRight': '15px'}),

        html.Div([
            html.Label("疊加:", style={'fontWeight': 'bold', 'marginRight': '5px', 'color': '#007bff'}),
            dcc.Dropdown(
                id='focus-dropdown',
                options=[{'label': get_label(s), 'value': s} for s in all_stocks_list],
                value=[], multi=True, placeholder="疊加比較...", style={'width': '200px'}
            )
        ], style={'display': 'flex', 'alignItems': 'center'})

    ], style={'flex': '0 0 60px', 'display': 'flex', 'alignItems': 'center', 'padding': '10px', 'background': '#f8f9fa', 'borderBottom': '1px solid #ddd'}),

    # Content
    html.Div([
        # Left
        html.Div(id='left-container', children=[
            dcc.Graph(id='main-graph', style={'height': '100%', 'width': '100%'}, responsive=True, config={'displayModeBar': False})
        ], style={'flex': '55', 'borderRight': '1px solid #ddd', 'position': 'relative', 'minWidth': '0', 'transition': 'all 0.3s'}),

        # Right
        html.Div(id='right-container', children=[
            # TreeMap
            html.Div([
                html.Div([
                    html.H4("板塊熱力圖", style={'margin': 0, 'fontSize': '16px'}),
                    dcc.RadioItems(
                        id='treemap-scope',
                        options=[
                            {'label': '全市場', 'value': 'all'},
                            {'label': '鎖定族群', 'value': 'focus'},
                        ],
                        value='all', 
                        inline=True,
                        style={'fontSize': '14px', 'marginLeft': '15px'},
                        labelStyle={'marginRight': '10px', 'cursor': 'pointer'}
                    )
                ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'padding': '5px 0'}),
                
                dcc.Graph(id='live-treemap', style={'height': 'calc(100% - 35px)', 'width': '100%'}, responsive=True, clickData=None, config={'displayModeBar': False})
            ], style={'height': '50%', 'borderBottom': '1px solid #ddd', 'display': 'flex', 'flexDirection': 'column', 'minHeight': '0'}),

            # Pie & Bar
            html.Div([
                html.Div([
                    dcc.Graph(id='pie-graph', style={'height': '100%', 'width': '100%'}, responsive=True, config={'displayModeBar': False})
                ], style={'flex': '4', 'borderRight': '1px solid #ddd', 'position': 'relative', 'minWidth': '0'}),
                html.Div([
                    dcc.Graph(id='bar-graph', style={'width': '100%'}, responsive=True, config={'displayModeBar': False})
                ], style={'flex': '6', 'overflowY': 'auto', 'position': 'relative', 'minWidth': '0'})
            ], style={'height': '50%', 'display': 'flex', 'flexDirection': 'row', 'overflow': 'hidden', 'minHeight': '0'})

        ], style={'flex': '45', 'display': 'flex', 'flexDirection': 'column', 'minWidth': '0', 'transition': 'all 0.3s'})

    ], style={'flex': '1', 'display': 'flex', 'overflow': 'hidden'}),

    dcc.Interval(id='interval-component', interval=2000, n_intervals=0)

], style={'display': 'flex', 'flexDirection': 'column', 'height': '100vh', 'width': '100vw', 'margin': 0, 'fontFamily': 'Arial'})

# ==========================================
# 6. Callbacks
# ==========================================

# 1. 視圖切換
@app.callback(
    [Output('left-container', 'style'),
     Output('right-container', 'style'),
     Output('btn-toggle-view', 'style')],
    Input('btn-toggle-view', 'n_clicks'),
    State('btn-toggle-view', 'style')
)
def toggle_view(n, current_btn_style):
    default_left = {'flex': '55', 'borderRight': '1px solid #ddd', 'position': 'relative', 'minWidth': '0', 'transition': 'all 0.3s'}
    default_right = {'flex': '45', 'display': 'flex', 'flexDirection': 'column', 'minWidth': '0', 'transition': 'all 0.3s'}
    btn_style = current_btn_style or {}
    
    if n % 2 == 1:
        new_left = {'flex': '1', 'width': '100%', 'height': '100%', 'position': 'relative', 'minWidth': '0', 'transition': 'all 0.3s'}
        new_right = {'display': 'none'}
        btn_style['backgroundColor'] = '#ccc' 
    else:
        new_left = default_left
        new_right = default_right
        btn_style['backgroundColor'] = ''
    return new_left, new_right, btn_style

# 🔥 2. 自訂族群管理 (管理儲存/刪除/開關)
@app.callback(
    [Output('group-modal', 'style'),
     Output('custom-groups-store', 'data')],
    [Input('btn-open-modal', 'n_clicks'),
     Input('btn-close-modal', 'n_clicks'),
     Input('btn-save-group', 'n_clicks'),
     Input('btn-delete-group', 'n_clicks')],
    [State('group-modal', 'style'),
     State('custom-groups-store', 'data'),
     State('new-group-name', 'value'),
     State('new-group-stocks', 'value')],
    prevent_initial_call=True
)
def manage_modal_actions(btn_open, btn_close, btn_save, btn_delete, 
                         modal_style_state, current_store, name_val, stocks_val):
    
    ctx_id = ctx.triggered_id
    current_store = current_store or {}
    
    if ctx_id == 'btn-open-modal':
        new_style = modal_style_state.copy()
        new_style['display'] = 'flex'
        return new_style, dash.no_update
    
    elif ctx_id == 'btn-close-modal':
        new_style = modal_style_state.copy()
        new_style['display'] = 'none'
        return new_style, dash.no_update

    elif ctx_id == 'btn-save-group':
        if name_val and stocks_val:
            current_store[name_val] = stocks_val
            new_style = modal_style_state.copy()
            new_style['display'] = 'none' # 存完關閉
            return new_style, current_store
    
    elif ctx_id == 'btn-delete-group':
        if name_val in current_store:
            del current_store[name_val]
            new_style = modal_style_state.copy()
            new_style['display'] = 'none' # 刪完關閉
            return new_style, current_store

    return dash.no_update, dash.no_update

# 🔥 3. 處理「載入現有族群」邏輯 (自動填入表單)
@app.callback(
    [Output('new-group-name', 'value'),
     Output('new-group-stocks', 'value'),
     Output('modal-group-select', 'value')], # 刪除後要清空選擇
    [Input('modal-group-select', 'value'),
     Input('btn-open-modal', 'n_clicks'),  # 打開視窗時重置
     Input('btn-delete-group', 'n_clicks')], # 刪除後重置
    State('custom-groups-store', 'data')
)
def sync_form_inputs(selected_group, btn_open, btn_delete, current_store):
    trigger = ctx.triggered_id
    current_store = current_store or {}
    
    # 1. 如果是選擇了某個族群 -> 載入資料
    if trigger == 'modal-group-select' and selected_group:
        if selected_group in current_store:
            return selected_group, current_store[selected_group], dash.no_update
    
    # 2. 如果是打開視窗、刪除、或選擇了空白 -> 清空表單
    return "", [], None

# 🔥 4. 更新「載入選單」與「主畫面族群選單」
@app.callback(
    [Output('category-dropdown', 'options'),
     Output('modal-group-select', 'options')],
    Input('custom-groups-store', 'data')
)
def update_all_dropdowns(custom_data):
    # 內建族群
    base_options = [{'label': cat, 'value': cat} for cat in sorted_categories]
    
    # 自訂族群
    custom_options = []
    modal_options = [] # Modal 裡的選單只要自訂的
    
    if custom_data:
        for name in custom_data.keys():
            custom_options.append({'label': f"★ {name}", 'value': name})
            modal_options.append({'label': name, 'value': name})
            
    # 主選單: 自訂 + 內建
    # Modal選單: 只有自訂
    return (custom_options + base_options), modal_options

# 5. 反查連動
@app.callback(
    [Output('multi-category-selector', 'options'),
     Output('multi-category-selector', 'value'),
     Output('multi-category-selector', 'style')],
    Input('stock-search-dropdown', 'value')
)
def update_search_selector(stock):
    if not stock: return [], None, {'display': 'none'}
    cats = STOCK_CATEGORIES.get(stock, [])
    if not cats: return [], None, {'display': 'none'}
    options = [{'label': c, 'value': c} for c in cats]
    style = {'marginLeft': '10px', 'fontSize': '14px', 'display': 'flex'} if len(cats) > 1 else {'display': 'none'}
    return options, cats[0], style

# 6. 熱力圖點擊連動
@app.callback(
    Output('category-dropdown', 'value'),
    [Input('live-treemap', 'clickData'), 
     Input('multi-category-selector', 'value')],
    prevent_initial_call=True
)
def update_main_category(clickData, selector_value):
    trigger_id = ctx.triggered_id
    if trigger_id == 'multi-category-selector' and selector_value:
        return selector_value
    if trigger_id == 'live-treemap' and clickData:
        point = clickData['points'][0]
        label = point.get('label')
        parent = point.get('parent')
        if label in sorted_categories: return label
        if parent in sorted_categories: return parent
    return dash.no_update

# --- 核心繪圖邏輯 ---
@app.callback(
    [Output('main-graph', 'figure'),
     Output('live-treemap', 'figure'),
     Output('pie-graph', 'figure'),
     Output('bar-graph', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('category-dropdown', 'value'),
     Input('focus-dropdown', 'value'),
     Input('treemap-scope', 'value'),
     Input('custom-groups-store', 'data')]
)
def update_charts(n, selected_category, selected_focus, treemap_scope, custom_groups):
    
    empty_fig = go.Figure(layout=dict(title="Waiting for data...", xaxis={'visible':False}, yaxis={'visible':False}))

    with store.lock:
        df_tree = store.df_treemap.copy()
        df_trend = store.df_trend.copy()
        
    custom_groups = custom_groups or {}
    
    # 建立成交量查詢表
    vol_map = {}
    if not df_tree.empty:
        vol_map = df_tree.drop_duplicates('symbol').set_index('symbol')['volume'].to_dict()

    # --- 判斷目前選的族群 ---
    is_custom = selected_category in custom_groups
    
    if is_custom:
        category_stocks = custom_groups[selected_category]
        filter_stocks = category_stocks
    else:
        category_stocks = CATEGORY_TO_STOCKS.get(selected_category, [])
        filter_stocks = None 

    # 1. Treemap (保持不變)
    if df_tree.empty:
        fig_tree = empty_fig
    else:
        if treemap_scope == 'focus':
            if is_custom:
                df_tree_filtered = df_tree[df_tree['symbol'].isin(filter_stocks)]
            elif selected_category in sorted_categories:
                df_tree_filtered = df_tree[df_tree['category2'] == selected_category]
            else:
                df_tree_filtered = df_tree
        else:
            df_tree_filtered = df_tree 

        if df_tree_filtered.empty:
            fig_tree = empty_fig
        else:
            try:
                path = ['symbol', 'display_name'] if is_custom and treemap_scope == 'focus' else ['category2', 'display_name']
                fig_tree = px.treemap(
                    df_tree_filtered, 
                    path=path, 
                    values='volume',              
                    color='pct', color_continuous_scale='RdYlGn_r', range_color=[-5, 5],
                    custom_data=['pct']
                )
                colors = [(0, "green"), (0.5, "white"), (1, "red")]
                fig_tree.update_layout(coloraxis_colorscale=colors, margin=dict(t=0, l=0, r=0, b=0), uirevision='constant')
                fig_tree.update_traces(
                    texttemplate="%{label}<br>%{customdata[0]:.2f}%",
                    hovertemplate='<b>%{label}</b><br>Change: %{customdata[0]:.2f}%<br>Vol: %{value}',
                    textposition="middle center", textfont=dict(size=14, color='black')
                )
            except Exception as e:
                fig_tree = empty_fig

    # 2. Trend Chart
    user_picks = selected_focus if selected_focus else []
    target_stocks = list(set(category_stocks + user_picks))
    target_stocks = [s for s in target_stocks if s in df_trend.columns]

    if df_trend.empty or not target_stocks:
        return empty_fig, fig_tree, empty_fig, empty_fig

    df_filtered = df_trend[target_stocks]
    
    prev_closes = []
    for s in target_stocks:
        p = YESTERDAY_CLOSE.get(s)
        if pd.isna(p) or p == 0:
             valid_prices = df_filtered[s].dropna()
             p = valid_prices.iloc[0] if not valid_prices.empty else 100
        prev_closes.append(p)
    
    df_pct = ((df_filtered - pd.Series(prev_closes, index=target_stocks)) / pd.Series(prev_closes, index=target_stocks)) * 100
    df_pct.sort_index(inplace=True)

    # 計算平均線
    valid_cat_stocks = [s for s in category_stocks if s in df_pct.columns]
    if valid_cat_stocks:
        avg_series = df_pct[valid_cat_stocks].mean(axis=1)
    else:
        avg_series = df_pct.mean(axis=1)

    avg_col_name = f'{selected_category} Avg'
    df_pct[avg_col_name] = avg_series

    last_row = df_pct.iloc[-1].sort_values(ascending=False) 
    
    # 步驟 A: 找出所有漲跌停股
    last_prices = df_filtered.iloc[-1]
    limit_up_stocks = []
    limit_down_stocks = []
    
    for s in target_stocks:
        current_p = last_prices.get(s)
        limit_up = LIMITED_UP_PRICE.get(s)
        limit_down = LIMITED_DOWN_PRICE.get(s)
        
        if current_p and limit_up and current_p >= limit_up:
            limit_up_stocks.append(s)
        elif current_p and limit_down and current_p <= limit_down:
            limit_down_stocks.append(s)
            
    limit_up_set = set(limit_up_stocks)
    limit_down_set = set(limit_down_stocks)
    
    count_limit_up = len(limit_up_set)
    count_limit_down = len(limit_down_set)

    # 步驟 B: 從排行候選名單中「移除」漲跌停股
    exclude_list = [avg_col_name] + list(limit_up_stocks) + list(limit_down_stocks)
    ranking_candidates = last_row.drop(labels=exclude_list, errors='ignore').sort_values()
    
    top_movers = list(ranking_candidates.tail(5).index) + list(ranking_candidates.head(5).index)
    
    user_picks_set = set(user_picks)
    movers_set = set(top_movers)
    custom_members_set = set(category_stocks) if is_custom else set()
    
    highlight_set = user_picks_set | movers_set | custom_members_set | limit_up_set | limit_down_set
    
    sorted_columns = last_row.index 
    
    # --- 顏色分配 ---
    
    ranking_warm_colors = ['#FF0000', '#FF4500', '#FF6347', '#CD5C5C', '#8B0000']
    ranking_cold_colors = ['#008000', '#2E8B57', '#3CB371', '#20B2AA', '#006400']
    FOCUS_SOLID_COLOR = '#007bff'
    
    stock_colors = {}
    
    normal_stocks = [s for s in sorted_columns if s in highlight_set and s not in limit_up_set and s not in limit_down_set and s != avg_col_name]
    
    focus_stocks_list = [s for s in normal_stocks if s in user_picks_set]
    ranking_stocks_list = [s for s in normal_stocks if s not in user_picks_set]
    
    for s in focus_stocks_list:
        stock_colors[s] = FOCUS_SOLID_COLOR
        
    pos_ranking = [s for s in ranking_stocks_list if last_row[s] >= 0]
    neg_ranking = [s for s in ranking_stocks_list if last_row[s] < 0]
    
    for i, s in enumerate(pos_ranking):
        stock_colors[s] = ranking_warm_colors[i % len(ranking_warm_colors)]
    for i, s in enumerate(neg_ranking):
        stock_colors[s] = ranking_cold_colors[i % len(ranking_cold_colors)]
        
    fig_main = go.Figure()
    last_time = df_pct.index[-1]
    labels_to_plot = [] 
    
    stocks_to_plot = [c for c in sorted_columns if c != avg_col_name]
    plot_order = sorted_columns

    for col in plot_order:
        if col == avg_col_name:
            val = df_pct[col].iloc[-1]
            fig_main.add_trace(go.Scatter(
                x=df_pct.index, y=df_pct[col], mode='lines', 
                name=avg_col_name, line=dict(width=4, color='black'),
                hoverinfo='all', hovertemplate=f'{avg_col_name}: %{{y:.2f}}%'
            ))
            fig_main.add_trace(go.Scatter(
                x=[last_time], y=[val],
                mode='markers', marker=dict(color='black', size=8),
                showlegend=False, hoverinfo='skip'
            ))
            labels_to_plot.append({'val': val, 'text': f"Avg {val:.2f}%", 'color': 'black'})
            continue

        val = last_row[col]
        label_name = get_label(col)
        current_vol = vol_map.get(col, 0)
        
        is_limit_up = col in limit_up_set
        is_limit_down = col in limit_down_set
        is_highlighted = col in stock_colors 
        is_focus = col in user_picks_set 
        
        if is_limit_up:
            color = '#d62728' 
            width = 0 
            opacity = 1.0
            show = True
            marker_size = 12 
            hover_info = 'all'
        elif is_limit_down:
            color = '#2ca02c' 
            width = 0 
            opacity = 1.0
            show = True
            marker_size = 12 
            hover_info = 'all'
        elif is_highlighted:
            color = stock_colors[col]
            width = 3 if is_focus else 2
            opacity = 0.9
            show = True
            marker_size = 8
            hover_info = 'all'
        else:
            color = '#999999'
            width = 1
            opacity = 0.4
            show = False
            marker_size = 8
            hover_info = 'skip' 

        if not is_limit_up and not is_limit_down:
            fig_main.add_trace(go.Scatter(
                x=df_pct.index, y=df_pct[col], mode='lines', 
                name=label_name, 
                line=dict(width=width, color=color), opacity=opacity,
                showlegend=show, hovertemplate=f'{label_name}: %{{y:.2f}}%',
                hoverinfo=hover_info
            ))

        is_limit = is_limit_up or is_limit_down
        
        hover_template = f'{label_name}: %{{y:.2f}}%<br>Vol: {int(current_vol):,}'
        if is_limit:
            hover_template += ' (Limit!)'

        fig_main.add_trace(go.Scatter(
            x=[last_time], y=[val],
            mode='markers', 
            marker=dict(color=color, size=marker_size),
            name=label_name if is_limit else None, 
            showlegend=(is_limit), 
            hoverinfo='skip' if not is_limit else 'all', 
            hovertemplate=hover_template if is_limit else None
        ))
        
        if is_highlighted or is_limit:
            label_text = f"{label_name} {val:.2f}%"
            if is_limit_up:
                label_text += f" (共{count_limit_up}支)"
            elif is_limit_down:
                label_text += f" (共{count_limit_down}支)"
                
            labels_to_plot.append({'val': val, 'text': label_text, 'color': color})

    labels_to_plot.sort(key=lambda x: x['val'], reverse=True)
    current_pixel_offset = 0 
    last_data_val = 9999
    
    for item in labels_to_plot:
        val = item['val']
        if last_data_val - val < 0.5:
            current_pixel_offset += 25
        else:
            current_pixel_offset = 0
        last_data_val = val
        
        fig_main.add_annotation(
            x=last_time, y=val,
            text=item['text'],
            font=dict(color=item['color'], size=12),
            showarrow=True, arrowhead=0, arrowcolor=item['color'],
            ax=5, ay=current_pixel_offset,
            yanchor="middle", xanchor="left", align="left"
        )

    limit_up_names = [get_label(s) for s in limit_up_stocks]
    limit_down_names = [get_label(s) for s in limit_down_stocks]
    
    limit_up_text = f"🔥 漲停 ({len(limit_up_names)}): {', '.join(limit_up_names)}" if limit_up_names else ""
    limit_down_text = f"💚 跌停 ({len(limit_down_names)}): {', '.join(limit_down_names)}" if limit_down_names else ""

    if limit_up_text:
        fig_main.add_annotation(
            text=limit_up_text,
            xref="paper", yref="paper",
            x=0.01, y=0.99, showarrow=False,
            font=dict(color="#d62728", size=13, family="Arial Black"),
            align="left", bgcolor="rgba(255,255,255,0.7)", bordercolor="#d62728", borderwidth=1
        )
    
    if limit_down_text:
        fig_main.add_annotation(
            text=limit_down_text,
            xref="paper", yref="paper",
            x=0.01, y=0.01, showarrow=False,
            font=dict(color="#2ca02c", size=13, family="Arial Black"),
            align="left", bgcolor="rgba(255,255,255,0.7)", bordercolor="#2ca02c", borderwidth=1
        )

    max_move = np.nanmax(np.abs(df_pct.values)) if not df_pct.empty else 0
    limit = min(max(2.0, max_move * 1.1), 10.5)

    fig_main.update_layout(
        title=f'{selected_category} Trend',
        margin=dict(l=60, r=150, t=50, b=40),
        yaxis=dict(range=[-limit, limit], zeroline=True, zerolinecolor='black'),
        hovermode="x unified",
        # 🔥 修改這裡：加入 categoryorder='category ascending' 強制時間排序
        xaxis=dict(
            type='category', 
            categoryorder='category ascending',  # 強制由小到大排序 (09:00 -> 13:30)
            showspikes=True, 
            spikemode="across", 
            spikesnap="cursor", 
            showline=True, 
            showgrid=True
        ),
        template='plotly_white', 
        uirevision='constant'
    )

    stats_row = df_pct.drop(columns=[avg_col_name], errors='ignore').iloc[-1]
    up_count = (stats_row > 0).sum()
    down_count = (stats_row < 0).sum()
    flat_count = (stats_row == 0).sum()

    fig_pie = go.Figure(data=[go.Pie(
        labels=['Up', 'Down', 'Flat'], values=[up_count, down_count, flat_count],
        hole=.5, marker=dict(colors=['#d62728', '#2ca02c', 'gray']),
        textinfo='label+value', hoverinfo='label+percent'
    )])
    fig_pie.update_layout(title="Market Breadth", margin=dict(l=10, r=10, t=40, b=10), showlegend=False, uirevision='constant')

    sorted_asc_bar = stats_row.sort_values(ascending=True)
    bar_colors = ['#d62728' if v > 0 else '#2ca02c' for v in sorted_asc_bar.values]
    num_stocks = len(sorted_asc_bar)
    dynamic_height = max(300, 80 + num_stocks * 30)

    y_labels = [get_label(s) for s in sorted_asc_bar.index]

    fig_bar = go.Figure(go.Bar(
        x=sorted_asc_bar.values, 
        y=y_labels, 
        orientation='h',
        marker=dict(color=bar_colors),
        text=[f"{v:.2f}%" for v in sorted_asc_bar.values], textposition='auto'
    ))

    fig_bar.update_layout(
        title="Rankings",
        margin=dict(l=100, r=40, t=40, b=20),
        xaxis=dict(range=[-10, 10], zeroline=True, side='top'),
        yaxis=dict(type='category', dtick=1),
        template='plotly_white', uirevision='constant',
        height=dynamic_height, autosize=False
    )

    return fig_main, fig_tree, fig_pie, fig_bar

if __name__ == '__main__':
    print("🚀 戰情室啟動 (本機): http://127.0.0.1:8050/")
    print("📡 內網連線 (給同事): http://192.168.188.112:8050/")
    app.run(host='0.0.0.0', port=8050, debug=True)