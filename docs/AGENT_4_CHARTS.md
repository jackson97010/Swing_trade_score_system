# Agent 4 - Charts 任務說明

## 身份識別
- **Agent ID**: Agent 4
- **負責模組**: 圖表視覺化 (Charts & Visualization)
- **分支名稱**: `feature/charts`
- **Worktree 路徑**: `C:\Users\User\Documents\_05_看盤波段\worktree-charts`

---

## 任務目標

建立選股評分系統的圖表模組，包括：
1. K線圖 (Candlestick Chart)
2. 技術指標疊加 (均線、MACD)
3. 成交量柱狀圖
4. 互動式圖表功能

---

## 必須完成的檔案

### 1. `modules/charts.py` - 圖表繪製模組
**優先級**: 🔴 最高

#### 功能需求
- 繪製 K線圖（含均線）
- 繪製 MACD 指標圖
- 繪製成交量圖
- 整合為多子圖佈局

#### 程式碼範本

```python
"""
圖表繪製模組 - 使用 Plotly 繪製互動式股票圖表
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta

# 注意：這些函數由 Agent 2 提供
# from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators


def create_candlestick_chart(
    stock_code: str,
    days: int = 60,
    show_ma: bool = True,
    show_macd: bool = True,
    show_volume: bool = True
) -> go.Figure:
    """
    建立股票 K線圖（含技術指標）

    Args:
        stock_code: 股票代碼
        days: 顯示天數，預設 60 天
        show_ma: 是否顯示均線
        show_macd: 是否顯示 MACD
        show_volume: 是否顯示成交量

    Returns:
        go.Figure: Plotly 圖表物件
    """
    try:
        # TODO: 取消註解以下程式碼（等 Agent 2 完成）
        # from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators
        #
        # # 取得資料
        # stock_data = fetch_stock_data([stock_code])
        # if not stock_data:
        #     return _create_error_figure("資料取得失敗")
        #
        # close = stock_data['close'][stock_code]
        # volume = stock_data['volume'][stock_code]
        #
        # # 計算技術指標
        # tech_indicators = calculate_technical_indicators(stock_data['close'])

        # 暫時使用模擬資料
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        close = pd.Series([580 + i * 0.5 for i in range(days)], index=dates)
        volume = pd.Series([100000 + i * 1000 for i in range(days)], index=dates)

        # 模擬 OHLC 資料
        open_price = close * 0.98
        high_price = close * 1.02
        low_price = close * 0.97

        # 計算均線
        ma10 = close.rolling(window=10).mean()
        ma20 = close.rolling(window=20).mean()
        ma60 = close.rolling(window=60).mean()

        # 計算 MACD
        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        macd_histogram = macd - macd_signal

        # 建立子圖
        rows = 1 + (1 if show_macd else 0) + (1 if show_volume else 0)
        row_heights = []
        subplot_titles = []

        if rows == 1:
            row_heights = [1.0]
            subplot_titles = [f'{stock_code} 股價走勢']
        elif rows == 2:
            row_heights = [0.7, 0.3]
            subplot_titles = [f'{stock_code} 股價走勢', 'MACD' if show_macd else '成交量']
        elif rows == 3:
            row_heights = [0.6, 0.2, 0.2]
            subplot_titles = [f'{stock_code} 股價走勢', 'MACD', '成交量']

        fig = make_subplots(
            rows=rows,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=row_heights,
            subplot_titles=subplot_titles
        )

        # 第 1 子圖：K線圖
        fig.add_trace(
            go.Candlestick(
                x=dates,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close,
                name='K線',
                increasing_line_color='#ef5350',
                decreasing_line_color='#26a69a'
            ),
            row=1, col=1
        )

        # 均線
        if show_ma:
            fig.add_trace(
                go.Scatter(
                    x=dates, y=ma10,
                    mode='lines',
                    name='MA10',
                    line=dict(color='#42a5f5', width=1.5)
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=dates, y=ma20,
                    mode='lines',
                    name='MA20',
                    line=dict(color='#ffa726', width=1.5)
                ),
                row=1, col=1
            )
            fig.add_trace(
                go.Scatter(
                    x=dates, y=ma60,
                    mode='lines',
                    name='MA60',
                    line=dict(color='#ab47bc', width=1.5)
                ),
                row=1, col=1
            )

        current_row = 1

        # 第 2 子圖：MACD
        if show_macd:
            current_row += 1

            # MACD 柱狀圖
            colors = ['#ef5350' if val >= 0 else '#26a69a' for val in macd_histogram]
            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=macd_histogram,
                    name='MACD Histogram',
                    marker_color=colors,
                    showlegend=False
                ),
                row=current_row, col=1
            )

            # MACD 線
            fig.add_trace(
                go.Scatter(
                    x=dates, y=macd,
                    mode='lines',
                    name='MACD',
                    line=dict(color='#1976d2', width=1.5)
                ),
                row=current_row, col=1
            )

            # Signal 線
            fig.add_trace(
                go.Scatter(
                    x=dates, y=macd_signal,
                    mode='lines',
                    name='Signal',
                    line=dict(color='#ff9800', width=1.5)
                ),
                row=current_row, col=1
            )

            # 零軸線
            fig.add_hline(y=0, line_dash="dash", line_color="gray", row=current_row, col=1)

        # 第 3 子圖：成交量
        if show_volume:
            current_row += 1

            # 成交量顏色（紅綠）
            volume_colors = ['#ef5350' if close.iloc[i] >= open_price.iloc[i] else '#26a69a'
                             for i in range(len(close))]

            fig.add_trace(
                go.Bar(
                    x=dates,
                    y=volume,
                    name='成交量',
                    marker_color=volume_colors,
                    showlegend=False
                ),
                row=current_row, col=1
            )

        # 更新佈局
        fig.update_layout(
            title={
                'text': f'{stock_code} 技術分析圖表',
                'x': 0.5,
                'xanchor': 'center',
                'font': {'size': 20, 'color': '#333'}
            },
            xaxis_rangeslider_visible=False,
            height=600 if rows == 1 else 700 if rows == 2 else 800,
            hovermode='x unified',
            template='plotly_white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            margin=dict(l=50, r=50, t=80, b=50)
        )

        # 更新 X 軸
        fig.update_xaxes(
            title_text="日期",
            gridcolor='#e0e0e0',
            row=rows, col=1
        )

        # 更新 Y 軸
        fig.update_yaxes(title_text="價格", row=1, col=1, gridcolor='#e0e0e0')
        if show_macd:
            fig.update_yaxes(title_text="MACD", row=2 if not show_volume else 2, col=1, gridcolor='#e0e0e0')
        if show_volume:
            fig.update_yaxes(title_text="成交量", row=rows, col=1, gridcolor='#e0e0e0')

        return fig

    except Exception as e:
        return _create_error_figure(f"圖表建立失敗: {str(e)}")


def create_simple_line_chart(stock_code: str, close_data: pd.Series, title: str = None) -> go.Figure:
    """
    建立簡易折線圖

    Args:
        stock_code: 股票代碼
        close_data: 收盤價資料
        title: 圖表標題

    Returns:
        go.Figure: Plotly 圖表物件
    """
    try:
        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=close_data.index,
                y=close_data.values,
                mode='lines',
                name=stock_code,
                line=dict(color='#1976d2', width=2),
                fill='tozeroy',
                fillcolor='rgba(25, 118, 210, 0.1)'
            )
        )

        fig.update_layout(
            title={
                'text': title or f'{stock_code} 收盤價走勢',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="日期",
            yaxis_title="收盤價",
            hovermode='x unified',
            template='plotly_white',
            height=400
        )

        return fig

    except Exception as e:
        return _create_error_figure(f"圖表建立失敗: {str(e)}")


def create_score_distribution_chart(scores_df: pd.DataFrame) -> go.Figure:
    """
    建立評分分布圖

    Args:
        scores_df: 評分結果 DataFrame

    Returns:
        go.Figure: Plotly 圖表物件
    """
    try:
        fig = go.Figure()

        # 橫向長條圖
        fig.add_trace(
            go.Bar(
                x=scores_df['total_score'],
                y=scores_df['stock_code'],
                orientation='h',
                marker=dict(
                    color=scores_df['total_score'],
                    colorscale='RdYlGn',
                    showscale=True,
                    colorbar=dict(title="評分")
                ),
                text=scores_df['total_score'],
                textposition='outside'
            )
        )

        fig.update_layout(
            title='股票評分分布',
            xaxis_title='總分',
            yaxis_title='股票代碼',
            height=max(300, len(scores_df) * 40),
            template='plotly_white'
        )

        return fig

    except Exception as e:
        return _create_error_figure(f"圖表建立失敗: {str(e)}")


def _create_error_figure(error_message: str) -> go.Figure:
    """
    建立錯誤提示圖表

    Args:
        error_message: 錯誤訊息

    Returns:
        go.Figure: 錯誤提示圖表
    """
    fig = go.Figure()

    fig.add_annotation(
        text=f"❌ {error_message}",
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=16, color="red")
    )

    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=400,
        template='plotly_white'
    )

    return fig


# 匯出函數
__all__ = [
    'create_candlestick_chart',
    'create_simple_line_chart',
    'create_score_distribution_chart'
]
```

