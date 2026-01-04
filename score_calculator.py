"""
選股評分系統 - Terminal 版本
用法: python score_calculator.py [日期]
範例: python score_calculator.py 2024-12-20
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys

from finlab import data, login

# Finlab 登入
import os
from pathlib import Path

# 讀取 .env 文件
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    with open(env_path, 'r') as f:
        for line in f:
            if '=' in line and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

FINLAB_TOKEN = os.environ.get('FINLAB_TOKEN', 'YOUR_FINLAB_TOKEN_HERE')
login(FINLAB_TOKEN)

# 設定資料範圍
data.set_universe('TSE_OTC')

# 產業分類資料庫路徑
INDUSTRY_CSV = r'C:\Users\user\Documents\_12_BO_strategy\產業分類資料庫.csv'


def calculate_macd(close_series, fast=12, slow=26, signal=9):
    """計算 MACD"""
    ema_fast = close_series.ewm(span=fast, adjust=False).mean()
    ema_slow = close_series.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    return macd_line, signal_line


def get_score(target_date: str = None):
    """
    計算指定日期的選股評分

    參數:
        target_date: 目標日期 (格式: YYYY-MM-DD)，若為 None 則自動找最新交易日

    回傳:
        DataFrame: 評分結果
    """

    # 先載入資料來找最新交易日
    if target_date is None:
        # 設定資料起始日 (往前抓 120 天)
        start_date = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')
        data.truncate_start = start_date

        print("\n[INFO] 載入資料中 (尋找最新交易日)...")
        close_temp = data.get('price:收盤價')
        target_date = close_temp.index[-1].strftime('%Y-%m-%d')
        print(f"[DATE] 自動選取最新交易日: {target_date}")

    print(f"\n{'='*60}")
    print(f"  選股評分系統 - 目標日期: {target_date}")
    print(f"{'='*60}\n")

    # 設定資料起始日 (往前抓 120 天確保有足夠資料計算 MA60)
    target_dt = pd.to_datetime(target_date)
    start_date = (target_dt - timedelta(days=120)).strftime('%Y-%m-%d')
    data.truncate_start = start_date

    print("[INFO] 載入資料中...")

    # 取得價格資料
    close = data.get('price:收盤價')
    trade_value = data.get('price:成交金額')  # 成交金額

    # 取得營收資料
    revenue_yoy = data.get('monthly_revenue:去年同月增減(%)')

    # 讀取產業分類
    industry_df = pd.read_csv(INDUSTRY_CSV)
    industry_df['代碼'] = industry_df['代碼'].astype(str)

    # 確認目標日期存在於資料中
    if target_date not in close.index.strftime('%Y-%m-%d').tolist():
        # 找最接近的日期
        available_dates = close.index[close.index <= target_dt]
        if len(available_dates) == 0:
            print(f"[ERROR] 找不到 {target_date} 或之前的資料")
            return None
        target_date = available_dates[-1].strftime('%Y-%m-%d')
        print(f"[WARN] 使用最接近的交易日: {target_date}")

    # 取得目標日期的 index 位置
    target_idx = close.index.get_loc(pd.to_datetime(target_date))

    # =====================
    # 0. 篩選月均成交值 >= 3億 的標的
    # =====================
    print(f"[FILTER] 篩選月均成交值 >= 3億...")

    # 計算過去20個交易日的平均成交金額
    lookback = min(20, target_idx + 1)
    avg_trade_value = trade_value.iloc[target_idx - lookback + 1:target_idx + 1].mean()

    # 篩選 >= 3億 (3E8)
    valid_stocks = avg_trade_value[avg_trade_value >= 3e8].index.tolist()
    print(f"[FILTER] 符合條件標的數: {len(valid_stocks)} / {len(close.columns)}")

    # 只保留符合條件的股票
    close = close[valid_stocks]
    trade_value = trade_value[valid_stocks]

    print(f"[CALC] 計算技術指標...")

    # =====================
    # 1. 計算均線 (MA10, MA20, MA60)
    # =====================
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma60 = close.rolling(60).mean()

    # 均線多頭排列: MA10 > MA20 > MA60
    ma_bullish = (ma10.iloc[target_idx] > ma20.iloc[target_idx]) & \
                 (ma20.iloc[target_idx] > ma60.iloc[target_idx])

    # =====================
    # 2. 計算 MACD
    # =====================
    macd_scores = {}
    for stock in close.columns:
        try:
            macd_line, signal_line = calculate_macd(close[stock])
            macd_today = macd_line.iloc[target_idx]
            macd_yesterday = macd_line.iloc[target_idx - 1]

            # MACD > 0 且向上彎
            if macd_today > 0 and macd_today > macd_yesterday:
                macd_scores[stock] = True
            else:
                macd_scores[stock] = False
        except:
            macd_scores[stock] = False

    macd_bullish = pd.Series(macd_scores)

    # =====================
    # 3. 營收成長 YoY > 20%
    # =====================
    # 取得最近一期的營收 YoY (往前找有資料的)
    revenue_latest = revenue_yoy.iloc[:target_idx+1].ffill().iloc[-1]
    revenue_good = revenue_latest > 20

    # =====================
    # 4. 產業趨勢 - 過去10天漲幅前五大族群
    # =====================
    print(f"[CALC] 計算產業趨勢...")

    # 計算每個族群的平均漲跌幅
    close_today = close.iloc[target_idx]
    close_10d_ago = close.iloc[max(0, target_idx - 10)]

    sector_returns = {}
    sector_stocks = {}

    for sector in industry_df['細產業別'].unique():
        stocks_in_sector = industry_df[industry_df['細產業別'] == sector]['代碼'].tolist()
        stocks_in_sector = [s for s in stocks_in_sector if s in close.columns]

        if len(stocks_in_sector) < 2:
            continue

        # 計算族群平均股價
        avg_price_today = close_today[stocks_in_sector].mean()
        avg_price_10d = close_10d_ago[stocks_in_sector].mean()

        if pd.notna(avg_price_today) and pd.notna(avg_price_10d) and avg_price_10d > 0:
            sector_return = (avg_price_today - avg_price_10d) / avg_price_10d * 100
            sector_returns[sector] = sector_return
            sector_stocks[sector] = stocks_in_sector

    # 取前五大漲幅族群
    top5_sectors = sorted(sector_returns.items(), key=lambda x: x[1], reverse=True)[:5]
    top5_sector_names = [s[0] for s in top5_sectors]

    print(f"\n[HOT] 過去10天漲幅前五大族群:")
    for i, (sector, ret) in enumerate(top5_sectors, 1):
        print(f"   {i}. {sector}: {ret:.2f}%")

    # 找出屬於前五大族群的股票
    hot_sector_stocks = set()
    for sector in top5_sector_names:
        hot_sector_stocks.update(sector_stocks.get(sector, []))

    # =====================
    # 5. 成交值前30大 (過去10天任一天)
    # =====================
    print(f"[CALC] 計算成交值排名...")

    top30_stocks = set()
    for i in range(max(0, target_idx - 9), target_idx + 1):
        daily_trade = trade_value.iloc[i].dropna().sort_values(ascending=False)
        top30_today = daily_trade.head(30).index.tolist()
        top30_stocks.update(top30_today)

    # =====================
    # 計算總分
    # =====================
    print(f"\n[CALC] 計算總分...")

    all_stocks = close.columns.tolist()
    results = []

    for stock in all_stocks:
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
            # 找出該股票所屬的熱門族群
            stock_sectors = industry_df[industry_df['代碼'] == stock]['細產業別'].tolist()
            hot_sectors = [s for s in stock_sectors if s in top5_sector_names]
            details.append(f"熱門族群(+10):{','.join(hot_sectors)}")

        # 基本面: 成交值前30 (+10)
        if stock in top30_stocks:
            score += 10
            details.append("成交熱絡(+10)")

        if score > 0:
            results.append({
                '代碼': stock,
                '總分': score,
                '收盤價': close_today.get(stock, np.nan),
                '評分說明': ', '.join(details)
            })

    # 轉換成 DataFrame 並排序
    df_result = pd.DataFrame(results)
    df_result = df_result.sort_values('總分', ascending=False).reset_index(drop=True)

    return df_result


def main():
    # 預設日期為今天，如果是假日會自動找最近的交易日
    if len(sys.argv) > 1:
        target_date = sys.argv[1]
    else:
        target_date = None  # None 表示自動找最新交易日

    # 計算評分
    result = get_score(target_date)

    if result is None or len(result) == 0:
        print("[ERROR] 沒有符合條件的股票")
        return

    # 顯示前50名
    print(f"\n{'='*80}")
    print(f"  評分結果 - 前 50 名")
    print(f"{'='*80}\n")

    top50 = result.head(50)

    # 格式化輸出
    print(f"{'排名':>4} {'代碼':>6} {'總分':>4} {'收盤價':>8} {'評分說明'}")
    print("-" * 80)

    for idx, row in top50.iterrows():
        rank = idx + 1
        print(f"{rank:>4} {row['代碼']:>6} {row['總分']:>4} {row['收盤價']:>8.2f} {row['評分說明']}")

    # 統計資訊
    print(f"\n{'='*80}")
    print(f"[STATS] 統計資訊:")
    print(f"   - 滿分 (70分) 股票數: {len(result[result['總分'] == 70])}")
    print(f"   - 60分以上股票數: {len(result[result['總分'] >= 60])}")
    print(f"   - 50分以上股票數: {len(result[result['總分'] >= 50])}")
    print(f"   - 總評分股票數: {len(result)}")
    print(f"{'='*80}\n")


if __name__ == '__main__':
    main()
