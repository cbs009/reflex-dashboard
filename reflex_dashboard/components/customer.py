import reflex as rx
from ..state.customer import CustomerState
from ..colors import CARD_BG, BORDER_COLOR, TEXT_COLOR
from .customer_behavior import behavioral_metrics_section

def section_header(icon: str, title: str, subtitle: str = None) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(icon, size=18, color=TEXT_COLOR), # Slightly larger icon
            rx.text(title, font_weight="900", color=TEXT_COLOR, font_size="sm", letter_spacing="0.1em"),
            spacing="3",
            align="center"
        ),
        rx.cond(
            subtitle is not None,
            rx.text(subtitle, font_size="10px", color="white", font_weight="bold", letter_spacing="0.05em"), # Changed to white
            rx.fragment()
        ),
        spacing="1",
        width="100%",
        padding_bottom="4",
        border_bottom=f"1px solid {BORDER_COLOR}",
        margin_bottom="4",
        align="center"
    )

def rfm_radar_card() -> rx.Component:
    return rx.box(
        section_header("target", "RFM BEHAVIORAL RADAR", "ACTIVITY VS VALUE DISTRIBUTION"),
        rx.center(
            rx.plotly(data=CustomerState.rfm_radar_chart, height="660px"),
            width="100%",
            height="100%",
        ),
        rx.box(
            rx.text("INTERPRETATION: This radar chart maps the customer base across 5 key dimensions. High scores in 'Recency' and 'Frequency' indicate active engagement, while 'Bundling' shows cross-category purchasing behavior.", font_size="xs", color="white", text_align="center"), # Changed to white
            bg="rgba(255, 255, 255, 0.05)",
            padding="3",
            border_radius="md",
            width="100%",
            margin_top="4"
        ),
        bg=CARD_BG,
        width="100%",
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        padding="6",
        height="100%",
        box_shadow="lg"
    )

def market_basket_row(item: dict) -> rx.Component:
    """Row for Market Basket Grid."""
    return rx.box(
        rx.vstack(
             rx.hstack(
                rx.text(item["pairs"], color="white", font_weight="bold", font_size="sm"),
                rx.spacer(),
                rx.badge(f"LIFT: {item['lift']}X", color_scheme="cyan", variant="solid", size="1"),
                width="100%",
                padding_bottom="2"
            ),
            rx.hstack(
                rx.text("Confidence", color="white", font_size="xs", font_weight="bold"), # Changed to white
                rx.spacer(),
                rx.text(f"{item['confidence']}%", color="white", font_size="xs", font_weight="bold"),
                rx.box(
                    rx.text("SUPPORT", font_size="9px", color="white", font_weight="bold"), # Changed to white
                    rx.text(f"{item['support']}%", font_size="sm", color="white", font_weight="900"),
                    text_align="right",
                    margin_left="4"
                ),
                width="100%",
                align="end"
            ),
             # Progress Bar for Confidence
            rx.box(
                rx.box(
                    width=f"{item['confidence']}%", 
                    height="100%", 
                    bg="linear-gradient(90deg, #F56565 0%, #48BB78 100%)",  # Red to Green Gradient
                    border_radius="full"
                ),
                width="80%", # Bar takes up partial width
                height="6px",
                bg="rgba(255,255,255,0.1)",
                border_radius="full",
                margin_top="1" # Slight spacing
            ),
            spacing="1",
            width="100%",
            padding_x="4" # Added padding for readability
        ),
        bg="rgba(255,255,255,0.03)", # Slight lighter bg for row
        border_radius="md",
        padding="4",
        width="100%",
        border=f"1px solid {BORDER_COLOR}"
    )

def market_basket_card() -> rx.Component:
    return rx.box(
        section_header("shopping-cart", "MARKET BASKET: ASSOCIATION GRID", "CROSS-SELL / BUNDLING AFFINITY"),
        rx.vstack(
            rx.foreach(
                CustomerState.market_basket_data,
                market_basket_row
            ),
            width="100%",
            spacing="3",
            overflow_y="auto",
            height="660px" # Fixed height
        ),
        rx.box(
            rx.text("INTERPRETATION: Identifies products frequently bought together. 'Lift' > 1 indicates a strong positive association. High 'Confidence' means if Product A is bought, Product B is highly likely to be bought.", font_size="xs", color="white", text_align="center"), # Changed to white
            bg="rgba(255, 255, 255, 0.05)",
            padding="3",
            border_radius="md",
            width="100%",
            margin_top="4"
        ),
        bg=CARD_BG,
        width="100%",
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        padding="6",
        height="100%",
         box_shadow="lg"
    )