---

## 測試方式

### 單元測試

建立測試檔案 `test_charts.py`:

```python
"""
圖表模組測試
"""

from modules.charts import create_candlestick_chart, create_simple_line_chart, create_score_distribution_chart
import pandas as pd
from datetime import datetime, timedelta

# 測試 1: K線圖
print("測試 K線圖...")
fig1 = create_candlestick_chart('2330', days=60)
print("✅ K線圖建立成功")

# 測試 2: 簡易折線圖
print("\n測試折線圖...")
dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
close_data = pd.Series([580 + i for i in range(30)], index=dates)
fig2 = create_simple_line_chart('2330', close_data)
print("✅ 折線圖建立成功")

# 測試 3: 評分分布圖
print("\n測試評分分布圖...")
scores_df = pd.DataFrame({
    'stock_code': ['2330', '2454', '2603'],
    'total_score': [60, 50, 40]
})
fig3 = create_score_distribution_chart(scores_df)
print("✅ 評分分布圖建立成功")

# 儲存測試圖表
fig1.write_html("test_candlestick.html")
fig2.write_html("test_line.html")
fig3.write_html("test_distribution.html")

print("\n✅ 所有測試完成！圖表已儲存為 HTML 檔案")
```

執行測試：
```bash
conda activate my_project
python test_charts.py
```

