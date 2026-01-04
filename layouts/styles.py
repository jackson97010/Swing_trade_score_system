"""
共用樣式定義 - 現代化 UI 設計
參考 FinLab 風格 + Tailwind CSS 配色
"""

# =====================
# 配色方案 (Color Palette)
# =====================
COLORS = {
    # 背景色
    'bg_page': '#F3F4F6',           # 頁面淺灰背景
    'bg_sidebar': '#1E293B',        # 側邊欄深靛藍
    'bg_card': '#FFFFFF',           # 卡片白色
    'bg_hover': '#334155',          # Sidebar hover 深色
    'bg_input': '#F9FAFB',          # 輸入框背景

    # 文字色
    'text_primary': '#1F2937',      # 主要文字深灰
    'text_secondary': '#6B7280',    # 次要文字
    'text_muted': '#9CA3AF',        # 更淡的文字
    'text_sidebar': '#94A3B8',      # 側邊欄淺灰文字
    'text_sidebar_active': '#FFFFFF',  # 側邊欄選中白字

    # 強調色
    'accent': '#3B82F6',            # 主色調藍色
    'accent_light': '#60A5FA',      # 淺藍
    'accent_dark': '#2563EB',       # 深藍

    # 漲跌色 (柔和)
    'up': '#EF4444',                # 漲 - 紅色
    'up_soft': '#F87171',           # 漲 - 珊瑚紅 (柔和)
    'up_bg': '#FEF2F2',             # 漲背景
    'down': '#10B981',              # 跌 - 綠色
    'down_soft': '#34D399',         # 跌 - 翠綠 (柔和)
    'down_bg': '#ECFDF5',           # 跌背景

    # 其他
    'purple': '#8B5CF6',            # 紫色
    'purple_bg': '#F5F3FF',         # 紫色背景
    'orange': '#F59E0B',            # 橙色
    'orange_bg': '#FFFBEB',         # 橙色背景

    # 邊框
    'border': '#E5E7EB',            # 淺灰邊框
    'border_light': '#F3F4F6',      # 更淺邊框
    'border_dark': '#D1D5DB',       # 深一點的邊框
}

# =====================
# 側邊欄樣式
# =====================
SIDEBAR_STYLES = {
    # 側邊欄容器
    'container': {
        'width': '240px',
        'backgroundColor': COLORS['bg_sidebar'],
        'padding': '24px 16px',
        'position': 'fixed',
        'left': 0,
        'top': 0,
        'bottom': 0,
        'display': 'flex',
        'flexDirection': 'column',
        'zIndex': 1000,
    },

    # Logo 區域
    'logo': {
        'color': COLORS['text_sidebar_active'],
        'fontSize': '18px',
        'fontWeight': '600',
        'marginBottom': '32px',
        'paddingLeft': '12px',
        'display': 'flex',
        'alignItems': 'center',
        'gap': '10px',
        'letterSpacing': '0.5px',
    },

    # 導航項目 (基礎)
    'nav_item_base': {
        'display': 'flex',
        'alignItems': 'center',
        'padding': '12px 16px',
        'textDecoration': 'none',
        'borderRadius': '8px',
        'marginBottom': '4px',
        'cursor': 'pointer',
        'transition': 'all 0.15s ease',
        'fontSize': '14px',
        'fontWeight': '500',
        'border': 'none',
        'width': '100%',
        'textAlign': 'left',
    },

    # 導航項目 (未選中)
    'nav_item': {
        'color': COLORS['text_sidebar'],
        'backgroundColor': 'transparent',
    },

    # 導航項目 (選中)
    'nav_item_active': {
        'color': COLORS['text_sidebar_active'],
        'backgroundColor': COLORS['bg_hover'],
        'borderLeft': f'3px solid {COLORS["accent"]}',
        'paddingLeft': '13px',  # 補償 border 寬度
    },

    # 底部資訊
    'footer': {
        'marginTop': 'auto',
        'paddingLeft': '12px',
        'paddingTop': '20px',
        'borderTop': f'1px solid {COLORS["bg_hover"]}',
    },

    # 版本文字
    'version': {
        'color': COLORS['text_sidebar'],
        'fontSize': '12px',
    },
}

# =====================
# 主內容區樣式
# =====================
MAIN_STYLES = {
    # 主內容容器
    'container': {
        'marginLeft': '240px',
        'padding': '24px 32px',
        'backgroundColor': COLORS['bg_page'],
        'minHeight': '100vh',
    },

    # 頁面標題
    'page_title': {
        'fontSize': '24px',
        'fontWeight': '600',
        'color': COLORS['text_primary'],
        'marginBottom': '8px',
        'letterSpacing': '-0.5px',
    },

    # 頁面副標題
    'page_subtitle': {
        'fontSize': '14px',
        'color': COLORS['text_secondary'],
        'marginBottom': '24px',
    },
}

