# Charts 模块使用指南

**模块**: `modules/charts.py`
**负责**: Agent 4 - Charts & Visualization
**状态**: ✅ 已完成并可用

---

## 快速开始

### 导入模块

```python
from modules.charts import (
    create_candlestick_chart,      # K线图
    create_simple_line_chart,      # 简易折线图
    create_score_distribution_chart # 评分分布图
)
```

---

## API 文档

### 1. create_candlestick_chart()

建立股票 K线图（含技术指标）

**函数签名**:
```python
create_candlestick_chart(
    stock_code: str,
    days: int = 60,
    show_ma: bool = True,
    show_macd: bool = True,
    show_volume: bool = True
) -> go.Figure
```

**参数说明**:
- `stock_code` (str): 股票代码，例如 '2330'
- `days` (int): 显示天数，默认 60 天
- `show_ma` (bool): 是否显示均线 (MA10/MA20/MA60)，默认 True
- `show_macd` (bool): 是否显示 MACD 指标，默认 True
- `show_volume` (bool): 是否显示成交量，默认 True

**返回值**: Plotly Figure 对象

**使用示例**:
```python
# 完整版 K线图（含所有指标）
fig = create_candlestick_chart('2330', days=60)
fig.show()

# 仅显示 K线和均线
fig = create_candlestick_chart('2330', show_macd=False, show_volume=False)

# 仅显示 K线（无任何指标）
fig = create_candlestick_chart('2330', show_ma=False, show_macd=False, show_volume=False)

# 在 Dash 中使用
import dash.dcc as dcc
dcc.Graph(figure=fig)
```

**图表特点**:
- 子图 1: K线图 + 均线 (MA10/MA20/MA60)
- 子图 2: MACD + Signal + Histogram
- 子图 3: 成交量柱状图（红涨绿跌）
- 互动功能: Hover、缩放、平移、图例切换

---

### 2. create_simple_line_chart()

建立简易折线图

**函数签名**:
```python
create_simple_line_chart(
    stock_code: str,
    close_data: pd.Series,
    title: str = None
) -> go.Figure
```

**参数说明**:
- `stock_code` (str): 股票代码
- `close_data` (pd.Series): 收盘价数据，index 为日期
- `title` (str, optional): 图表标题，默认为 '{stock_code} 收盘价走势'

**返回值**: Plotly Figure 对象

**使用示例**:
```python
import pandas as pd
from datetime import datetime

# 准备数据
dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
close_data = pd.Series([580 + i * 2 for i in range(30)], index=dates)

# 创建图表
fig = create_simple_line_chart('2330', close_data, title='台积电 30日走势')
fig.show()

# 在 Dash 中使用
dcc.Graph(figure=fig)
```

**图表特点**:
- 折线图 + 面积填充
- 简洁设计，适合快速预览
- 高度: 400px

---

### 3. create_score_distribution_chart()

建立评分分布图

**函数签名**:
```python
create_score_distribution_chart(
    scores_df: pd.DataFrame
) -> go.Figure
```

**参数说明**:
- `scores_df` (pd.DataFrame): 评分结果，必须包含以下列：
  - `stock_code`: 股票代码
  - `total_score`: 总分

**返回值**: Plotly Figure 对象

**使用示例**:
```python
import pandas as pd

# 准备数据
scores_df = pd.DataFrame({
    'stock_code': ['2330', '2454', '2603', '3008'],
    'total_score': [60, 55, 50, 45]
})

# 创建图表
fig = create_score_distribution_chart(scores_df)
fig.show()

# 在 Dash 中使用
dcc.Graph(figure=fig)
```

**图表特点**:
- 横向条形图
- 颜色梯度显示评分高低（RdYlGn 配色）
- 动态高度（根据股票数量调整）
- 显示评分数值

---

## 与 Agent 2 整合

### 当前状态（使用模拟数据）

目前 `create_candlestick_chart()` 使用模拟数据进行测试：

```python
# 模拟数据（charts.py 第 84-86 行）
dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
close = pd.Series([580 + i * 0.5 for i in range(days)], index=dates)
volume = pd.Series([100000 + i * 1000 for i in range(days)], index=dates)
```

### 整合真实数据（待 Agent 2 完成）

