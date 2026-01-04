"""
評分計算模組 - 計算股票綜合評分 (技術面 + 基本面)
"""

import pandas as pd
import numpy as np


def check_ma_bullish(ma10: float, ma20: float, ma60: float) -> tuple:
    """
    檢查均線多頭排列 (MA10 > MA20 > MA60)

    Args:
        ma10: 10日均線
        ma20: 20日均線
        ma60: 60日均線

    Returns:
        tuple: (是否多頭, 得分, 說明)
    """
    if pd.isna(ma10) or pd.isna(ma20) or pd.isna(ma60):
        return False, 0, ""

    if ma10 > ma20 > ma60:
        return True, 20, "均線多排(+20)"
    else:
        return False, 0, ""


def check_macd_bullish(macd_current: float, macd_prev: float) -> tuple:
    """
    檢查 MACD 強勢 (MACD > 0 且向上)

    Args:
        macd_current: 當前 MACD 值
        macd_prev: 前一日 MACD 值

    Returns:
        tuple: (是否強勢, 得分, 說明)
    """
    if pd.isna(macd_current) or pd.isna(macd_prev):
        return False, 0, ""

    if macd_current > 0 and macd_current > macd_prev:
        return True, 20, "MACD多頭(+20)"
    else:
        return False, 0, ""


def check_revenue_growth(revenue_yoy: float, threshold: float = 20.0) -> tuple:
    """
    檢查營收成長 (YoY > threshold%)

    Args:
        revenue_yoy: 月營收年增率 (%)
        threshold: 門檻值，預設 20%

    Returns:
        tuple: (是否達標, 得分, 說明)
    """
    if pd.isna(revenue_yoy):
        return False, 0, ""

    if revenue_yoy > threshold:
        return True, 10, f"營收強勁(+10)"
    else:
        return False, 0, ""


def check_industry_trend(stock_code: str, industry_df: pd.DataFrame, top_industries: list) -> tuple:
    """
    檢查是否屬於強勢產業

    Args:
        stock_code: 股票代碼
        industry_df: 產業分類 DataFrame
        top_industries: 前五大強勢產業清單

    Returns:
        tuple: (是否強勢產業, 得分, 說明)
    """
    if industry_df.empty or not top_industries:
        return False, 0, ""

    stock_industry = industry_df[industry_df['stock_code'] == stock_code]['industry'].values

    if len(stock_industry) > 0 and stock_industry[0] in top_industries:
        return True, 10, f"強勢族群(+10)"
    else:
        return False, 0, ""


def check_volume_activity(amount_series: pd.Series, days: int = 10, top_n: int = 30) -> tuple:
    """
    檢查成交值活絡度 (過去 N 天內有任一天進入前 top_n 大)

    Args:
        amount_series: 成交金額 Series (過去 N 天)
        days: 檢查天數
        top_n: 前幾名，預設 30

    Returns:
        tuple: (是否活絡, 得分, 說明)
    """
    if amount_series.empty:
        return False, 0, ""

    try:
        # 取得過去 N 天的成交金額
        recent_amounts = amount_series.tail(days)

        # 取得同期所有股票的成交金額並排名
        # (此處簡化處理，假設已有全市場資料)
        # 實際應用中需要與全市場資料比較

        # 暫時以成交金額 > 50億為活絡標準
        if recent_amounts.max() > 5_000_000_000:
            return True, 10, "成交活絡(+10)"
        else:
            return False, 0, ""

    except Exception as e:
        return False, 0, ""


