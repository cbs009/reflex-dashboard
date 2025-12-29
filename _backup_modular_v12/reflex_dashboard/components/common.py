import reflex as rx
from ..constants import CARD_BG, BORDER_COLOR, TEXT_COLOR, TEXT_SECONDARY, ACCENT_BLUE

def table_container(title: str, content: rx.Component, bg_header: str = "slate.800", text_header: str = "white"):
    return rx.box(
        rx.box(
            rx.text(title, font_size="10px", font_weight="black", text_align="center", padding_y="2", text_transform="uppercase", letter_spacing="widest", color="black"),
            bg="orange.400", border_bottom=f"1px solid {BORDER_COLOR}", width="100%"
        ),
        rx.box(
            content,
            padding="0",
            width="100%",
        ),
        background_color="white",
        border=f"1px solid {BORDER_COLOR}",
        shadow="sm",
        overflow="hidden",
        width="100%",
    )

def premium_metric_card(title: str, value: str, sub: str, icon: str, grad: str, badge: str = None):
    # Colors from reference image
    bg_colors = {
        "indigo": "#6366f1",
        "emerald": "#10b981",
        "amber": "#f59e0b",
        "rose": "#e11d48",
        "blue": "#3b82f6"
    }
    bg_color = bg_colors.get(grad, bg_colors["blue"])
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(title, font_size="11px", font_weight="900", text_transform="uppercase", letter_spacing="0.12em", color="white", opacity=0.8),
                rx.box(
                    rx.el.i(class_name=f"{icon} text-white opacity-40 text-[14px]"),
                    bg="rgba(255,255,255,0.2)", padding="2.5", border_radius="12px"
                ),
                width="100%",
                justify_content="between",
                align_items="start"
            ),
            rx.vstack(
                rx.text(value, font_size="6xl", font_weight="900", letter_spacing="[-0.04em]", line_height="0.9", color="white"),
                rx.hstack(
                    rx.cond(
                        badge is not None,
                        # Specific box for the % trend as seen in reference
                        rx.box(
                            rx.text(badge, font_size="10px", font_weight="900", color="white", letter_spacing="-0.01em"),
                            bg="rgba(255,255,255,0.2)", padding_x="3", padding_y="1", border_radius="8px", margin_right="3"
                        ),
                        rx.fragment()
                    ),
                    rx.text(sub, font_size="11px", font_weight="900", text_transform="uppercase", color="white", opacity=0.9, letter_spacing="0.08em"),
                    align_items="center",
                    margin_top="4"
                ),
                align_items="start",
                spacing="0",
                margin_top="3"
            ),
            height="100%",
            width="100%",
            align_items="start",
            spacing="0"
        ),
        padding="10",
        border_radius="2.5rem",
        background_color=bg_color,
        height="220px", # Slightly more compact
        shadow="0 30px 60px -12px rgba(0, 0, 0, 0.25)",
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        _hover={"transform": "translateY(-6px)", "shadow": "0 40px 70px -15px rgba(0, 0, 0, 0.3)"},
        width="100%"
    )

def kpi_card(title: str, value: str, trend: str, icon: str, color_scheme: str, bg_color: str = CARD_BG, align: str = "start", value_size: str = "6", title_size: str = "2", bottom_left: str = None, bottom_right: str = None, bottom_left_trend: str = None, bottom_right_trend: str = None, bottom_left_icon: str = None, bottom_right_icon: str = None, trend_inline: bool = False, subtitle: str = None):
    # Keep legacy kpi_card for compatibility if needed, but we prefer premium_metric_card now
    return premium_metric_card(title, value, subtitle if subtitle else "", f"fa-solid fa-{icon}", "blue", trend)
