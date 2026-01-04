"""
資料取得模組 - 從 Finlab API 取得股票資料並計算技術指標
"""

from finlab import data
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os
import pickle

# 資料存儲目錄
DATA_DIR = 'data'

# 設定資料範圍
data.set_universe('TSE_OTC')
data.truncate_start = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')


def fetch_stock_data(stock_codes: list) -> dict:
    """
    取得指定股票清單的所有必要資料（總是取得最新資料）

    Args:
        stock_codes: 股票代碼清單，例如 ['2330', '2454', '2603']

    Returns:
        dict: 包含各項資料的字典
        {
            'close': DataFrame,  # 收盤價
            'volume': DataFrame,  # 成交量
            'amount': DataFrame,  # 成交金額
            'revenue_yoy': DataFrame,  # 月營收年增率
            'stock_names': dict  # 股票名稱對照表
        }
    """
    try:
        print(f"📊 正在取得 {len(stock_codes)} 檔股票的最新資料...")
        
        # 取得價格資料（Finlab 會自動更新到最新日期）
        close = data.get('price:收盤價')
        volume = data.get('price:成交股數') / 1000  # 轉換為千股
        amount = data.get('price:成交金額')

        # 取得基本面資料
        revenue_yoy = data.get('monthly_revenue:去年同月增減(%)')

        # 取得股票名稱
        from finlab.markets.tw import TWMarket
        market = TWMarket()
        all_stock_names = market.get_asset_id_to_name()
        stock_names = {code: all_stock_names.get(code, code) for code in stock_codes}

        # 篩選指定股票
        close = close[stock_codes] if isinstance(close, pd.DataFrame) else close
        volume = volume[stock_codes] if isinstance(volume, pd.DataFrame) else volume
        amount = amount[stock_codes] if isinstance(amount, pd.DataFrame) else amount

        return {
            'close': close,
            'volume': volume,
            'amount': amount,
            'revenue_yoy': revenue_yoy,
            'stock_names': stock_names
        }

    except Exception as e:
        print(f"資料取得失敗: {str(e)}")
        return None


def calculate_technical_indicators(close_df: pd.DataFrame) -> dict:
    """
    計算技術指標 (均線、MACD)

    Args:
        close_df: 收盤價 DataFrame

    Returns:
        dict: 包含各項技術指標
        {
            'ma10': DataFrame,
            'ma20': DataFrame,
            'ma60': DataFrame,
            'macd': DataFrame,
            'macd_signal': DataFrame,
            'macd_histogram': DataFrame
        }
    """
    # 計算均線
    ma10 = close_df.rolling(window=10).mean()
    ma20 = close_df.rolling(window=20).mean()
    ma60 = close_df.rolling(window=60).mean()

    # 計算 MACD
    ema12 = close_df.ewm(span=12, adjust=False).mean()
    ema26 = close_df.ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    macd_signal = macd.ewm(span=9, adjust=False).mean()
    macd_histogram = macd - macd_signal

    return {
        'ma10': ma10,
        'ma20': ma20,
        'ma60': ma60,
        'macd': macd,
        'macd_signal': macd_signal,
        'macd_histogram': macd_histogram
    }


def load_industry_data(csv_path: str = None) -> pd.DataFrame:
    """
    載入產業分類資料

    Args:
        csv_path: CSV 檔案路徑，如未指定則使用專案目錄下的檔案

    Returns:
        DataFrame: 產業分類資料 (columns: ['stock_code', 'industry'])
    """
    # 如果沒有指定路徑，使用專案根目錄下的產業分類資料庫.csv
    if csv_path is None:
        # 取得當前模組的目錄
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 專案根目錄在 modules 的上一層
        project_dir = os.path.dirname(current_dir)
        csv_path = os.path.join(project_dir, '產業分類資料庫.csv')
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        # 重新命名欄位以符合程式碼預期
        df = df.rename(columns={
            '細產業別': 'industry',
            '代碼': 'stock_code',
            '商品': 'name'
        })
        # 確保 stock_code 是字串
        df['stock_code'] = df['stock_code'].astype(str)
        return df
    except FileNotFoundError:
        print(f"警告: 找不到產業分類檔案 {csv_path}")
        return pd.DataFrame(columns=['stock_code', 'industry'])
    except Exception as e:
        print(f"載入產業分類資料失敗: {str(e)}")
        return pd.DataFrame(columns=['stock_code', 'industry'])


