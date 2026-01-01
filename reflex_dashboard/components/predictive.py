import reflex as rx
from ..state.predictive import PredictiveState
from ..colors import CARD_BG, TEXT_COLOR, BORDER_COLOR

def chart_container(title: str, chart: rx.Component, height: str = "400px") -> rx.Component:
    return rx.box(
        rx.vstack(
             rx.hstack(
                rx.icon("activity", size=20, color="white"), # Generic icon, can be customized
                rx.heading(title.upper(), size="4", color=TEXT_COLOR, font_weight="900", letter_spacing="0.05em"),
                align="center",
                justify="center", # Center align the header content
                spacing="2",
                width="100%",
                padding_bottom="4"
            ),
            rx.box(
                chart,
                width="100%",
                height="100%",
            ),
            width="100%",
            height="100%",
        ),
        bg=CARD_BG,
        padding="6",
        border_radius="xl",
        box_shadow="lg",
        border=f"1px solid {BORDER_COLOR}",
        width="100%",
        height=height
    )

def predictive_tab_content() -> rx.Component:
    return rx.vstack(
        # Row 1: Revenue Growth & Regression
        rx.grid(
            chart_container(
                "Revenue Growth Trajectory",
                rx.plotly(data=PredictiveState.revenue_growth_chart, height="300px"),
                height="420px"
            ),
             chart_container(
                "Regression Analysis",
                rx.plotly(data=PredictiveState.regression_chart, height="300px"),
                height="420px"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6",
            width="100%",
        ),
        
        # Row 2: Survival & Propensity
        rx.grid(
            chart_container(
                "Survival Probability",
                rx.plotly(data=PredictiveState.survival_chart, height="300px"),
                height="420px"
            ),
            chart_container(
                "Propensity Matrix",
                rx.plotly(data=PredictiveState.propensity_chart, height="300px"),
                height="420px"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6",
            width="100%",
        ),
        
        # Section Header
        rx.center(
            rx.heading("DECISION MATRICES", size="6", color="white", font_weight="900", letter_spacing="0.05em"),
            padding_y="4",
            width="100%"
        ),
        
        # Row 3: Decision Matrices
        rx.grid(
            chart_container(
                "BCG Matrix (Share vs Growth)",
                rx.plotly(data=PredictiveState.bcg_matrix_chart, height="300px"),
                height="420px"
            ),
            chart_container(
                "Toxic SKU Diagnostic",
                rx.plotly(data=PredictiveState.toxic_sku_chart, height="300px"),
                height="420px"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6",
            width="100%",
        ),
        
        # Section Header Phase 3
        rx.center(
            rx.heading("ADVANCED FORECASTING & ALERTS", size="6", color="white", font_weight="900", letter_spacing="0.05em"),
            padding_y="4",
            width="100%"
        ),
        
        # Row 4: SKU Forecast & Seasonality
        rx.grid(
            chart_container(
                "SKU-Level Revenue Forecast",
                rx.plotly(data=PredictiveState.sku_forecast_chart, height="300px"),
                height="420px"
            ),
             chart_container(
                "Seasonality & Promo Uplift",
                rx.plotly(data=PredictiveState.seasonality_chart, height="300px"),
                height="420px"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="6",
            width="100%",
        ),
        
        # Row 5: Demand Planning Table
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.icon("shopping-cart", size=20, color="white"),
                    rx.heading("DEMAND PLANNING & REPLENISHMENT", size="4", color=TEXT_COLOR, font_weight="900", letter_spacing="0.05em"),
                    align="center",
                    justify="center",
                    spacing="2",
                    width="100%",
                    padding_bottom="4"
                ),
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("SKU ID", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Category", color="white", font_weight="bold"),
                             rx.table.column_header_cell("Current Stock", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Forecast Demand (M+1)", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Reorder Qty", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Status", text_align="center", color="white", font_weight="bold"),
                        ),
                        bg="rgba(255,255,255,0.05)"
                    ),
                    rx.table.body(
                        rx.foreach(
                            PredictiveState.demand_planning_display,
                            lambda row: rx.table.row(
                                rx.table.cell(rx.text(row["SKU_ID"], font_weight="bold", color="white")),
                                rx.table.cell(rx.text(row["Category"], color="white")), # Changed to white
                                rx.table.cell(rx.text(row["Current Stock"], font_weight="bold", color="white"), text_align="center"), # Changed to bold white text for visibility
                                rx.table.cell(rx.badge(row["Forecasted Demand (M+1)"], variant="solid", color_scheme="blue"), text_align="center"),
                                rx.table.cell(rx.text(row["Reorder Qty"], font_weight="bold", color="white"), text_align="center"),
                                rx.table.cell(
                                    rx.badge(row["Status"], color_scheme=row["status_color"], variant="solid"),
                                    text_align="center"
                                ),
                                bg="rgba(255,255,255,0.01)"
                            )
                        )
                    ),
                    width="100%"
                ),
                width="100%",
                align="center" # Centering the content (table)
            ),
            bg=CARD_BG,
            padding="6",
            border_radius="xl",
            box_shadow="lg",
            border=f"1px solid {BORDER_COLOR}",
            width="100%",
        ),
        
        # Row 6: Risk Alerts
        rx.box(
             rx.vstack(
                rx.hstack(
                    rx.icon("alert-triangle", size=20, color="#EF4444"),
                    rx.heading("OUT-OF-STOCK RISK ALERTS", size="4", color="#EF4444", font_weight="900", letter_spacing="0.05em"),
                    align="center",
                    justify="center",
                    spacing="2",
                    width="100%",
                    padding_bottom="4"
                ),
                 rx.grid(
                    rx.foreach(
                        PredictiveState.risk_alerts,
                        lambda item: rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.badge(item["Risk Level"], color_scheme="red", variant="solid"),
                                    rx.text(item["SKU_ID"], font_weight="bold", color="white"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.text(item["Alert Message"], color="white", font_weight="bold", font_size="sm"), # Changed to bold white
                                rx.text(f"Days Cover: {item['Days Cover']} days", color="white", font_weight="bold", font_size="xs"), # Changed to bold white
                                align="start",
                                spacing="2"
                            ),
                            bg="rgba(239, 68, 68, 0.1)", # Red tint
                            padding="4",
                            border_radius="lg",
                            border="1px solid #7F1D1D"
                        )
                    ),
                    columns={"initial": "1", "md": "2", "lg": "3"},
                    spacing="4",
                    width="100%"
                ),
                width="100%"
            ),
            bg=CARD_BG,
            padding="6",
            border_radius="xl",
            box_shadow="lg",
            border=f"1px solid {BORDER_COLOR}",
            width="100%",
        ),

        width="100%",
        spacing="6",
        padding_bottom="40px",
        on_mount=PredictiveState.load_predictive_data
    )