def calculate_stock_score(
    stock_code: str,
    technical_indicators: dict,
    fundamental_data: dict,
    industry_df: pd.DataFrame,
    top_industries: list
) -> dict:
    """
    計算單一股票的綜合評分

    Args:
        stock_code: 股票代碼
        technical_indicators: 技術指標字典
        fundamental_data: 基本面資料字典
        industry_df: 產業分類 DataFrame
        top_industries: 強勢產業清單

    Returns:
        dict: 評分結果
        {
            'stock_code': str,
            'total_score': int,
            'details': list,  # 評分說明清單
            'breakdown': dict  # 詳細分數
        }
    """
    score = 0
    details = []
    breakdown = {}

    try:
        # 1. 技術面 - 均線多頭排列 (20分)
        ma10 = technical_indicators['ma10'][stock_code].iloc[-1] if stock_code in technical_indicators['ma10'].columns else np.nan
        ma20 = technical_indicators['ma20'][stock_code].iloc[-1] if stock_code in technical_indicators['ma20'].columns else np.nan
        ma60 = technical_indicators['ma60'][stock_code].iloc[-1] if stock_code in technical_indicators['ma60'].columns else np.nan

        is_ma_bullish, ma_score, ma_detail = check_ma_bullish(ma10, ma20, ma60)
        score += ma_score
        if ma_detail:
            details.append(ma_detail)
        breakdown['ma_bullish'] = ma_score

        # 2. 技術面 - MACD 強勢 (20分)
        macd_current = technical_indicators['macd'][stock_code].iloc[-1] if stock_code in technical_indicators['macd'].columns else np.nan
        macd_prev = technical_indicators['macd'][stock_code].iloc[-2] if stock_code in technical_indicators['macd'].columns and len(technical_indicators['macd']) >= 2 else np.nan

        is_macd_bullish, macd_score, macd_detail = check_macd_bullish(macd_current, macd_prev)
        score += macd_score
        if macd_detail:
            details.append(macd_detail)
        breakdown['macd_bullish'] = macd_score

        # 3. 基本面 - 營收成長 (10分)
        revenue_yoy = fundamental_data.get('revenue_yoy', {}).get(stock_code, np.nan)
        is_revenue_good, revenue_score, revenue_detail = check_revenue_growth(revenue_yoy)
        score += revenue_score
        if revenue_detail:
            details.append(revenue_detail)
        breakdown['revenue_growth'] = revenue_score

        # 4. 基本面 - 產業趨勢 (10分)
        is_strong_industry, industry_score, industry_detail = check_industry_trend(stock_code, industry_df, top_industries)
        score += industry_score
        if industry_detail:
            details.append(industry_detail)
        breakdown['industry_trend'] = industry_score

        # 5. 基本面 - 成交值活絡 (10分)
        amount_series = fundamental_data.get('amount', {}).get(stock_code, pd.Series())
        is_active, volume_score, volume_detail = check_volume_activity(amount_series)
        score += volume_score
        if volume_detail:
            details.append(volume_detail)
        breakdown['volume_activity'] = volume_score

    except Exception as e:
        print(f"計算 {stock_code} 評分時發生錯誤: {str(e)}")

    return {
        'stock_code': stock_code,
        'total_score': score,
        'details': ', '.join(details) if details else '無符合條件',
        'breakdown': breakdown
    }


def calculate_batch_scores(
    stock_codes: list,
    stock_data: dict,
    technical_indicators: dict,
    industry_df: pd.DataFrame,
    top_industries: list
) -> pd.DataFrame:
    """
    批次計算多檔股票的評分

    Args:
        stock_codes: 股票代碼清單
        stock_data: 股票資料字典
        technical_indicators: 技術指標字典
        industry_df: 產業分類 DataFrame
        top_industries: 強勢產業清單

    Returns:
        DataFrame: 評分結果表
    """
    results = []

    for code in stock_codes:
        result = calculate_stock_score(
            code,
            technical_indicators,
            {
                'revenue_yoy': stock_data.get('revenue_yoy', {}),
                'amount': stock_data.get('amount', {})
            },
            industry_df,
            top_industries
        )
        results.append(result)

    return pd.DataFrame(results)


# 匯出函數
__all__ = [
    'check_ma_bullish',
    'check_macd_bullish',
    'check_revenue_growth',
    'check_industry_trend',
    'check_volume_activity',
    'calculate_stock_score',
    'calculate_batch_scores'
]
