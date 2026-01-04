"""
快速查詢評分 - 從預計算的 parquet 讀取
用法: python query_scores.py [日期]
範例: python query_scores.py 2024-12-20
"""

import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys
import json

DATA_DIR = Path(__file__).parent / 'data'
INDUSTRY_CSV = r'C:\Users\user\Documents\_12_BO_strategy\產業分類資料庫.csv'


def load_data():
    """載入預計算的資料"""
    if not DATA_DIR.exists():
        print("[ERROR] 找不到 data 目錄，請先執行 precompute_scores.py")
        return None

    data = {}
    files = ['total_score', 'score_ma', 'score_macd', 'score_revenue',
             'score_sector', 'score_volume', 'close', 'sector_return_10d']

    for name in files:
        path = DATA_DIR / f'{name}.parquet'
        if path.exists():
            data[name] = pd.read_parquet(path)
        else:
            print(f"[WARN] 找不到 {name}.parquet")

    # 載入元資料
    meta_path = DATA_DIR / 'meta.json'
    if meta_path.exists():
        with open(meta_path, 'r') as f:
            data['meta'] = json.load(f)

    return data


def query_scores(target_date: str = None, top_n: int = 50):
    """
    查詢指定日期的評分

    參數:
        target_date: 目標日期 (格式: YYYY-MM-DD)，若為 None 則使用最新日期
        top_n: 顯示前 N 名

    回傳:
        DataFrame: 評分結果
    """

    print(f"\n[LOAD] 載入預計算資料...")
    data = load_data()

    if data is None:
        return None

    total_score = data['total_score']
    close = data['close']
    sector_return = data['sector_return_10d']

    # 讀取產業分類
    industry_df = pd.read_csv(INDUSTRY_CSV)
    industry_df['代碼'] = industry_df['代碼'].astype(str)
    stock_to_sectors = industry_df.groupby('代碼')['細產業別'].apply(list).to_dict()

    # 決定目標日期
    available_dates = total_score.index.strftime('%Y-%m-%d').tolist()

    if target_date is None:
        target_date = available_dates[-1]
        print(f"[DATE] 使用最新日期: {target_date}")
    elif target_date not in available_dates:
        # 找最接近的日期
        target_dt = pd.to_datetime(target_date)
        valid_dates = total_score.index[total_score.index <= target_dt]
        if len(valid_dates) == 0:
            print(f"[ERROR] 找不到 {target_date} 或之前的資料")
            print(f"[INFO] 可用日期範圍: {available_dates[0]} ~ {available_dates[-1]}")
            return None
        target_date = valid_dates[-1].strftime('%Y-%m-%d')
        print(f"[WARN] 使用最接近的日期: {target_date}")

    print(f"\n{'='*60}")
    print(f"  評分查詢 - 目標日期: {target_date}")
    print(f"{'='*60}\n")

    # 取得該日資料
    scores_today = total_score.loc[target_date].dropna().sort_values(ascending=False)
    close_today = close.loc[target_date]

    # 取得各項分數
    score_ma = data['score_ma'].loc[target_date]
    score_macd = data['score_macd'].loc[target_date]
    score_revenue = data['score_revenue'].loc[target_date]
    score_sector = data['score_sector'].loc[target_date]
    score_volume = data['score_volume'].loc[target_date]

    # 取得前五大族群
    sector_today = sector_return.loc[target_date].dropna().sort_values(ascending=False)
    top5_sectors = sector_today.head(5)

    print(f"[HOT] 過去10天漲幅前五大族群:")
    for i, (sector, ret) in enumerate(top5_sectors.items(), 1):
        print(f"   {i}. {sector}: {ret:.2f}%")

    # 組合結果
    results = []
    for stock in scores_today.head(top_n).index:
        details = []

        if score_ma.get(stock, 0) > 0:
            details.append("均線多排(+20)")
        if score_macd.get(stock, 0) > 0:
            details.append("MACD強勢(+20)")
        if score_revenue.get(stock, 0) > 0:
            details.append("營收強(+10)")
        if score_sector.get(stock, 0) > 0:
            sectors = stock_to_sectors.get(stock, [])
            hot_sectors = [s for s in sectors if s in top5_sectors.index]
            if hot_sectors:
                details.append(f"熱門族群(+10):{','.join(hot_sectors)}")
            else:
                details.append("熱門族群(+10)")
        if score_volume.get(stock, 0) > 0:
            details.append("成交熱絡(+10)")

        results.append({
            '代碼': stock,
            '總分': int(scores_today[stock]),
            '收盤價': close_today.get(stock, np.nan),
            '評分說明': ', '.join(details)
        })

    df_result = pd.DataFrame(results)

    # 顯示結果
    print(f"\n{'='*80}")
    print(f"  評分結果 - 前 {top_n} 名")
    print(f"{'='*80}\n")

    print(f"{'排名':>4} {'代碼':>6} {'總分':>4} {'收盤價':>8} {'評分說明'}")
    print("-" * 80)

    for idx, row in df_result.iterrows():
        rank = idx + 1
        print(f"{rank:>4} {row['代碼']:>6} {row['總分']:>4} {row['收盤價']:>8.2f} {row['評分說明']}")

    # 統計
    all_scores = scores_today
    print(f"\n{'='*80}")
    print(f"[STATS] 統計資訊:")
    print(f"   - 滿分 (70分) 股票數: {len(all_scores[all_scores == 70])}")
    print(f"   - 60分以上股票數: {len(all_scores[all_scores >= 60])}")
    print(f"   - 50分以上股票數: {len(all_scores[all_scores >= 50])}")
    print(f"   - 總評分股票數: {len(all_scores)}")
    print(f"{'='*80}\n")

    return df_result


def list_available_dates():
    """列出可用的日期"""
    data = load_data()
    if data is None:
        return

    dates = data['total_score'].index.strftime('%Y-%m-%d').tolist()
    print(f"\n可用日期範圍: {dates[0]} ~ {dates[-1]}")
    print(f"共 {len(dates)} 個交易日\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--list':
            list_available_dates()
        else:
            query_scores(sys.argv[1])
    else:
        query_scores()
