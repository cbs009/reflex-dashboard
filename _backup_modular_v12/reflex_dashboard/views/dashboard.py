import reflex as rx
from ..state.metrics import MetricsState as State
from ..constants import BG_COLOR, TEXT_COLOR, ACCENT_BLUE, BORDER_COLOR
from ..components.common import kpi_card, table_container, premium_metric_card
from ..components.filters import sidebar_component, date_picker_modal
from ..components.cards import (
    card_avg_monthly_sale, 
    card_daily_velocity, 
    card_returns_invoices, 
    card_pareto, 
    courier_performance_card,
    channel_sales_card
)
from ..components.tables import (
    product_sales_table,
    b2c_aov_table,
    state_wise_product_table,
    monthly_summary_table_v2,
    monthly_sales_return_table,
    invoice_vs_return_table
)
from ..components.ai_chat import ai_chat_component

def business_summary_view() -> rx.Component:
    return rx.vstack(
        # Header - Scaled down for better professional look
        rx.hstack(
            rx.vstack(
                rx.heading("GLOBAL CONTROL", font_size="5.25rem", font_weight="900", color="#020617", letter_spacing="-0.04em", line_height="1"),
                rx.text("Synthesized Enterprise analytics Suite v12.0", font_size="12.5px", font_weight="700", color="slate.400", text_transform="uppercase", letter_spacing="0.45em", margin_top="1.5"),
                spacing="0", align_items="start"
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    rx.hstack(
                        rx.box(width="5.5", height="5.5", bg="white", border_radius="6px"),
                        rx.text("Upload stream", font_size="13px", font_weight="900", text_transform="uppercase", letter_spacing="0.1em"),
                        spacing="4"
                    ),
                    bg="#020617", color="white", padding_x="6", padding_y="4", border_radius="12px", shadow="0 25px 50px -12px rgba(2, 6, 23, 0.4)"
                ),
                rx.button(
                    rx.hstack(
                        rx.box(width="5.5", height="5.5", bg="#f8fafc", border_radius="6px", border="1px solid #e2e8f0"),
                        rx.text("Intelligence PDF", font_size="13px", font_weight="900", text_transform="uppercase", letter_spacing="0.1em"),
                        spacing="4"
                    ),
                    bg="white", border="1px solid #e2e8f0", color="slate.600", padding_x="6", padding_y="4", border_radius="12px", shadow="sm"
                ),
                spacing="5", align_items="center"
            ),
            width="100%", padding_bottom="12", align_items="end"
        ),
        # KPI Cards Grid - Higher Density
        rx.grid(
            premium_metric_card("Revenue Audit", State.total_sales, "Net Realized Sales", "fa-solid fa-indian-rupee-sign", "indigo", State.total_sales_trend),
            premium_metric_card("Loyalty index", "90.3%", "Retention Velocity", "fa-solid fa-users", "emerald"),
            premium_metric_card("Basket Mean", "₹2,481", "Mean Transaction AOV", "fa-solid fa-calculator", "amber"),
            premium_metric_card("Logistics Risk", "1.01%", "Returns Volume index", "fa-solid fa-rotate-left", "rose"),
            columns={"initial": "1", "sm": "2", "lg": "4"},
            spacing="8",
            width="100%",
            margin_top="10"
        ),
        # Main chart and Strategy Lab - Synchronized Heights
        rx.grid(
            # Growth Trajectory
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.text("Descriptive Growth Trajectory (Realized)", font_size="12.5px", font_weight="900", text_transform="uppercase", letter_spacing="0.12em", color="#020617"),
                        rx.box(width="100%", height="4.5px", bg="#3b82f6", margin_top="2.5"),
                        width="fit-content", margin_bottom="14"
                    ),
                    rx.plotly(data=State.monthly_sales_chart, height="520px"),
                    align_items="start", width="100%"
                ),
                bg="white", padding="16", border_radius="2.5rem", border="1px solid #e2e8f0", shadow="rgba(0, 0, 0, 0.04) 0px 20px 30px -5px", grid_column="span 2"
            ),
            # Strategy Lab - High Density
            rx.box(
                 rx.vstack(
                    rx.text("Prescriptive Strategy Lab", font_size="12.5px", font_weight="900", text_transform="uppercase", letter_spacing="0.12em", color="white", opacity=0.8, margin_bottom="14"),
                    rx.vstack(
                        rx.hstack(
                             rx.center(rx.box(width="5.5", height="5.5", bg="white", border_radius="6px"), width="15", height="15", bg="#3b82f6", border_radius="22px", shadow="0 20px 25px -5px rgba(59, 130, 246, 0.45)"),
                             rx.vstack(rx.text("Sync Rates", font_weight="900", font_size="19px", text_transform="uppercase", letter_spacing="-0.01em"), rx.text("Recover ₹40L monthly leakage via rate normalization.", font_size="13px", opacity=0.75, font_weight="600", line_height="1.4"), spacing="1", align_items="start"),
                             spacing="7", width="100%"
                        ),
                        rx.hstack(
                             rx.center(rx.box(width="5.5", height="5.5", bg="white", border_radius="6px"), width="15", height="15", bg="#10b981", border_radius="22px", shadow="0 20px 25px -5px rgba(16, 185, 129, 0.45)"),
                             rx.vstack(rx.text("Regional Pivot", font_weight="900", font_size="19px", text_transform="uppercase", letter_spacing="-0.01em"), rx.text("Mitigate 14% RTO risk via localized hubs.", font_size="13px", opacity=0.75, font_weight="600", line_height="1.4"), spacing="1", align_items="start"),
                             spacing="7", width="100%"
                        ),
                        spacing="8", align_items="start"
                    ),
                    rx.spacer(),
                    rx.vstack(
                        rx.text("System Integrity Benchmark", font_size="11px", font_weight="900", color="#3b82f6", text_transform="uppercase", letter_spacing="0.18em", margin_bottom="3"),
                        rx.text("98.1", font_size="8.5rem", font_weight="900", tracking="-0.07em", line_height="0.75"),
                        align_items="center", width="100%", padding_top="14"
                    ),
                    height="100%", width="100%", align_items="start"
                 ),
                 bg="#020617", border_radius="2.5rem", padding="16", color="white", shadow="0 25px 60px -12px rgba(0, 0, 0, 0.5)"
            ),
            columns={"initial": "1", "lg": "3"},
            spacing="9",
            width="100%",
            margin_top="16"
        ),
        # Table Section - Contained Width
        rx.box(
            table_container(
                "Monthly Channel Performance Summary",
                monthly_summary_table_v2()
            ),
            margin_top="18",
            width="100%",
            max_width="1400px", # Prevent excessive stretching
            margin_x="auto"
        ),
        # Bottom High-Density Metrics (More compact cards)
        rx.grid(
            # Pareto Metric
            rx.box(
                rx.vstack(
                    rx.text("Pareto Metric", font_size="10px", font_weight="900", text_transform="uppercase", letter_spacing="0.18em", opacity=0.7),
                    rx.spacer(),
                    rx.text("A+", font_size="8.5xl", font_weight="900", color="#10b981", tracking="-0.09em", line_height="1"),
                    rx.spacer(),
                    rx.text("20% SKUs drive 80% Revenue.", font_size="11px", font_weight="900", text_transform="uppercase", letter_spacing="0.12em", opacity=0.9),
                    align_items="start", height="100%"
                ),
                bg="#020617", color="white", border_radius="2.5rem", padding="14", height="300px", shadow="2xl"
            ),
            # Clustering
            rx.box(
                rx.vstack(
                    rx.text("Clustering (K-Means)", font_size="10px", font_weight="900", text_transform="uppercase", letter_spacing="0.18em", color="slate.400"),
                    rx.spacer(),
                    rx.text("C4", font_size="9.5xl", font_weight="900", color="#6366f1", tracking="-0.09em", line_height="1"),
                    rx.spacer(),
                    rx.text("Detected 4 loyalty profiles.", font_size="11px", font_weight="900", text_transform="uppercase", letter_spacing="0.12em", color="slate.500"),
                    align_items="start", height="100%"
                ),
                bg="white", border="1px solid #e2e8f0", border_radius="2.5rem", padding="14", height="300px", shadow="rgba(0,0,0,0.05) 0px 10px 20px"
            ),
            # Market Sentiment
            rx.box(
                rx.vstack(
                    rx.text("Market Sentiment", font_size="10px", font_weight="900", text_transform="uppercase", letter_spacing="0.18em", color="slate.400"),
                    rx.spacer(),
                    rx.text("85%", font_size="9.5xl", font_weight="900", color="#3b82f6", tracking="-0.09em", line_height="1"),
                    rx.spacer(),
                    rx.text("Positive Affinity Delta.", font_size="11px", font_weight="900", text_transform="uppercase", letter_spacing="0.12em", color="slate.500"),
                    align_items="start", height="100%"
                ),
                bg="white", border="1px solid #e2e8f0", border_radius="2.5rem", padding="14", height="300px", shadow="rgba(0,0,0,0.05) 0px 10px 20px"
            ),
            columns={"initial": "1", "sm": "3"},
            spacing="9",
            width="100%",
            margin_top="18",
            padding_bottom="32"
        ),
        width="100%", spacing="0", class_name="fade-in", padding_x="6"
    )

