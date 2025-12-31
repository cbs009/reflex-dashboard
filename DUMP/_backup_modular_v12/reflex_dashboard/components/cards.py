import reflex as rx
from ..state.metrics import MetricsState as State
from ..constants import CARD_BG, BORDER_COLOR, TEXT_COLOR

def card_avg_monthly_sale():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("AVG. MONTHLY SALE", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                rx.spacer(),
                rx.icon("chart-bar", color="#FF9966", size=20),
                width="100%", align="center",
            ),
            rx.hstack(
                rx.heading(State.average_monthly_sale, color="white", size="8", font_weight="900", letter_spacing="-0.02em"),
                rx.badge("↗ 14.9%", color_scheme="green", variant="surface", size="1"),
                align="baseline", spacing="3"
            ),
            rx.spacer(),
            rx.hstack(
                 rx.icon("briefcase", color="gray.500", size=14),
                 rx.text(State.avg_monthly_b2b, color="gray.300", font_size="xs", font_weight="bold"),
                 rx.spacer(),
                 rx.icon("shopping-cart", color="gray.500", size=14),
                 rx.text(State.avg_monthly_b2c, color="gray.300", font_size="xs", font_weight="bold"),
                 width="100%", align="center", padding_top="4", border_top=f"1px solid {BORDER_COLOR}"
            ),
            height="100%", justify="between", align_items="start", spacing="1"
        ),
        bg=CARD_BG, border=f"1px solid {BORDER_COLOR}", border_left="4px solid #FF9966", border_radius="xl", padding="24px", width="100%", height="180px", box_shadow="lg"
    )

