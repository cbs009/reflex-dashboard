import reflex as rx
from ..state import State
from ..colors import CARD_BG, TEXT_COLOR

# Channel Sales Card
def channel_sales_card() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Channel Wise Sale", size="4", color=TEXT_COLOR, width="100%", text_align="center", margin_bottom="4"), 
            
            rx.flex(
                # Chart
                rx.box(
                    rx.plotly(data=State.channel_sales_chart, height="580px", config={"displayModeBar": False}),
                    width="55%", # Slightly increased width allocation
                    min_width="300px",
                    display="flex",
                    justify_content="center",
                    align_items="center"
                ),
                
                # Custom Legend
                rx.vstack(
                    rx.foreach(
                        State.channel_sales_stats,
                        lambda item: rx.hstack(
                             rx.box(width="10px", height="10px", border_radius="50%", bg=item["color"]),
                             rx.text(item["channel"], color="white", font_size="sm", font_weight="medium"),
                             rx.spacer(),
                             rx.text(item["value"], color="white", font_size="sm", font_weight="bold"),
                             rx.text(item["pct"], color="white", font_size="xs", font_weight="medium"),
                             width="100%",
                             padding_y="1",
                             border_bottom="1px dashed #4A5568",
                             align="center"
                        )
                    ),
                    width="50%",
                    min_width="250px",
                    padding_left="4",
                    spacing="0"
                ),
                
                width="100%",
                flex_wrap="wrap",
                align="center",
                justify="center"
            ),
            width="100%",
        ),
        bg="#000000",
        border_radius="xl",
        box_shadow="lg",
        border="1px solid #4A5568",
        padding="6",
        width="100%",
        height="100%"
    )
