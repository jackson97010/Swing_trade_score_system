"""
預計算評分系統 - 批次計算所有日期的評分並存成 parquet
用法: python precompute_scores.py [天數]
範例: python precompute_scores.py 60  # 計算最近60天
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from pathlib import Path

from finlab import data, login

# Finlab 登入
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

FINLAB_TOKEN = os.environ.get('FINLAB_TOKEN', 'YOUR_FINLAB_TOKEN_HERE')
login(FINLAB_TOKEN)

# 設定
data.set_universe('TSE_OTC')
INDUSTRY_CSV = r'C:\Users\user\Documents\_12_BO_strategy\產業分類資料庫.csv'
OUTPUT_DIR = Path(__file__).parent / 'data'
OUTPUT_DIR.mkdir(exist_ok=True)


def calculate_macd(close_df, fast=12, slow=26, signal=9):
    """批次計算所有股票的 MACD"""
    ema_fast = close_df.ewm(span=fast, adjust=False).mean()
    ema_slow = close_df.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    return macd_line


def precompute_all_scores(days=60):
    """
    預計算所有日期的評分

    參數:
        days: 要計算的天數 (預設60天)
    """

    print(f"\n{'='*60}")
    print(f"  預計算評分系統 - 計算最近 {days} 天")
    print(f"{'='*60}\n")

    # 設定資料起始日 (多抓一些確保有足夠資料計算 MA60)
    start_date = (datetime.now() - timedelta(days=days + 120)).strftime('%Y-%m-%d')
    data.truncate_start = start_date

    print("[INFO] 載入資料中...")

    # =====================
    # 1. 載入所有資料 (一次性)
    # =====================
    close = data.get('price:收盤價')
    trade_value = data.get('price:成交金額')
    revenue_yoy = data.get('monthly_revenue:去年同月增減(%)')

    # 讀取產業分類
    industry_df = pd.read_csv(INDUSTRY_CSV)
    industry_df['代碼'] = industry_df['代碼'].astype(str)

    print(f"[INFO] 資料範圍: {close.index[0].strftime('%Y-%m-%d')} ~ {close.index[-1].strftime('%Y-%m-%d')}")
    print(f"[INFO] 股票數量: {len(close.columns)}")

    # =====================
    # 2. 預計算技術指標 (向量化)
    # =====================
    print("[CALC] 計算技術指標...")

    # 均線
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()

    # 均線多頭: MA10 > MA20 > MA60
    ma_bullish = (ma10 > ma20) & (ma20 > ma60)

    # MACD
    macd_line = calculate_macd(close)
    macd_prev = macd_line.shift(1)

    # MACD > 0 且向上彎
    macd_bullish = (macd_line > 0) & (macd_line > macd_prev)

    # =====================
    # 3. 預計算基本面指標
    # =====================
    print("[CALC] 計算基本面指標...")

    # 營收 YoY > 20% (向前填充到每個交易日)
    revenue_aligned = revenue_yoy.reindex(close.index, method='ffill')
    revenue_good = revenue_aligned > 20

    # =====================
    # 4. 計算月均成交值篩選
    # =====================
    print("[CALC] 計算月均成交值...")
    avg_trade_20d = trade_value.rolling(20).mean()
    valid_stocks_mask = avg_trade_20d >= 3e8  # >= 3億

    # =====================
    # 5. 計算成交值前30大 (過去10天任一天)
    # =====================
    print("[CALC] 計算成交值排名...")

    # 每天的成交值排名
    trade_rank = trade_value.rank(axis=1, ascending=False)
    top30_daily = trade_rank <= 30

    # 過去10天任一天進入前30
    top30_10d = top30_daily.rolling(10).max().fillna(0).astype(bool)

    # =====================
    # 6. 計算產業趨勢 (過去10天漲幅前五大)
    # =====================
    print("[CALC] 計算產業趨勢...")

    # 建立股票->族群對照表
    stock_to_sectors = industry_df.groupby('代碼')['細產業別'].apply(list).to_dict()
    all_sectors = industry_df['細產業別'].unique()

    # 計算每個族群每天的平均股價
    sector_avg_price = {}
    sector_stocks_map = {}

    for sector in all_sectors:
        stocks_in_sector = industry_df[industry_df['細產業別'] == sector]['代碼'].tolist()
        stocks_in_sector = [s for s in stocks_in_sector if s in close.columns]
        if len(stocks_in_sector) >= 2:
            sector_avg_price[sector] = close[stocks_in_sector].mean(axis=1)
            sector_stocks_map[sector] = stocks_in_sector

    sector_price_df = pd.DataFrame(sector_avg_price)

    # 計算族群10日漲跌幅
    sector_return_10d = (sector_price_df / sector_price_df.shift(10) - 1) * 100

    # 每天的前五大族群
    sector_rank = sector_return_10d.rank(axis=1, ascending=False)
    top5_sectors_daily = sector_rank <= 5

    # 建立每天的熱門族群股票集合
    print("[CALC] 建立熱門族群對照表...")
    hot_sector_stocks = pd.DataFrame(False, index=close.index, columns=close.columns)

    for date in close.index:
        if date in top5_sectors_daily.index:
            hot_sectors_today = top5_sectors_daily.loc[date]
            hot_sectors_today = hot_sectors_today[hot_sectors_today].index.tolist()

            for sector in hot_sectors_today:
                if sector in sector_stocks_map:
                    for stock in sector_stocks_map[sector]:
                        if stock in hot_sector_stocks.columns:
                            hot_sector_stocks.loc[date, stock] = True

    # =====================
    # 7. 計算總分
    # =====================
    print("[CALC] 計算總分...")

    # 各項分數
    score_ma = ma_bullish.astype(int) * 20
    score_macd = macd_bullish.astype(int) * 20
    score_revenue = revenue_good.astype(int) * 10
    score_sector = hot_sector_stocks.astype(int) * 10
    score_volume = top30_10d.astype(int) * 10

    # 總分
    total_score = score_ma + score_macd + score_revenue + score_sector + score_volume

    # 套用月均成交值篩選 (不符合的設為 NaN)
    total_score = total_score.where(valid_stocks_mask)

    # =====================
    # 8. 儲存結果
    # =====================
    print("[SAVE] 儲存結果...")

    # 只保留最近 N 天
    recent_dates = close.index[-days:]

    # 儲存各項資料
    output_data = {
        'total_score': total_score.loc[recent_dates],
        'score_ma': score_ma.loc[recent_dates],
        'score_macd': score_macd.loc[recent_dates],
        'score_revenue': score_revenue.loc[recent_dates],
        'score_sector': score_sector.loc[recent_dates],
        'score_volume': score_volume.loc[recent_dates],
        'close': close.loc[recent_dates],
        'trade_value': trade_value.loc[recent_dates],
        'avg_trade_20d': avg_trade_20d.loc[recent_dates],
    }

    for name, df in output_data.items():
        output_path = OUTPUT_DIR / f'{name}.parquet'
        df.to_parquet(output_path)
        print(f"   - {name}.parquet ({df.shape})")

    # 儲存族群漲幅
    sector_return_10d.loc[recent_dates].to_parquet(OUTPUT_DIR / 'sector_return_10d.parquet')
    print(f"   - sector_return_10d.parquet")

    # 儲存元資料
    meta = {
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'date_range': f"{recent_dates[0].strftime('%Y-%m-%d')} ~ {recent_dates[-1].strftime('%Y-%m-%d')}",
        'total_stocks': len(close.columns),
        'total_days': len(recent_dates),
    }
    pd.Series(meta).to_json(OUTPUT_DIR / 'meta.json')

    print(f"\n{'='*60}")
    print(f"[DONE] 預計算完成!")
    print(f"   - 日期範圍: {meta['date_range']}")
    print(f"   - 股票數量: {meta['total_stocks']}")
    print(f"   - 天數: {meta['total_days']}")
    print(f"   - 輸出目錄: {OUTPUT_DIR}")
    print(f"{'='*60}\n")

    return output_data


if __name__ == '__main__':
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    precompute_all_scores(days)
