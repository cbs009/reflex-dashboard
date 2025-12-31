import reflex as rx
from ..colors import CARD_BG, BORDER_COLOR

def table_container(title, subtitle, bg_color, content, footer=None):
    return rx.box(
        rx.flex(
            rx.box(
                rx.text(title, font_size="lg", font_weight="900", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                rx.text(subtitle, font_size="xs", font_weight="bold", color="white", text_align="center", width="100%", letter_spacing="0.05em"),
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            border_bottom=f"1px solid {BORDER_COLOR}",
            bg="rgba(255, 255, 255, 0.02)"
        ),
        content,
        footer if footer is not None else rx.fragment(),
        bg=CARD_BG,
        border_radius="xl",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="0 4px 20px rgba(0, 0, 0, 0.5)", # Deeper shadow
    )

def trend_badge(trend: str, text_color: str = None, font_size: str = "0.7em"):
    """Helper to render the trend badge."""
    if trend is None:
        trend = ""
    if text_color is None:
        trend_color = rx.cond(
            (trend.contains("-")) | (trend.contains("↓")), 
            "#D0312D", # Pitch Red
            "#00C851" # Good Green
        )
    else:
        trend_color = text_color
        
    return rx.el.span(
        f"{trend}", 
        style={
            "backgroundColor": "white",
            "color": trend_color, 
            "fontSize": font_size, 
            "fontWeight": "bold", 
            "padding": "2px 6px",
            "borderRadius": "6px",
            "marginLeft": "8px",
            "position": "relative", 
            "top": "-2px", # Adjusted for alignment in various contexts
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            "whiteSpace": "nowrap",
        }
    )