def calculate_industry_trend(close_df: pd.DataFrame, industry_df: pd.DataFrame, days: int = 10) -> pd.DataFrame:
    """
    計算產業趨勢 (過去 N 天的漲跌幅)

    Args:
        close_df: 收盤價 DataFrame
        industry_df: 產業分類 DataFrame
        days: 計算天數，預設 10 天

    Returns:
        DataFrame: 產業漲跌幅排名
        columns: ['industry', 'return_pct', 'rank']
    """
    if industry_df.empty or close_df.empty:
        return pd.DataFrame(columns=['industry', 'return_pct', 'rank'])

    try:
        # 取得最近 N 天的收盤價
        latest_close = close_df.iloc[-1]
        past_close = close_df.iloc[-days] if len(close_df) >= days else close_df.iloc[0]

        # 計算個股漲跌幅
        stock_returns = ((latest_close - past_close) / past_close * 100).to_dict()

        # 計算產業平均漲跌幅
        industry_returns = {}
        for industry in industry_df['industry'].unique():
            stocks_in_industry = industry_df[industry_df['industry'] == industry]['stock_code'].tolist()
            stocks_in_industry = [str(s) for s in stocks_in_industry]  # 轉換為字串

            # 計算該產業的平均報酬率
            returns = [stock_returns.get(stock, np.nan) for stock in stocks_in_industry if stock in stock_returns]
            if returns:
                industry_returns[industry] = np.nanmean(returns)

        # 轉換為 DataFrame 並排序
        result = pd.DataFrame([
            {'industry': ind, 'return_pct': ret}
            for ind, ret in industry_returns.items()
        ])
        result = result.sort_values('return_pct', ascending=False).reset_index(drop=True)
        result['rank'] = range(1, len(result) + 1)

        return result

    except Exception as e:
        print(f"計算產業趨勢失敗: {str(e)}")
        return pd.DataFrame(columns=['industry', 'return_pct', 'rank'])


def get_top_industries(industry_trend_df: pd.DataFrame, top_n: int = 5) -> list:
    """
    取得漲幅前 N 大產業

    Args:
        industry_trend_df: 產業趨勢 DataFrame
        top_n: 取前幾名，預設 5

    Returns:
        list: 產業名稱清單
    """
    return industry_trend_df.head(top_n)['industry'].tolist()



# ========== Bug 2 修復：資料存儲功能 ==========

def save_stock_data(stock_data: dict, filename: str = None):
    """
    將股票資料存儲到 data 資料夾

    Args:
        stock_data: 股票資料字典（來自 fetch_stock_data）
        filename: 檔案名稱，預設使用日期
    """
    # 建立 data 資料夾
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"✅ 建立資料夾: {DATA_DIR}")

    # 預設檔案名稱：使用今天日期
    if filename is None:
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d')}.pkl"

    filepath = os.path.join(DATA_DIR, filename)

    try:
        with open(filepath, 'wb') as f:
            pickle.dump(stock_data, f)
        print(f"✅ 資料已存儲: {filepath}")
    except Exception as e:
        print(f"❌ 資料存儲失敗: {str(e)}")


def load_stock_data(filename: str = None) -> dict:
    """
    從 data 資料夾載入股票資料

    Args:
        filename: 檔案名稱，預設使用今天日期

    Returns:
        dict: 股票資料字典，如果檔案不存在則返回 None
    """
    if filename is None:
        filename = f"stock_data_{datetime.now().strftime('%Y%m%d')}.pkl"

    filepath = os.path.join(DATA_DIR, filename)

    if not os.path.exists(filepath):
        print(f"⚠️ 檔案不存在: {filepath}")
        return None

    try:
        with open(filepath, 'rb') as f:
            stock_data = pickle.load(f)
        print(f"✅ 資料已載入: {filepath}")
        return stock_data
    except Exception as e:
        print(f"❌ 資料載入失敗: {str(e)}")
        return None


def fetch_and_save_stock_data(stock_codes: list, force_update: bool = False) -> dict:
    """
    取得股票資料並存儲（帶快取功能）

    Args:
        stock_codes: 股票代碼清單
        force_update: 是否強制更新資料（忽略快取）

    Returns:
        dict: 股票資料字典
    """
    # 如果不強制更新，先嘗試載入今日快取
    if not force_update:
        cached_data = load_stock_data()
        if cached_data is not None:
            print("✅ 使用快取資料")
            return cached_data

    # 從 Finlab 取得最新資料
    print("📥 從 Finlab 取得最新資料...")
    stock_data = fetch_stock_data(stock_codes)

    # 存儲資料
    if stock_data is not None:
        save_stock_data(stock_data)

    return stock_data


# 匯出函數
__all__ = [
    'fetch_stock_data',
    'fetch_and_save_stock_data',  # 新增
    'save_stock_data',             # 新增
    'load_stock_data',             # 新增
    'calculate_technical_indicators',
    'load_industry_data',
    'calculate_industry_trend',
    'get_top_industries'
]