def card_daily_velocity():
    return rx.box(
         rx.vstack(
            rx.hstack(
                rx.text("DAILY SALES VELOCITY", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                rx.spacer(), rx.icon("zap", color="#63b3ed", size=20), width="100%", align="center",
            ),
            rx.heading(State.daily_sales_velocity_data["total"], color="white", size="8", font_weight="900", letter_spacing="-0.02em"),
            rx.spacer(),
            rx.hstack(
                 rx.icon("briefcase", color="gray.500", size=14),
                 rx.text(State.daily_sales_velocity_data["b2b"], color="gray.300", font_size="xs", font_weight="bold"),
                 rx.spacer(),
                 rx.icon("shopping-cart", color="gray.500", size=14),
                 rx.text(State.daily_sales_velocity_data["b2c"], color="gray.300", font_size="xs", font_weight="bold"),
                 width="100%", align="center", padding_top="4", border_top=f"1px solid {BORDER_COLOR}"
            ),
            height="100%", justify="between", align_items="start", spacing="1"
        ),
        bg=CARD_BG, border=f"1px solid {BORDER_COLOR}", border_left="4px solid #63b3ed", border_radius="xl", padding="24px", width="100%", height="180px", box_shadow="lg"
    )

def card_returns_invoices():
    return rx.box(
        rx.vstack(
            rx.flex(
                rx.box(
                    rx.vstack(
                        rx.hstack(rx.icon("rotate-ccw", color="red", size=14), rx.text("RETURNS", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.05em")),
                        rx.heading(State.return_metrics["count"], color="white", size="6", font_weight="900"),
                        rx.hstack(rx.text(State.return_metrics["rate_pct"], color="red", font_size="xs", font_weight="bold"), rx.text(State.return_metrics["val_cr"], color="gray.500", font_size="xs"), spacing="2"),
                        align_items="start", spacing="1", width="100%"
                    ),
                    flex="1",
                ),
                rx.divider(orientation="vertical", height="auto", margin_x="4", border_color=BORDER_COLOR),
                rx.box(
                    rx.vstack(
                        rx.hstack(rx.icon("file-text", color="gray.400", size=14), rx.text("INVOICES", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.05em")),
                        rx.heading(State.invoice_stats["count"], color="white", size="6", font_weight="900"),
                        rx.hstack(rx.text("Avg", color="gray.500", font_size="xs"), rx.text(State.invoice_stats["daily_avg"], color="white", font_size="xs", font_weight="bold"), spacing="2"),
                        align_items="start", spacing="1", width="100%"
                    ),
                    flex="1.2", 
                ),
                width="100%", align_items="stretch" 
            ),
            rx.separator(color_scheme="gray", opacity=0.1),
            rx.text("B2C RETURN RATE", color="gray.500", font_weight="bold", font_size="10px", width="100%", letter_spacing="0.1em"),
            rx.vstack(rx.foreach(State.return_breakdown, lambda item: rx.hstack(rx.text(item["channel"], color="gray.300", font_size="xs"), rx.spacer(), rx.badge(item["formatted_rate"], color_scheme="red", variant="surface", size="1"), width="100%", padding_y="1", border_bottom=f"1px dashed {BORDER_COLOR}")), width="100%", spacing="0"),
            spacing="3", width="100%"
        ),
        bg=CARD_BG, border=f"1px solid {BORDER_COLOR}", border_left="4px solid #e53935", border_radius="xl", padding="24px", width="100%", box_shadow="lg"
    )

def card_pareto():
    return rx.box(
        rx.vstack(
                rx.center(rx.vstack(rx.text("PARETO (80% SALE)", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.1em"), rx.heading(State.pareto_stats["count_80"], color="white", size="8", font_weight="900", letter_spacing="-0.02em"), spacing="1", align_items="center", width="100%"), width="100%"),
                 rx.box(rx.vstack(rx.foreach(State.pareto_top_products, lambda item: rx.hstack(rx.badge(item["rank"], variant="solid", color_scheme="yellow", border_radius="full", size="1"), rx.text(item["name"], color="gray.200", font_size="xs", no_of_lines=1, width="40%"), rx.spacer(), rx.text(item["value_cr"], color="white", font_size="xs", font_weight="bold"), rx.spacer(), rx.text(item["pct"], color="gray.500", font_size="xs", font_weight="bold"), width="100%", padding_y="1", border_bottom=f"1px solid {BORDER_COLOR}")), width="100%", spacing="1"), width="100%", bg="rgba(255,255,255,0.02)", border_radius="md", padding="4"),
            rx.text(rx.text.span("Products driving 80% of sales ", font_weight="bold", color="gray.400"), rx.text.span(State.pareto_stats["pct_catalog"], font_weight="bold", color="white"), font_size="xs", text_align="center", width="100%"),
            spacing="3", width="100%"
        ),
        bg=CARD_BG, border=f"1px solid {BORDER_COLOR}", border_left="4px solid #8E2DE2", border_radius="xl", padding="24px", width="100%", box_shadow="lg"
    )

def courier_performance_card():
    return rx.box(
        rx.vstack(
            rx.center(rx.hstack(rx.center(rx.icon("truck", color="#3182CE", size=20), bg="rgba(49, 130, 206, 0.1)", padding="2", border_radius="md", border="1px solid #3182CE"), rx.text("Courier Performance(Only for Rajnigandha.com)", font_weight="900", color=TEXT_COLOR, font_size="md", letter_spacing="0.05em"), align="center", spacing="3"), width="100%", margin_bottom="4"),
            rx.grid(
                rx.box(rx.vstack(rx.hstack(rx.icon("indian-rupee", size=14, color="gray"), rx.text("AVG DELIVERY COST", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.1em"), spacing="2", align="center"), rx.heading(State.courier_metrics["avg_cost"], size="6", color="white", font_weight="900"), rx.text("per shipment", font_size="xs", color="gray.500"), spacing="1", align_items="center"), bg="rgba(255,255,255,0.02)", padding="4", border_radius="lg", border=f"1px solid {BORDER_COLOR}", width="100%"),
                rx.box(rx.vstack(rx.hstack(rx.icon("clock", size=14, color="gray"), rx.text("AVERAGE DELIVERY TIME", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.1em"), spacing="2", align="center"), rx.heading(State.courier_metrics["avg_time"], size="6", color="white", font_weight="900"), rx.text("pickup to delivered", font_size="xs", color="gray.500"), spacing="1", align_items="center"), bg="rgba(255,255,255,0.02)", padding="4", border_radius="lg", border=f"1px solid {BORDER_COLOR}", width="100%"),
                rx.box(rx.vstack(rx.hstack(rx.icon("circle_check", size=14, color="#48BB78"), rx.text("SUCCESSFUL DELIVERY RATE", font_size="xs", font_weight="bold", color="#48BB78", letter_spacing="0.1em"), spacing="2", align="center"), rx.heading(State.courier_metrics["success_rate"], size="6", color="white", font_weight="900"), rx.text("delivery rate", font_size="xs", color="gray.500"), spacing="1", align_items="center"), bg="rgba(72, 187, 120, 0.05)", padding="4", border_radius="lg", border="1px solid #2F855A", width="100%"),
                rx.box(rx.vstack(rx.hstack(rx.icon("rotate_cw", size=14, color="#F56565"), rx.text("RETURN RATE", font_size="xs", font_weight="bold", color="#F56565", letter_spacing="0.1em"), spacing="2", align="center"), rx.heading(State.courier_metrics["return_rate"], size="6", color="white", font_weight="900"), rx.text("of total orders", font_size="xs", color="gray.500"), spacing="1", align_items="center"), bg="rgba(245, 101, 101, 0.05)", padding="4", border_radius="lg", border="1px solid #9B2C2C", width="100%"),
                columns={"initial": "1", "sm": "1", "lg": "2"}, spacing="4", width="100%"
            ), width="100%"
        ),
        bg=CARD_BG, padding="24px", border_radius="xl", box_shadow="lg", width="100%", border=f"1px solid {BORDER_COLOR}"
    )

def channel_sales_card():
    return rx.card(
        rx.vstack(
            rx.heading("Channel Wise Sale", size="4", color=TEXT_COLOR, width="100%", text_align="center", margin_bottom="4"), 
            rx.flex(
                rx.box(rx.plotly(data=State.channel_sales_chart, height="580px", config={"displayModeBar": False}), width="55%", min_width="300px", display="flex", justify_content="center", align_items="center"),
                rx.vstack(rx.foreach(State.channel_sales_stats, lambda item: rx.hstack(rx.box(width="10px", height="10px", border_radius="50%", bg=item["color"]), rx.text(item["channel"], color="gray.300", font_size="sm", font_weight="medium"), rx.spacer(), rx.text(item["value"], color="white", font_size="sm", font_weight="bold"), rx.text(item["pct"], color="gray.500", font_size="xs", font_weight="medium"), width="100%", padding_y="1", border_bottom="1px dashed #4A5568", align="center")), width="50%", min_width="250px", padding_left="4", spacing="0"),
                width="100%", flex_wrap="wrap", align="center", justify="center"
            ),
            width="100%",
        ),
        bg=CARD_BG, border_radius="xl", box_shadow="lg", border="1px solid #4A5568", padding="6", width="100%", height="100%"
    )
