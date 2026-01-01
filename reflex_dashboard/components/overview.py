import reflex as rx
from ..state import State
from ..colors import CARD_BG, TEXT_COLOR, BORDER_COLOR
from .common import table_container
from .kpi import kpi_card, card_avg_monthly_sale, card_daily_velocity, card_returns_invoices, card_pareto
from .logistics import courier_performance_card
from .charts import channel_sales_card
from .tables import monthly_summary_table, monthly_sales_return_table, invoice_vs_return_table

def overview_tab_content() -> rx.Component:
    """The main dashboard content."""
    return rx.vstack(
        # KPI Section
        rx.vstack(
            kpi_card(
                title="TOTAL SALE",
                subtitle="(Apr'25 - Nov'25)",
                value=State.total_sales,
                trend=State.total_sales_trend,
                icon="dollar-sign",
                color_scheme="#48BB78",
                align="center",
                value_size="9", 
                title_size="8", 
                bottom_left=State.total_b2b_sales,
                bottom_right=State.total_b2c_sales,
                bottom_left_trend=State.b2b_trend,
                bottom_right_trend=State.b2c_trend,
                bottom_left_icon="briefcase", 
                bottom_right_icon="shopping-cart", 
                trend_inline=True, 
            ),
            rx.grid(
                card_avg_monthly_sale(),
                card_daily_velocity(),
                card_returns_invoices(),
                card_pareto(),
                columns={"initial": "1", "sm": "1", "lg": "2", "xl": "2"}, # 2x2 Layout
                spacing="4",
                width="100%"
            ),
            
            # Courier Performance Card
            courier_performance_card(),

            spacing="4",
            width="100%",
        ),
        
        rx.box(height="10px"),

        # Monthly Summary Table
        rx.box(
            monthly_summary_table(),
            width="100%"
        ),
        
        rx.box(height="20px"),

        # Monthly Sales Return Table
        rx.box(
            monthly_sales_return_table(),
            width="100%"
        ),

        rx.box(height="20px"),

        # Invoice vs Returns Table
        rx.box(
            invoice_vs_return_table(),
            width="100%"
        ),
        
        rx.separator(margin_y="6", color_scheme="gray"),
        
        # Charts Row 1
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.heading("Monthly Sales Trend (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                    rx.plotly(data=State.monthly_sales_chart, height="400px"),
                    width="100%",
                    align="center",
                ),
                bg="#000000",
                box_shadow="lg",
                border="1px solid #4A5568",
                border_radius="xl",
                padding="4"
            ),
            
            # Added Channel Wise Sale (Donut Chart)
            channel_sales_card(),
            
            rx.box(
                rx.vstack(
                    rx.heading("Sales by State Top -10 Distribution (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                    rx.plotly(data=State.state_sales_chart, height="580px"),
                    width="100%",
                    align="center",
                ),
                bg="#000000",
                box_shadow="lg",
                border="1px solid #4A5568",
                border_radius="xl",
                padding="4"
            ),
            columns="1",
            spacing="4",
            width="100%",
        ),
        
        # Charts Row 2
        rx.grid(
            rx.box(
                rx.vstack(
                    rx.heading("Sales by Product - Top 5 (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),

                    rx.plotly(data=State.product_sales_chart, height="580px"),
                    width="100%",
                    align="center",
                ),
                bg="#000000",
                box_shadow="lg",
                border="1px solid #4A5568",
                border_radius="xl",
                padding="4"
            ),
             rx.box(
                rx.vstack(
                    rx.heading("Sales by Supply Type (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                    rx.plotly(data=State.supply_sales_chart, height="580px"),
                    width="100%",
                    align="center",
                ),
                bg="#000000",
                box_shadow="lg",
                border="1px solid #4A5568",
                border_radius="xl",
                padding="4"
            ),
            columns="1",
            spacing="4",
            width="100%",
        ),
        
        rx.separator(margin_y="6", color_scheme="gray"),

        # --- AI & Advanced Analytics Section ---
        
        # Top Products & B2C AOV Grid
        rx.grid(
            # Top Products Table
            table_container(
                "Product Sales Distribution", "Top 10 items & others contribution", "transparent",
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Rank", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Product Name", text_align="center", color="white", font_weight="bold"), # Center align
                            rx.table.column_header_cell("Sales", text_align="center", color="white", font_weight="bold"), # shortened for space
                            rx.table.column_header_cell("Contribution (in %)", text_align="center", color="white", font_weight="bold"), # Renamed
                        ),
                        bg="rgba(255,255,255,0.05)"
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.product_data,
                            lambda row: rx.table.row(
                                rx.table.cell(
                                    rx.center(
                                        rx.text(row["rank"], font_weight="bold", color="white", font_size="xs"),
                                        bg=row["rank_bg"],
                                        width="24px",
                                        height="24px",
                                        border_radius="full",
                                        margin_x="auto" # Center alignment fix
                                    ),
                                    text_align="center"
                                ),
                                rx.table.cell(rx.text(row["label"], font_size="xs", weight="medium", color="white", text_shadow="0px 1px 2px black"), text_align="center"), # Center align
                                rx.table.cell(rx.text(row["formatted_value"], font_family="mono", color="white", font_size="xs", font_weight="bold", text_shadow="0px 1px 2px black"), text_align="center"),
                                rx.table.cell(
                                    rx.badge(row["formatted_pct"], color_scheme="blue", variant="solid"),
                                    text_align="center"
                                ),
                                bg=row["row_bg"] # Banded lines
                            )
                        )
                    )
                ),
                # footer removed
            ),
            

            columns={"initial": "1", "sm": "1", "lg": "1"}, # Changed to single column for top products
            spacing="4",
            width="100%",
        ),
        
        rx.box(height="20px"),
        
        # B2C AOV Table in new row
        rx.box(
             table_container(
                "B2C Average Order Value", "AOV by Channel (B2C Only)", "transparent",
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Channel", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Sales", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Orders", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("AOV", text_align="center", color="white", font_weight="bold"),
                        ),
                        bg="rgba(255,255,255,0.05)"
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.b2c_data,
                            lambda row: rx.table.row(
                                rx.table.cell(
                                    rx.text(
                                        row["channel"], 
                                        color=row["channel_color"], 
                                        font_weight="bold", 
                                        text_shadow="0px 1px 2px black"
                                    ), 
                                    text_align="center"
                                ),
                                rx.table.cell(rx.text(row["formatted_sales"], font_family="mono", font_size="xs", color="white"), text_align="center"),
                                rx.table.cell(rx.text(row["orders"], font_family="mono", font_size="xs", color="white"), text_align="center"),
                                rx.table.cell(rx.badge(row["formatted_aov"], color_scheme="green", variant="solid"), text_align="center"),
                            )
                        )
                    )
                )
            ),
            width="100%",
        ),
        
        rx.box(height="20px"),

        # State Wise Table
        rx.box(
            table_container(
                "State-wise Top Selling B2C Product", "Highest revenue product by state", "transparent",
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("State", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Top Product", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Sales", text_align="right", color="white", font_weight="bold"),
                            rx.table.column_header_cell("% contribution to Sales in the State", text_align="center", color="white", font_weight="bold"),
                            rx.table.column_header_cell("Total Sale in the State", text_align="center", color="white", font_weight="bold"),
                        ),
                        bg="rgba(255,255,255,0.05)"
                    ),
                    rx.table.body(
                        rx.foreach(
                            State.state_data,
                            lambda row: rx.table.row(
                                rx.table.cell(rx.text(row["state"], font_weight="bold", font_size="xs", color="white")),
                                rx.table.cell(rx.text(row["product"], font_size="xs", color="white")),
                                rx.table.cell(rx.badge(row["formatted_sales"], color_scheme="blue", variant="solid"), text_align="right"),
                                rx.table.cell(rx.badge(row["formatted_pct"], color_scheme="green", variant="outline"), text_align="center"),
                                rx.table.cell(rx.badge(row["formatted_total_sales"], color_scheme="purple", variant="soft"), text_align="center"),
                            )
                        )
                    )
                )
            ),
            width="100%",
        ),
        
        width="100%",
        spacing="4",
        padding_bottom="40px",
    )