# =====================
# 卡片樣式
# =====================
CARD_STYLES = {
    # 基礎卡片
    'base': {
        'backgroundColor': COLORS['bg_card'],
        'borderRadius': '12px',
        'padding': '24px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)',
        'marginBottom': '24px',
    },

    # 卡片標題
    'title': {
        'fontSize': '16px',
        'fontWeight': '600',
        'color': COLORS['text_primary'],
        'marginBottom': '16px',
        'display': 'flex',
        'alignItems': 'center',
        'gap': '8px',
    },

    # 統計卡片
    'stat': {
        'backgroundColor': COLORS['bg_card'],
        'borderRadius': '12px',
        'padding': '20px 24px',
        'boxShadow': '0 1px 3px rgba(0,0,0,0.1)',
        'textAlign': 'center',
        'flex': '1',
        'minWidth': '150px',
    },

    # 統計數字
    'stat_number': {
        'fontSize': '28px',
        'fontWeight': '700',
        'marginBottom': '4px',
    },

    # 統計標籤
    'stat_label': {
        'fontSize': '13px',
        'color': COLORS['text_secondary'],
    },
}

# =====================
# 表格樣式 (DataTable)
# =====================
TABLE_STYLES = {
    # 表格容器
    'container': {
        'overflowX': 'auto',
    },

    # 單元格基礎樣式
    'cell': {
        'textAlign': 'left',
        'padding': '14px 16px',
        'fontFamily': '"Noto Sans TC", "Inter", -apple-system, sans-serif',
        'fontSize': '14px',
        'border': 'none',
        'borderBottom': f'1px solid {COLORS["border_light"]}',
    },

    # 表頭樣式
    'header': {
        'backgroundColor': COLORS['bg_input'],
        'color': COLORS['text_primary'],
        'fontWeight': '600',
        'fontSize': '13px',
        'borderBottom': f'2px solid {COLORS["border"]}',
        'textTransform': 'none',
    },

    # 數據行樣式
    'data': {
        'backgroundColor': COLORS['bg_card'],
        'color': COLORS['text_primary'],
    },

    # 條件樣式
    'conditional': [
        # hover 效果 (AG Grid 會處理，DataTable 需要特別設定)
        {
            'if': {'state': 'active'},
            'backgroundColor': COLORS['bg_page'],
        },
    ],
}

# =====================
# 按鈕樣式
# =====================
BUTTON_STYLES = {
    # 主要按鈕
    'primary': {
        'padding': '10px 20px',
        'fontSize': '14px',
        'fontWeight': '500',
        'backgroundColor': COLORS['accent'],
        'color': 'white',
        'border': 'none',
        'borderRadius': '8px',
        'cursor': 'pointer',
        'transition': 'all 0.15s ease',
    },

    # 次要按鈕
    'secondary': {
        'padding': '10px 20px',
        'fontSize': '14px',
        'fontWeight': '500',
        'backgroundColor': COLORS['bg_card'],
        'color': COLORS['text_primary'],
        'border': f'1px solid {COLORS["border"]}',
        'borderRadius': '8px',
        'cursor': 'pointer',
        'transition': 'all 0.15s ease',
    },
}

# =====================
# 輸入框樣式
# =====================
INPUT_STYLES = {
    'base': {
        'padding': '10px 14px',
        'fontSize': '14px',
        'border': f'1px solid {COLORS["border"]}',
        'borderRadius': '8px',
        'backgroundColor': COLORS['bg_card'],
        'color': COLORS['text_primary'],
        'outline': 'none',
        'transition': 'border-color 0.15s ease',
    },
}

# =====================
# 徽章樣式 (分數顯示)
# =====================
BADGE_STYLES = {
    # 基礎徽章
    'base': {
        'display': 'inline-flex',
        'alignItems': 'center',
        'justifyContent': 'center',
        'padding': '4px 12px',
        'borderRadius': '16px',
        'fontSize': '13px',
        'fontWeight': '600',
    },

    # 滿分 70
    'score_70': {
        'backgroundColor': COLORS['up_bg'],
        'color': COLORS['up'],
    },

    # 60分以上
    'score_60': {
        'backgroundColor': '#EFF6FF',
        'color': COLORS['accent_dark'],
    },

    # 50分以上
    'score_50': {
        'backgroundColor': COLORS['purple_bg'],
        'color': COLORS['purple'],
    },

    # 其他分數
    'score_default': {
        'backgroundColor': COLORS['bg_page'],
        'color': COLORS['text_secondary'],
    },
}

# =====================
# 工具函數
# =====================
def merge_styles(*style_dicts):
    """合併多個樣式字典"""
    result = {}
    for style in style_dicts:
        result.update(style)
    return result


def get_nav_item_style(is_active: bool) -> dict:
    """取得導航項目樣式"""
    base = SIDEBAR_STYLES['nav_item_base'].copy()
    if is_active:
        base.update(SIDEBAR_STYLES['nav_item_active'])
    else:
        base.update(SIDEBAR_STYLES['nav_item'])
    return base


def get_score_badge_style(score: int) -> dict:
    """根據分數取得徽章樣式"""
    base = BADGE_STYLES['base'].copy()
    if score >= 70:
        base.update(BADGE_STYLES['score_70'])
    elif score >= 60:
        base.update(BADGE_STYLES['score_60'])
    elif score >= 50:
        base.update(BADGE_STYLES['score_50'])
    else:
        base.update(BADGE_STYLES['score_default'])
    return base


# 匯出所有
__all__ = [
    'COLORS',
    'SIDEBAR_STYLES',
    'MAIN_STYLES',
    'CARD_STYLES',
    'TABLE_STYLES',
    'BUTTON_STYLES',
    'INPUT_STYLES',
    'BADGE_STYLES',
    'merge_styles',
    'get_nav_item_style',
    'get_score_badge_style',
]
