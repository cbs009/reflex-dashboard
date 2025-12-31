import reflex as rx
from ..state import State
from ..colors import CARD_BG, BORDER_COLOR, TEXT_COLOR
from .common import trend_badge

def kpi_card(title: str, value: str, trend: str, icon: str, color_scheme: str, bg_color: str = CARD_BG, align: str = "start", value_size: str = "6", title_size: str = "2", bottom_left: str = None, bottom_right: str = None, bottom_left_trend: str = None, bottom_right_trend: str = None, bottom_left_icon: str = None, bottom_right_icon: str = None, trend_inline: bool = False, subtitle: str = None):
    """
    A modern KPI card with:
    - Icon on the left (or top-right)
    - Value prominent
    - Title subtle
    - Subtitle option
    - Trend indicator
    - Optional bottom corners
    - Optional inline trend
    """
    # Color mapping for trends
    trend_color = rx.cond(
        (trend.contains("-")) | (trend.contains("↓")), 
        "#D0312D", # Pitch Red
        "#68D391" # Lighter green for dark mode
    )
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(title, size=title_size, font_weight="900", color="white", letter_spacing="0.05em", text_transform="uppercase"), # Uppercase title
                    rx.cond(
                         subtitle is not None,
                         rx.text(subtitle, font_size="xs", color="white", font_weight="bold"),
                         rx.fragment()
                    ),
                    rx.heading(
                        value, 
                        rx.cond(
                            trend_inline,
                            rx.box(trend_badge(trend, font_size="0.5em"), display="inline-block", style={"verticalAlign": "middle", "marginTop": "-10px", "marginLeft": "8px"}),
                            rx.fragment()
                        ),
                        size=value_size, 
                        font_weight="900", 
                        color="white",
                        letter_spacing="-0.02em" # Tight spacing for numbers
                    ),
                    align_items=align,
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    align == "start",
                    rx.box(
                         rx.spacer(),
                         rx.icon(icon, size=28, color=color_scheme, stroke_width=1.5), # Thinner stroke for elegance
                    ),
                    rx.fragment() 
                ),
                width="100%",
                align_items="center" if align == "center" else "start",
                justify_content="center" if align == "center" else "start",
            ),
            
            rx.cond(
                not trend_inline,
                rx.hstack(
                    rx.text(trend, color=trend_color, font_size="sm", font_weight="bold", text_align=align, width="100%"),
                    width="100%",
                    justify_content=align, 
                ),
                rx.fragment()
            ),
            
            # Bottom Corner Content (for Total Sales)
            rx.cond(
                bottom_left is not None,
                rx.flex(
                    rx.hstack(
                        rx.icon(bottom_left_icon, size=16, color="gray.400") if bottom_left_icon is not None else rx.fragment(),
                        rx.text(bottom_left, font_size="sm", color="white", font_weight="bold"),
                        trend_badge(bottom_left_trend, font_size="0.75em") if bottom_left_trend is not None else rx.fragment(),
                        align="center",
                        spacing="2"
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.icon(bottom_right_icon, size=16, color="gray.400") if bottom_right_icon is not None else rx.fragment(),
                        rx.text(bottom_right, font_size="sm", color="white", font_weight="bold"),
                        trend_badge(bottom_right_trend, font_size="0.75em") if bottom_right_trend is not None else rx.fragment(),
                        align="center",
                        spacing="2"
                    ),
                    width="100%",
                    justify="between",
                    padding_top="4",
                    border_top=f"1px solid {BORDER_COLOR}",
                    margin_top="2"
                ),
                rx.fragment()
            ),
            
            spacing="3",
            align_items=align,
        ),
        padding="6", 
        bg=bg_color,
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        width="100%",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        transition="all 0.2s",
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "border_color": color_scheme
        },
    )

def card_avg_monthly_sale():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("AVG. MONTHLY SALE", color="white", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                rx.icon("chart-bar", color="#FF9966", size=20),
                width="100%",
                align="center",
                justify="center",
                spacing="2"
            ),
            rx.hstack(
                rx.heading(State.average_monthly_sale, color="white", size="8", font_weight="900", letter_spacing="-0.02em"),
                rx.badge("↗ 14.9%", color_scheme="green", variant="surface", size="1"),
                align="baseline",
                spacing="3",
                justify="center",
                width="100%"
            ),
            rx.spacer(),
            rx.hstack(
                 rx.hstack(
                     rx.text("B2B", color="#FF9966", font_size="xs", font_weight="900"),
                     rx.text(State.avg_monthly_b2b, color="white", font_size="xs", font_weight="bold"),
                     align="center",
                     spacing="1"
                 ),
                 rx.spacer(),
                 rx.hstack(
                     rx.text("B2C", color="#63b3ed", font_size="xs", font_weight="900"),
                     rx.text(State.avg_monthly_b2c, color="white", font_size="xs", font_weight="bold"),
                     align="center",
                     spacing="1"
                 ),
                 width="100%",
                 align="center",
                 padding_top="4",
                 border_top=f"1px solid {BORDER_COLOR}"
            ),
            height="100%",
            justify="between",
            align_items="center",
            spacing="1"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #FF9966", # Orange Accent
        border_radius="xl",
        padding="24px",
        width="100%",
        height="180px",
        box_shadow="lg"
    )

