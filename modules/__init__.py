"""
選股評分系統 - 功能模組

此套件包含以下模組：
- data_fetcher: 資料取得模組 (Agent 2) ✅
- scoring: 評分計算引擎 (Agent 2) ✅
- charts: 圖表繪製模組 (Agent 4) ✅

使用方式：
    from modules.charts import create_candlestick_chart
    from modules.data_fetcher import fetch_stock_data
    from modules.scoring import calculate_score
"""

__version__ = '1.0.0'
__author__ = 'Claude AI Agents'

# 模組可以單獨導入，避免循環依賴
__all__ = [
    'data_fetcher',
    'scoring',
    'charts'
]