当 Agent 2 完成 `modules/data_fetcher.py` 后，在 `charts.py` 中取消注释以下代码（第 70-81 行）：

```python
# 取消以下注释
from modules.data_fetcher import fetch_stock_data, calculate_technical_indicators

# 取得资料
stock_data = fetch_stock_data([stock_code])
if not stock_data:
    return _create_error_figure("资料取得失败")

close = stock_data['close'][stock_code]
volume = stock_data['volume'][stock_code]

# 计算技术指标
tech_indicators = calculate_technical_indicators(stock_data['close'])
```

**整合步骤**:
1. 等待 Agent 2 完成 Bug 1 和 Bug 2 修复
2. 取消注释上述代码
3. 删除或注释掉模拟数据代码（第 84-86 行）
4. 测试图表是否正常显示真实数据

---

## 与 Agent 3 整合

Agent 3 在 `layouts/selection_page.py` 中调用图表：

```python
from modules.charts import create_candlestick_chart

# 在 Dash Callback 中使用
@app.callback(
    Output('stock-chart', 'figure'),
    Input('stock-table', 'active_cell')
)
def update_chart(active_cell):
    if active_cell:
        stock_code = active_cell['row_id']
        fig = create_candlestick_chart(stock_code, days=60)
        return fig
    return go.Figure()
```

---

## 配色方案（台股标准）

所有图表遵循以下配色：

| 元素 | 颜色代码 | 说明 |
|------|---------|------|
| 上涨 K线 | `#ef5350` | 红色 |
| 下跌 K线 | `#26a69a` | 绿色 |
| MA10 | `#42a5f5` | 蓝色 |
| MA20 | `#ffa726` | 橙色 |
| MA60 | `#ab47bc` | 紫色 |
| MACD | `#1976d2` | 深蓝色 |
| Signal | `#ff9800` | 橙色 |

---

## 图表尺寸

| 配置 | 高度 |
|------|------|
| 仅 K线 | 600px |
| K线 + MACD 或 K线 + 成交量 | 700px |
| K线 + MACD + 成交量 | 800px |
| 简易折线图 | 400px |
| 评分分布图 | 动态 (最小 300px，每档股票 40px) |

---

## 错误处理

所有函数都包含完整的错误处理：

```python
try:
    # 图表创建逻辑
    ...
except Exception as e:
    return _create_error_figure(f"图表建立失败: {str(e)}")
```

错误时会显示友善的错误提示图表，而不是抛出异常。

---

## 完整使用示例

### 在 Dash 应用中使用

```python
from dash import Dash, dcc, html, Input, Output
from modules.charts import create_candlestick_chart
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id='stock-selector',
        options=[
            {'label': '台积电', 'value': '2330'},
            {'label': '联发科', 'value': '2454'},
        ],
        value='2330'
    ),
    dcc.Graph(id='stock-chart')
])

@app.callback(
    Output('stock-chart', 'figure'),
    Input('stock-selector', 'value')
)
def update_chart(stock_code):
    return create_candlestick_chart(stock_code, days=60)

if __name__ == '__main__':
    app.run_server(debug=True)
```

---

## 测试命令

```bash
# 测试模块导入
python -c "from modules.charts import create_candlestick_chart; print('OK')"

# 创建简单测试
python -c "
from modules.charts import create_candlestick_chart
fig = create_candlestick_chart('2330', days=30)
fig.write_html('test.html')
print('Chart saved to test.html')
"
```

---

## 注意事项

1. **依赖库**: 需要 `plotly` 和 `pandas`
2. **数据格式**: close_data 必须是 pandas Series，index 为日期
3. **性能**: 数据点过多时（>1000天）可能影响性能
4. **浏览器**: 建议使用 Chrome 或 Firefox 查看互动图表

---

## 问题排查

### 问题 1: 图表显示空白
- 检查数据是否为空
- 确认 pandas Series 的 index 是否为日期格式

### 问题 2: 无法导入模块
- 确认当前目录在项目根目录
- 检查 modules/__init__.py 是否存在

### 问题 3: 中文显示乱码
- 这是 Windows cmd 编码问题，不影响功能
- 在浏览器中查看 HTML 文件时中文正常显示

---

**文档版本**: v1.0
**最后更新**: 2026-01-04
**维护者**: Agent 4 - Charts