def card_daily_velocity():
    return rx.box(
         rx.vstack(
            rx.hstack(
                rx.text("DAILY SALES VELOCITY", color="white", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                rx.icon("zap", color="#63b3ed", size=20),
                width="100%",
                align="center",
                justify="center",
                spacing="2"
            ),
            rx.heading(State.daily_sales_velocity_data["total"], color="white", size="8", font_weight="900", letter_spacing="-0.02em"),
            rx.spacer(),
            rx.hstack(
                 rx.hstack(
                     rx.text("B2B", color="#FF9966", font_size="xs", font_weight="900"),
                     rx.text(State.daily_sales_velocity_data["b2b"], color="white", font_size="xs", font_weight="bold"),
                     align="center",
                     spacing="1"
                 ),
                 rx.spacer(),
                 rx.hstack(
                     rx.text("B2C", color="#63b3ed", font_size="xs", font_weight="900"),
                     rx.text(State.daily_sales_velocity_data["b2c"], color="white", font_size="xs", font_weight="bold"),
                     align="center",
                     spacing="1"
                 ),
                 width="100%",
                 align="center",
                 padding_top="4",
                 border_top=f"1px solid {BORDER_COLOR}"
            ),
            height="100%",
            justify="between",
            align_items="center",
            spacing="1"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #63b3ed", # Blue Accent
        border_radius="xl",
        padding="24px",
        width="100%",
        height="180px",
        box_shadow="lg"
    )

def card_returns_invoices():
    return rx.box(
        rx.vstack(
            rx.hstack(
                # Left: Returns (CENTERED)
                rx.box(
                    rx.vstack(
                        rx.hstack(rx.icon("rotate-ccw", color="red", size=14), rx.text("RETURNS", color="white", font_weight="bold", font_size="xs", letter_spacing="0.05em"), spacing="2", align="center"),
                        rx.heading(State.return_metrics["count"], color="white", size="6", font_weight="900"),
                        rx.hstack(
                             rx.text(State.return_metrics["rate_pct"], color="red", font_size="xs", font_weight="bold"),
                             rx.text(State.return_metrics["val_cr"], color="white", font_size="xs"),
                             spacing="2"
                        ),
                        align_items="center", # Center align internal content
                        spacing="1",
                        width="100%"
                    ),
                    flex="1",
                    display="flex",
                    justify_content="center", 
                    width="100%"
                ),
                 # Right: Invoices (RIGHT ALIGNED BLOCK, EXTREME RIGHT)
                rx.box(
                    rx.vstack(
                        rx.hstack(rx.icon("file-text", color="white", size=14), rx.text("INVOICES", color="white", font_weight="bold", font_size="xs", letter_spacing="0.05em"), spacing="2", align="center"),
                        rx.heading(State.invoice_stats["count"], color="white", size="6", font_weight="900"),
                        rx.hstack(
                            rx.text("Avg", color="white", font_size="xs"),
                            rx.text(State.invoice_stats["daily_avg"], color="white", font_size="xs", font_weight="bold"),
                            spacing="2"
                        ),
                        align_items="end", # Right align internal content
                        spacing="1",
                        width="100%"
                    ),
                    flex="1", 
                    display="flex",
                    justify_content="end", # Push to right
                    width="100%"
                ),
                width="100%",
                align_items="center",
                justify="between" # Ensure they are spread out
            ),
            # Removed B2C RETURN RATE section as requested
            spacing="3",
            width="100%",
            height="100%", # Fill height
            justify="center", # Center vertically
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #e53935", # Red Accent
        border_radius="xl",
        padding="24px", # Explicit padding
        width="100%",
        height="180px", # Consistent height
        box_shadow="lg"
    )

def card_pareto():
    return rx.box(
        rx.vstack(
                rx.center(
                     rx.vstack(
                        rx.text("PARETO (80% SALE)", color="white", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                        rx.heading(
                            State.pareto_stats["count_80"], 
                            color="white", 
                            size="8", 
                            font_weight="900",
                            letter_spacing="-0.02em"
                        ),
                        spacing="1",
                        align_items="center",
                        width="100%"
                     ),
                     width="100%"
                ),
                 rx.box(
                    rx.vstack(
                        rx.foreach(
                            State.pareto_top_products,
                            lambda item: rx.hstack(
                                rx.badge(item["rank"], variant="solid", color_scheme="yellow", border_radius="full", size="1"),
                                rx.text(item["name"], color="white", font_size="xs", no_of_lines=1, width="40%"), 
                                rx.spacer(),
                                rx.text(item["value_cr"], color="white", font_size="xs", font_weight="bold"),
                                rx.spacer(),
                                rx.text(item["pct"], color="white", font_size="xs", font_weight="bold"),
                                width="100%",
                                padding_y="1",
                                border_bottom=f"1px solid {BORDER_COLOR}"
                            )
                        ),
                        width="100%",
                        spacing="1"
                    ),
                    width="100%",
                    bg="rgba(255,255,255,0.02)",
                    border_radius="md",
                    padding="4"
                ),
            rx.box( # Wrapper for spacing
                rx.text(
                    rx.text.span("Products driving 80% of sales ", font_weight="bold", color="white"),
                    rx.text.span(State.pareto_stats["pct_catalog"], font_weight="bold", color="white"),
                    font_size="xs", 
                    text_align="center"
                ),
                padding_top="4", # Added padding to push it down
                width="100%",
                display="flex",
                justify_content="center"
            ),
            spacing="1", # Reduced spacing since we use manual padding
            align_items="center",
            width="100%"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left=f"4px solid {rx.color('yellow', 9)}",
         # Gradient background override
        background=f"linear-gradient(135deg, {CARD_BG} 0%, rgba(80, 40, 100, 0.3) 100%)",
        border_radius="xl",
        padding="24px",
        width="100%",
        box_shadow="lg"
    )
