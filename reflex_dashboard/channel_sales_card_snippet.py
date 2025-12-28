
def channel_sales_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Channel Wise Sale", size="4", color="black", width="100%", text_align="center", margin_bottom="4"), # Black text on white card
            
            rx.flex(
                # Chart
                rx.box(
                    rx.plotly(data=State.channel_sales_chart, height="300px", config={"displayModeBar": False}),
                    width="50%",
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
                             rx.text(item["channel"], color="gray.600", font_size="sm", font_weight="medium"),
                             rx.spacer(),
                             rx.text(item["value"], color="black", font_size="sm", font_weight="bold"),
                             width="100%",
                             padding_y="1",
                             border_bottom="1px dashed #E2E8F0",
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
        bg="white",
        border_radius="xl",
        box_shadow="lg",
        padding="6",
        width="100%"
    )