def revenue_card() -> rx.Component:
    return rx.box(
        section_header("refresh-cw", "NEW VS RETURNING REVENUE"), # Icon roughly matches cycle
        rx.center(
            rx.plotly(data=CustomerState.revenue_trends_chart, height="660px"),
            width="100%",
        ),
         rx.hstack(
            rx.text("Apr", font_size="9px", color="white"), # Changed to white
            rx.spacer(),
            rx.text("Feb (F)", font_size="9px", color="white"), # Changed to white
             width="100%",
             padding_x="2"
        ),
        rx.box(
            rx.text("INTERPRETATION: Tracks revenue contribution from New vs Returning customers over time. A rising Returning Revenue (Purple) trend indicates strong retention and customer loyalty.", font_size="xs", color="white", text_align="center"), # Changed to white
            bg="rgba(255, 255, 255, 0.05)",
            padding="3",
            border_radius="md",
            width="100%",
            margin_top="4"
        ),
        bg=CARD_BG,
        width="100%",
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        padding="6",
        height="100%",
        box_shadow="lg"
    )

def wallet_share_card() -> rx.Component:
    return rx.box(
        section_header("bar-chart", "CUSTOMER WALLET SHARE", "EXPANSION"),
        rx.center(
            rx.plotly(data=CustomerState.wallet_share_chart, height="660px"),
            width="100%",
        ),
        rx.hstack(
             rx.text("Apr", font_size="9px", color="white"), # Changed to white
             rx.spacer(),
             rx.text("Feb (F)", font_size="9px", color="white"), # Changed to white
             width="100%",
             padding_x="2"
        ),
        rx.box(
            rx.text("INTERPRETATION: Shows the percentage of customer spend captured by us. An upward trend suggests we are becoming the primary vendor for our customers, displacing competitors.", font_size="xs", color="white", text_align="center"), # Changed to white
            bg="rgba(255, 255, 255, 0.05)",
            padding="3",
            border_radius="md",
            width="100%",
            margin_top="4"
        ),
        bg=CARD_BG,
        width="100%",
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        padding="6",
        height="100%",
        box_shadow="lg"
    )

def ltv_segments_card() -> rx.Component:
    return rx.box(
        section_header("database", "PREDICTIVE LTV SEGMENTS"),
        rx.center(
            rx.plotly(data=CustomerState.ltv_segments_chart, height="660px"),
            width="100%",
        ),
        # Custom Legend
        rx.hstack(
            rx.hstack(rx.box(width="10px", height="10px", bg="#39FF14"), rx.text("Champions", font_size="9px", color="white"), align="center", spacing="1"), # Changed to white
            rx.hstack(rx.box(width="10px", height="10px", bg="#A0AEC0"), rx.text("Loyal", font_size="9px", color="white"), align="center", spacing="1"), # Changed to white
            rx.hstack(rx.box(width="10px", height="10px", bg="#718096"), rx.text("Potential", font_size="9px", color="white"), align="center", spacing="1"), # Changed to white
            rx.hstack(rx.box(width="10px", height="10px", bg="#FF0000"), rx.text("Churning", font_size="9px", color="white"), align="center", spacing="1"), # Changed to white
            spacing="3",
            width="100%",
            justify="center",
            margin_top="2"
        ),
        rx.box(
            rx.text("INTERPRETATION: Segment distribution based on predicted Lifetime Value (LTV). 'Champions' generate the most value. 'Churning' customers require immediate re-engagement campaigns.", font_size="xs", color="white", text_align="center"), # Changed to white
            bg="rgba(255, 255, 255, 0.05)",
            padding="3",
            border_radius="md",
            width="100%",
            margin_top="4"
        ),
        bg=CARD_BG,
        width="100%",
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        padding="6",
        height="100%",
        box_shadow="lg"
    )

def customer_tab_content() -> rx.Component:
    return rx.vstack(
        rfm_radar_card(),
        market_basket_card(),
        revenue_card(),
        wallet_share_card(),
        ltv_segments_card(),
        behavioral_metrics_section(),
        spacing="9",
        width="100%",
        padding_bottom="40px"
    )
