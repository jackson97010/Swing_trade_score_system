"""
側邊導航欄元件 - 現代化扁平設計
"""

from dash import html, dcc
from .styles import COLORS, SIDEBAR_STYLES, get_nav_item_style


# 導航項目定義
NAV_ITEMS = [
    {'path': '/ranking', 'icon': '📈', 'label': '每日排行榜'},
    {'path': '/selection', 'icon': '🎯', 'label': '選股評分系統'},
    {'path': '/sector', 'icon': '🔥', 'label': '族群熱力圖'},
    {'path': '/realtime', 'icon': '📡', 'label': '即時戰情室'},
]


def create_nav_item(item: dict, current_path: str) -> html.Div:
    """
    建立單個導航項目

    Args:
        item: 導航項目資訊
        current_path: 當前頁面路徑

    Returns:
        html.Div: 導航項目元件
    """
    # 判斷是否為當前頁面
    is_active = (current_path == item['path']) or \
                (item['path'] == '/ranking' and current_path == '/')

    return dcc.Link(
        html.Div([
            html.Span(item['icon'], style={
                'marginRight': '12px',
                'fontSize': '16px',
                'opacity': '0.9' if is_active else '0.7',
            }),
            html.Span(item['label']),
        ], style=get_nav_item_style(is_active)),
        href=item['path'],
        style={'textDecoration': 'none'},
    )


def create_sidebar(current_path: str = '/') -> html.Div:
    """
    建立側邊導航欄

    Args:
        current_path: 當前頁面路徑

    Returns:
        html.Div: 側邊導航欄元件
    """
    return html.Div([
        # Logo 區域
        html.Div([
            html.Span('📊', style={'fontSize': '22px'}),
            html.Span('台股戰情室', style={'letterSpacing': '1px'}),
        ], style=SIDEBAR_STYLES['logo']),

        # 分隔線
        html.Div(style={
            'height': '1px',
            'backgroundColor': COLORS['bg_hover'],
            'margin': '0 0 20px 0',
        }),

        # 導航選單
        html.Nav([
            create_nav_item(item, current_path)
            for item in NAV_ITEMS
        ], style={'flex': '1'}),

        # 底部資訊
        html.Div([
            html.Div([
                html.Span('更新時間', style={
                    'fontSize': '11px',
                    'color': COLORS['text_sidebar'],
                    'textTransform': 'uppercase',
                    'letterSpacing': '0.5px',
                }),
            ], style={'marginBottom': '4px'}),
            html.Div(id='sidebar-update-time', children='--', style={
                'fontSize': '13px',
                'color': COLORS['text_sidebar_active'],
                'fontWeight': '500',
            }),
            html.Div([
                html.Span('v1.0', style={
                    'fontSize': '11px',
                    'color': COLORS['text_sidebar'],
                    'marginTop': '16px',
                    'display': 'block',
                }),
            ]),
        ], style=SIDEBAR_STYLES['footer']),

    ], style=SIDEBAR_STYLES['container'])


# 匯出函數
__all__ = ['create_sidebar']