def executive_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Executive Control", size="9", font_weight="black", color="slate.900", letter_spacing="tighter", text_transform="uppercase"),
                rx.text("Quarterly Strategic Performance Audit", font_size="10px", font_weight="bold", color="slate.500", text_transform="uppercase", letter_spacing="0.3em", opacity=0.7),
                spacing="2", align_items="start"
            ),
            rx.spacer(),
            width="100%", padding_bottom="10", border_bottom="1px solid #e2e8f0"
        ),
        rx.grid(
            premium_metric_card("B2B Segment", State.total_b2b_sales, "Business Institutional", "fa-solid fa-building", "indigo", State.b2b_trend),
            premium_metric_card("B2C Segment", State.total_b2c_sales, "Direct Consumer", "fa-solid fa-basket-shopping", "blue", State.b2c_trend),
            premium_metric_card("Daily Velocity", State.daily_velocity, "Avg Daily Throughput", "fa-solid fa-bolt", "amber"),
            columns={"initial": "1", "sm": "3"},
            spacing="6", width="100%", margin_top="10"
        ),
        rx.grid(
            rx.box(
                rx.text("Channel Contribution Analysis", font_size="10px", font_weight="black", text_transform="uppercase", letter_spacing="widest", margin_bottom="10", color="slate.800", text_decoration="underline", text_decoration_color="#3b82f6", text_decoration_thickness="4px", text_underline_offset="8px"),
                rx.center(rx.plotly(data=State.channel_sales_chart, height="400px")),
                bg="white", padding="12", border_radius="2.5rem", border="1px solid #e2e8f0", shadow="sm", flex="1"
            ),
            rx.box(
                rx.text("Regional Performance audit", font_size="10px", font_weight="black", text_transform="uppercase", letter_spacing="widest", margin_bottom="10", color="slate.800", text_decoration="underline", text_decoration_color="#10b981", text_decoration_thickness="4px", text_underline_offset="8px"),
                rx.plotly(data=State.state_sales_chart, height="400px"),
                bg="white", padding="12", border_radius="2.5rem", border="1px solid #e2e8f0", shadow="sm", flex="1"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="9", width="100%", margin_top="12"
        ),
        rx.box(
            monthly_sales_return_table(),
            margin_top="12",
            width="100%"
        ),
        width="100%", spacing="6", class_name="fade-in", padding_bottom="32"
    )

