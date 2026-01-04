# Swing_trade_score_system

台股波段選股評分系統

## 評分標準 (總分 70 分)

### 1. 技術面動能 (40分)
| 指標 | 配分 | 判斷條件 |
|------|------|----------|
| 均線多頭排列 | +20 | MA10 > MA20 > MA60 |
| MACD 強勢 | +20 | MACD > 0 且向上彎 |

### 2. 基本面輔助 (30分)
| 指標 | 配分 | 判斷條件 |
|------|------|----------|
| 營收成長 | +10 | 月營收 YoY > 20% |
| 產業趨勢 | +10 | 所屬族群為過去10天漲幅前五大 |
| 成交值活絡 | +10 | 過去10天內有任一天成交值進入前30大 |

### 篩選條件
- 月均成交值 >= 3億

## 使用方式

```bash
conda activate my_project

# 方法1: 即時計算 (較慢，每次從 API 抓資料)
python score_calculator.py
python score_calculator.py 2024-12-20

# 方法2: 預計算 + 快速查詢 (推薦)
# Step 1: 預計算最近 N 天的資料 (只需執行一次)
python precompute_scores.py 60

# Step 2: 快速查詢 (從 parquet 讀取，瞬間完成)
python query_scores.py
python query_scores.py 2024-12-20
python query_scores.py --list  # 列出可用日期
```

## 檔案說明

| 檔案 | 說明 |
|------|------|
| `score_calculator.py` | 即時計算評分 (較慢) |
| `precompute_scores.py` | 批次預計算並存成 parquet |
| `query_scores.py` | 從 parquet 快速查詢 |

## 依賴套件
- finlab
- pandas
- numpy
- pyarrow (for parquet)