預期輸出：
- `test_candlestick.html` - K線圖
- `test_line.html` - 折線圖
- `test_distribution.html` - 評分分布圖

---

## 與其他 Agent 整合

### 與 Agent 2 整合
在程式碼中取消註解以下部分：
```python
from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators
```

### 與 Agent 3 整合
Agent 3 會在 `selection_page.py` 中呼叫：
```python
from modules.charts import create_candlestick_chart
```

---

## Commit 訊息範例

```
[Agent-4] Charts: 實作圖表視覺化模組

- 實作 K線圖（含均線、MACD、成交量）
- 實作簡易折線圖
- 實作評分分布圖
- 使用 Plotly 建立互動式圖表
- 新增錯誤處理與測試程式

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 依賴關係

**依賴模組**:
- Agent 2 的 `modules/data_fetcher.py` (用於取得股票資料)

**開發策略**:
1. 先使用模擬資料測試圖表功能
2. 等 Agent 2 完成後，整合真實資料

---

## 圖表設計規範

### 配色方案
- 上漲（紅）: `#ef5350`
- 下跌（綠）: `#26a69a`
- MA10（藍）: `#42a5f5`
- MA20（橙）: `#ffa726`
- MA60（紫）: `#ab47bc`
- MACD（深藍）: `#1976d2`
- Signal（橙）: `#ff9800`

### 圖表高度
- 單圖: 600px
- 雙圖: 700px
- 三圖: 800px

### 互動功能
- Hover 顯示詳細資訊
- 縮放與平移
- 圖例點擊顯示/隱藏

---

## ⚠️ BUG 修復任務

### 當前 Bug 狀態說明

**好消息**: 目前的 3 個 bug 都不直接影響 Agent 4 的圖表模組開發！

**Bug 說明**:
1. **Bug 1** - 股票名稱更新問題：由 Agent 2 和 Agent 3 處理
2. **Bug 2** - 資料存儲問題：由 Agent 2 處理
3. **Bug 3** - Redis 功能：由 Agent 1 和 Agent 3 處理（低優先級）

**Agent 4 可以照常開發**:
- 圖表模組使用模擬資料即可獨立測試
- 等 Agent 2 完成後，直接整合真實資料即可
- 不需要等待其他 bug 修復即可開始工作

**建議開發順序**:
1. 先完成 K 線圖功能（使用模擬資料測試）
2. 確保圖表樣式符合 `real_time_panel.py` 的風格
3. 等 Agent 2 完成 `data_fetcher.py` 後，整合真實資料
4. 與 Agent 3 的 `selection_page.py` 整合測試

**整合時機**:
- 當 Agent 2 完成 Bug 1 和 Bug 2 的修復後
- 在 `create_candlestick_chart()` 函數中取消註解：
  ```python
  from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators
  ```

**優先級**: ✅ 無需等待，可立即開始開發

---

## 注意事項

1. ⚠️ **使用 Plotly**：參考 `real_time_panel.py` 的圖表風格
2. ⚠️ **效能優化**：資料點過多時考慮降採樣
3. ⚠️ **錯誤處理**：確保資料異常時顯示友善錯誤訊息
4. ⚠️ **響應式設計**：圖表應自適應容器寬度

---

## 參考資料

- 主專案說明: `CLAUDE.md`
- 參考程式碼: `real_time_panel.py`
- Plotly 文件: https://plotly.com/python/
- 協調文件: `MULTI_AGENT_GUIDE.md`

---

**任務文件版本**: v1.0
**建立日期**: 2026-01-04
**預計完成時間**: 2-3 小時