def ops_intelligence_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Ops Intelligence", size="9", font_weight="black", color="slate.900", letter_spacing="tighter", text_transform="uppercase"),
                rx.text("Supply Chain & Logistical Risk Matrix", font_size="10px", font_weight="bold", color="slate.500", text_transform="uppercase", letter_spacing="0.3em", opacity=0.7),
                spacing="2", align_items="start"
            ),
            rx.spacer(),
            width="100%", padding_bottom="10", border_bottom="1px solid #e2e8f0"
        ),
        rx.grid(
            premium_metric_card("Logistics Risk", "1.01%", "Returns Volume index", "fa-solid fa-rotate-left", "rose"),
            premium_metric_card("Fulfillment rate", "98.4%", "OTIF Performance", "fa-solid fa-check-double", "emerald"),
            columns={"initial": "1", "sm": "2"},
            spacing="6", width="100%", margin_top="10"
        ),
        rx.grid(
            rx.box(
                rx.text("Supply Type distribution", font_size="10px", font_weight="black", text_transform="uppercase", letter_spacing="widest", margin_bottom="10", color="slate.800", text_decoration="underline", text_decoration_color="#6366f1", text_decoration_thickness="4px", text_underline_offset="8px"),
                rx.plotly(data=State.supply_sales_chart, height="400px"),
                bg="white", padding="12", border_radius="2.5rem", border="1px solid #e2e8f0", shadow="sm"
            ),
            rx.box(
                courier_performance_card(),
                padding="0", bg="transparent"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="9", width="100%", margin_top="12"
        ),
        rx.box(
            invoice_vs_return_table(),
            margin_top="12",
            width="100%"
        ),
        width="100%", spacing="6", class_name="fade-in", padding_bottom="32"
    )

