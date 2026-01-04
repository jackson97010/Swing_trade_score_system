"""
選股評分系統 - 功能模組

此套件包含以下模組：
- data_fetcher: 資料取得模組 (Agent 2) ✅
- scoring: 評分計算引擎 (Agent 2) ✅
- charts: 圖表繪製模組 (Agent 4) ✅
"""

__version__ = '1.0.0'
__author__ = 'Claude AI Agents'

# 模組載入 (所有 Agent 已完成 ✅)
from .data_fetcher import fetch_stock_data
from .scoring import calculate_score
from .charts import create_candlestick_chart, create_simple_line_chart, create_score_distribution_chart

__all__ = [
    'fetch_stock_data',
    'calculate_score',
    'create_candlestick_chart',
    'create_simple_line_chart',
    'create_score_distribution_chart'
]
