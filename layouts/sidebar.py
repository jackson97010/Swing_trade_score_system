"""
側邊導航欄元件
"""

from dash import html, dcc


def create_sidebar(current_path: str = '/') -> html.Div:
    """
    建立側邊導航欄

    Args:
        current_path: 當前頁面路徑

    Returns:
        html.Div: 側邊導航欄元件
    """
    return html.Div([
        # 標題
        html.H2(
            "台股戰情室",
            style={
                'color': '#ffffff',
                'margin-bottom': '30px',
                'text-align': 'center',
                'font-weight': 'bold'
            }
        ),

        html.Hr(style={'border-color': '#444', 'margin': '20px 0'}),

        # 導航按鈕組
        html.Div([
            # 即時戰情室按鈕
            dcc.Link(
                html.Button(
                    [
                        html.Span("🔴 ", style={'font-size': '18px'}),
                        html.Span("即時戰情室")
                    ],
                    style={
                        'width': '100%',
                        'padding': '15px',
                        'margin-bottom': '15px',
                        'background-color': '#d32f2f' if current_path == '/realtime' else '#424242',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '8px',
                        'cursor': 'pointer',
                        'font-size': '16px',
                        'font-weight': 'bold' if current_path == '/realtime' else 'normal',
                        'transition': 'all 0.3s',
                        'box-shadow': '0 2px 4px rgba(0,0,0,0.2)' if current_path == '/realtime' else 'none'
                    }
                ),
                href='/realtime',
                style={'text-decoration': 'none'}
            ),

            # 選股評分系統按鈕
            dcc.Link(
                html.Button(
                    [
                        html.Span("📊 ", style={'font-size': '18px'}),
                        html.Span("選股評分系統")
                    ],
                    style={
                        'width': '100%',
                        'padding': '15px',
                        'background-color': '#1976d2' if current_path in ['/selection', '/'] else '#424242',
                        'color': 'white',
                        'border': 'none',
                        'border-radius': '8px',
                        'cursor': 'pointer',
                        'font-size': '16px',
                        'font-weight': 'bold' if current_path in ['/selection', '/'] else 'normal',
                        'transition': 'all 0.3s',
                        'box-shadow': '0 2px 4px rgba(0,0,0,0.2)' if current_path in ['/selection', '/'] else 'none'
                    }
                ),
                href='/selection',
                style={'text-decoration': 'none'}
            )
        ], style={'margin-top': '20px'}),

        # 版本資訊
        html.Div([
            html.Hr(style={'border-color': '#444', 'margin': '40px 0 20px 0'}),
            html.P(
                "v1.0.0 | 2026",
                style={
                    'color': '#888',
                    'font-size': '12px',
                    'text-align': 'center',
                    'margin-top': '40px'
                }
            )
        ], style={'position': 'absolute', 'bottom': '20px', 'width': 'calc(100% - 40px)'})

    ], style={
        'position': 'relative',
        'height': '100%'
    })


# 匯出函數
__all__ = ['create_sidebar']