def customer_science_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Customer Science", size="9", font_weight="black", color="slate.900", letter_spacing="tighter", text_transform="uppercase"),
                rx.text("Loyalty Segmentation & Behavioral Audit", font_size="10px", font_weight="bold", color="slate.500", text_transform="uppercase", letter_spacing="0.3em", opacity=0.7),
                spacing="2", align_items="start"
            ),
            rx.spacer(),
            width="100%", padding_bottom="10", border_bottom="1px solid #e2e8f0"
        ),
        rx.grid(
            rx.box(
                rx.text("Segment Loyalty Fingerprint (Radar)", font_size="10px", font_weight="black", text_transform="uppercase", letter_spacing="widest", margin_bottom="10", color="slate.800", text_decoration="underline", text_decoration_color="#6366f1", text_decoration_thickness="4px", text_underline_offset="8px"),
                rx.plotly(data=State.loyalty_radar_chart, height="400px"),
                bg="white", padding="12", border_radius="2.5rem", border="1px solid #e2e8f0", shadow="sm"
            ),
            rx.box(
                rx.vstack(
                    rx.text("Segmentation AI Insights", font_size="10px", font_weight="black", text_transform="uppercase", letter_spacing="widest", opacity=0.4, margin_bottom="12"),
                    rx.vstack(
                        rx.hstack(
                             rx.center(rx.el.i(class_name="fa-solid fa-crown"), width="12", height="12", bg="indigo.600", border_radius="xl", color="white"),
                             rx.vstack(rx.text("VIP Retention", font_weight="black", font_size="sm"), rx.text("94% stability in Monetary index.", font_size="xs", opacity=0.6), spacing="0", align_items="start"),
                             spacing="4"
                        ),
                        rx.hstack(
                             rx.center(rx.el.i(class_name="fa-solid fa-user-clock"), width="12", height="12", bg="amber.600", border_radius="xl", color="white"),
                             rx.vstack(rx.text("Churn Alert", font_size="sm", font_weight="black"), rx.text("Defected 12 accounts in B2B tier.", font_size="xs", opacity=0.6), spacing="0", align_items="start"),
                             spacing="4"
                        ),
                        spacing="8", align_items="start"
                    ),
                    rx.spacer(),
                    rx.box(
                         rx.text("Propensity Score", font_size="10px", font_weight="black", color="blue.400", text_transform="uppercase", margin_bottom="2"),
                         rx.heading("0.89", size="8", font_weight="black"),
                         padding_top="8", border_top="1px solid rgba(255,255,255,0.1)", width="100%"
                    ),
                    height="100%", width="100%", align_items="start"
                ),
                bg="slate.900", border_radius="2.5rem", padding="10", color="white", shadow="2xl"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="9", width="100%", margin_top="12"
        ),
        rx.box(
            b2c_aov_table(),
            margin_top="12", width="100%"
        ),
        width="100%", spacing="6", class_name="fade-in", padding_bottom="32"
    )

def strategic_lab_view() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.vstack(
                rx.heading("Strategic Lab", size="9", font_weight="black", color="slate.900", letter_spacing="tighter", text_transform="uppercase"),
                rx.text("Product Portfolio & Market Expansion Matrix", font_size="10px", font_weight="bold", color="slate.500", text_transform="uppercase", letter_spacing="0.3em", opacity=0.7),
                spacing="2", align_items="start"
            ),
            rx.spacer(),
            width="100%", padding_bottom="10", border_bottom="1px solid #e2e8f0"
        ),
        rx.grid(
            rx.box(
                rx.text("Product Portfolio Growth (BCG Matrix)", font_size="10px", font_weight="black", text_transform="uppercase", letter_spacing="widest", margin_bottom="10", color="slate.800", text_decoration="underline", text_decoration_color="#10b981", text_decoration_thickness="4px", text_underline_offset="8px"),
                rx.plotly(data=State.bcg_bubble_chart, height="500px"),
                bg="white", padding="12", border_radius="2.5rem", border="1px solid #e2e8f0", shadow="sm"
            ),
            columns={"initial": "1"},
            width="100%", margin_top="12"
        ),
        rx.grid(
            product_sales_table(),
            state_wise_product_table(),
            columns={"initial": "1", "lg": "2"},
            spacing="9", width="100%", margin_top="12"
        ),
        width="100%", spacing="6", class_name="fade-in", padding_bottom="32"
    )

def dashboard_view() -> rx.Component:
    return rx.flex(
        date_picker_modal(),
        sidebar_component(),
        
        rx.box(
            rx.box(
                rx.match(
                    State.current_tab,
                    ("business-summary", business_summary_view()),
                    ("executive", executive_view()),
                    ("operations", ops_intelligence_view()),
                    ("customer", customer_science_view()),
                    ("prescriptive", strategic_lab_view()),
                    # Fallback for others
                    rx.vstack(
                        rx.heading(f"{State.current_tab.replace('-', ' ').title()}", size="9", font_weight="black", color="slate.900", text_transform="uppercase", letter_spacing="tighter"),
                        rx.text("Advanced Lab analytics in development...", color="slate.400", font_size="lg", italic=True),
                        rx.box(height="500px"),
                        width="100%",
                        align_items="start",
                        class_name="fade-in"
                    )
                ),
                padding="10",
                background_color=BG_COLOR,
                min_height="100vh",
            ),
            flex="1",
            padding="0",
            overflow_y="auto",
            class_name="custom-scrollbar"
        ),
        width="100%",
        background_color=BG_COLOR,
    )
