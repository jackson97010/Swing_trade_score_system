"""
測試資料取得與評分模組
"""

import os
import sys

# 確保可以 import modules
sys.path.insert(0, os.path.dirname(__file__))

from finlab import login
from modules.data_fetcher import (
    fetch_stock_data,
    calculate_technical_indicators,
    load_industry_data,
    calculate_industry_trend,
    get_top_industries
)
from modules.scoring import calculate_batch_scores

# 登入 Finlab
login('Y8qx8Zs1zTnNk7McQPGpR4Lb9jv29EMQpiOMAxyBpmcIK4mYc2vODIvD8PuXLctw')

def test_data_scoring():
    """測試資料取得與評分功能"""

    print("=" * 60)
    print("開始測試資料取得與評分模組")
    print("=" * 60)

    # 測試股票清單
    test_codes = ['2330', '2454', '2603']
    print(f"\n測試股票: {', '.join(test_codes)}")

    # 1. 測試資料取得
    print("\n[步驟 1] 取得股票資料...")
    stock_data = fetch_stock_data(test_codes)

    if stock_data:
        print("✅ 資料取得成功")
        print(f"   收盤價資料: {stock_data['close'].shape}")
        print(f"   成交量資料: {stock_data['volume'].shape}")
        print(f"   股票名稱: {stock_data['stock_names']}")
    else:
        print("❌ 資料取得失敗")
        return False

    # 2. 測試技術指標計算
    print("\n[步驟 2] 計算技術指標...")
    tech_indicators = calculate_technical_indicators(stock_data['close'])
    print("✅ 技術指標計算完成")
    print(f"   MA10: {tech_indicators['ma10'].shape}")
    print(f"   MA20: {tech_indicators['ma20'].shape}")
    print(f"   MACD: {tech_indicators['macd'].shape}")

    # 3. 測試產業趨勢計算
    print("\n[步驟 3] 計算產業趨勢...")

    # 嘗試載入產業分類資料
    industry_df = load_industry_data()

    # 如果找不到預設路徑，嘗試當前目錄
    if industry_df.empty:
        local_path = os.path.join(os.path.dirname(__file__), '產業分類資料庫.csv')
        print(f"   嘗試使用本地路徑: {local_path}")
        industry_df = load_industry_data(local_path)

    if not industry_df.empty:
        print(f"✅ 產業分類資料載入成功，共 {len(industry_df)} 筆")

        industry_trend = calculate_industry_trend(stock_data['close'], industry_df)
        top_industries = get_top_industries(industry_trend)

        print(f"✅ 產業趨勢計算完成")
        print(f"   前五大強勢產業: {top_industries}")
    else:
        print("⚠️ 產業分類資料未載入，將跳過產業趨勢評分")
        industry_trend = None
        top_industries = []

    # 4. 測試評分計算
    print("\n[步驟 4] 計算股票評分...")
    scores = calculate_batch_scores(
        test_codes,
        stock_data,
        tech_indicators,
        industry_df,
        top_industries
    )

    print("✅ 評分計算完成")
    print("\n" + "=" * 60)
    print("評分結果:")
    print("=" * 60)
    print(scores.to_string(index=False))

    # 顯示詳細評分明細
    print("\n" + "=" * 60)
    print("詳細評分明細:")
    print("=" * 60)
    for _, row in scores.iterrows():
        stock_name = stock_data['stock_names'].get(row['stock_code'], '未知')
        print(f"\n{row['stock_code']} {stock_name}")
        print(f"  總分: {row['total_score']} 分")
        print(f"  評分說明: {row['details']}")
        if 'breakdown' in row:
            print(f"  明細: {row['breakdown']}")

    print("\n" + "=" * 60)
    print("測試完成!")
    print("=" * 60)

    return True


if __name__ == '__main__':
    try:
        test_data_scoring()
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
