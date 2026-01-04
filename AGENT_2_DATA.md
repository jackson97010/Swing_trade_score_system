# Agent 2 - Data & Scoring 任務說明

## 身份識別
- **Agent ID**: Agent 2
- **負責模組**: 資料取得與評分引擎 (Data Fetcher & Scoring Engine)
- **分支名稱**: `feature/data-scoring`
- **Worktree 路徑**: `C:\Users\User\Documents\_05_看盤波段\worktree-data`

---

## 任務目標

建立選股評分系統的資料引擎，包括：
1. 從 Finlab API 取得股票資料
2. 計算技術指標 (均線、MACD)
3. 實作評分邏輯 (技術面 + 基本面)
4. 計算產業趨勢排名

---

## 必須完成的檔案

### 1. `modules/data_fetcher.py` - 資料取得模組
**優先級**: 🔴 最高

#### 功能需求
- 從 Finlab 取得股票價格、成交量、營收、EPS 等資料
- 計算技術指標 (MA10, MA20, MA60, MACD)
- 取得產業分類資料
- 計算產業漲跌幅

#### 程式碼範本

```python
"""
資料取得模組 - 從 Finlab API 取得股票資料並計算技術指標
"""

from finlab import data
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# 設定資料範圍
data.set_universe('TSE_OTC')
data.truncate_start = (datetime.now() - timedelta(days=120)).strftime('%Y-%m-%d')


def fetch_stock_data(stock_codes: list) -> dict:
    """
    取得指定股票清單的所有必要資料

    Args:
        stock_codes: 股票代碼清單，例如 ['2330', '2454', '2603']

    Returns:
        dict: 包含各項資料的字典
        {
            'close': DataFrame,  # 收盤價
            'volume': DataFrame,  # 成交量
            'amount': DataFrame,  # 成交金額
            'revenue_yoy': DataFrame,  # 月營收年增率
            'eps': DataFrame,  # 每股盈餘
            'stock_names': dict  # 股票名稱對照表
        }
    """
    try:
        # 取得價格資料
        close = data.get('price:收盤價')
        volume = data.get('price:成交股數') / 1000  # 轉換為千股
        amount = data.get('price:成交金額')

        # 取得基本面資料
        revenue_yoy = data.get('monthly_revenue:去年同月增減(%)')
        eps = data.get('fundamental_features:每股盈餘')

        # 取得股票名稱
        from finlab.data import TWMarket
        market = TWMarket()
        stock_names = {code: market.get_name(code) for code in stock_codes if code in market.get_stocks()}

        # 篩選指定股票
        close = close[stock_codes] if isinstance(close, pd.DataFrame) else close
        volume = volume[stock_codes] if isinstance(volume, pd.DataFrame) else volume
        amount = amount[stock_codes] if isinstance(amount, pd.DataFrame) else amount

        return {
            'close': close,
            'volume': volume,
            'amount': amount,
            'revenue_yoy': revenue_yoy,
            'eps': eps,
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


def load_industry_data(csv_path: str = r'C:\Users\user\Documents\_12_BO_strategy\產業分類資料庫.csv') -> pd.DataFrame:
    """
    載入產業分類資料

    Args:
        csv_path: CSV 檔案路徑

    Returns:
        DataFrame: 產業分類資料 (columns: ['stock_code', 'industry'])
    """
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
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


# 匯出函數
__all__ = [
    'fetch_stock_data',
    'calculate_technical_indicators',
    'load_industry_data',
    'calculate_industry_trend',
    'get_top_industries'
]
```

---

### 2. `modules/scoring.py` - 評分計算模組
**優先級**: 🔴 最高

#### 功能需求
- 實作均線多頭排列判斷
- 實作 MACD 強勢判斷
- 實作基本面評分 (營收、產業趨勢、成交值)
- 彙整總分並產生評分說明

#### 程式碼範本

```python
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
        ma10 = technical_indicators['ma10'].loc[stock_code].iloc[-1] if stock_code in technical_indicators['ma10'].columns else np.nan
        ma20 = technical_indicators['ma20'].loc[stock_code].iloc[-1] if stock_code in technical_indicators['ma20'].columns else np.nan
        ma60 = technical_indicators['ma60'].loc[stock_code].iloc[-1] if stock_code in technical_indicators['ma60'].columns else np.nan

        is_ma_bullish, ma_score, ma_detail = check_ma_bullish(ma10, ma20, ma60)
        score += ma_score
        if ma_detail:
            details.append(ma_detail)
        breakdown['ma_bullish'] = ma_score

        # 2. 技術面 - MACD 強勢 (20分)
        macd_current = technical_indicators['macd'].loc[stock_code].iloc[-1] if stock_code in technical_indicators['macd'].columns else np.nan
        macd_prev = technical_indicators['macd'].loc[stock_code].iloc[-2] if stock_code in technical_indicators['macd'].columns and len(technical_indicators['macd']) >= 2 else np.nan

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
```

---

## 測試方式

### 單元測試

建立測試檔案 `test_data_scoring.py` (可選)：

```python
from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators
from modules.scoring import calculate_batch_scores, load_industry_data, calculate_industry_trend, get_top_industries

# 測試資料取得
test_codes = ['2330', '2454', '2603']
stock_data = fetch_stock_data(test_codes)

if stock_data:
    print("✅ 資料取得成功")
    print(f"收盤價: {stock_data['close'].shape}")

    # 測試技術指標
    tech_indicators = calculate_technical_indicators(stock_data['close'])
    print(f"✅ 技術指標計算完成")

    # 測試產業趨勢
    industry_df = load_industry_data()
    industry_trend = calculate_industry_trend(stock_data['close'], industry_df)
    top_industries = get_top_industries(industry_trend)
    print(f"✅ 產業趨勢計算完成，前五大: {top_industries}")

    # 測試評分
    scores = calculate_batch_scores(test_codes, stock_data, tech_indicators, industry_df, top_industries)
    print("✅ 評分計算完成")
    print(scores)
else:
    print("❌ 資料取得失敗")
```

執行測試：
```bash
conda activate my_project
python test_data_scoring.py
```

---

## Commit 訊息範例

```
[Agent-2] Data & Scoring: 實作資料取得與評分引擎

- 實作 data_fetcher.py: Finlab 資料取得與技術指標計算
- 實作 scoring.py: 評分邏輯 (技術面 + 基本面)
- 新增產業趨勢計算功能
- 新增批次評分功能

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 依賴關係

**此模組不依賴其他 Agent**，可以獨立開發與測試。

但會被以下 Agent 使用：
- Agent 3 (UI Layouts) 需要呼叫這些函數來顯示評分結果

---

## 注意事項

1. ⚠️ **確保 Finlab API Key 已設定**：檢查 `.env` 檔案
2. ⚠️ **產業分類檔案路徑**：確認 `C:\Users\user\Documents\_12_BO_strategy\產業分類資料庫.csv` 存在
3. ⚠️ **錯誤處理**：所有函數都應包含 try-except 錯誤處理
4. ⚠️ **參考 CLAUDE.md**：確保評分邏輯符合規格

---

## 參考資料

- 主專案說明: `CLAUDE.md` (評分系統設計章節)
- 協調文件: `MULTI_AGENT_GUIDE.md`

---

**任務文件版本**: v1.0
**建立日期**: 2026-01-04
**預計完成時間**: 3-4 小時
