import reflex as rx
from ..state import State
from ..colors import CARD_BG, TEXT_COLOR, CONTENT_BG, BORDER_COLOR
from .common import table_container
from .kpi import kpi_card, card_avg_monthly_sale, card_daily_velocity, card_returns_invoices, card_pareto
from .filters import date_picker_modal, horizontal_filter_bar
from .ai import ai_chat_component
from .charts import channel_sales_card
from .tables import monthly_summary_table, monthly_sales_return_table, invoice_vs_return_table
from .customer import customer_tab_content

def courier_performance_card():
    return rx.box(
        rx.vstack(
            rx.center(
                rx.hstack(
                    rx.center(
                        rx.icon("truck", color="#3182CE", size=20),
                        bg="rgba(49, 130, 206, 0.1)", # Dark Blue tint
                        padding="2",
                        border_radius="md",
                        border="1px solid #3182CE"
                    ),
                    rx.text("Courier Performance(Only for Rajnigandha.com)", font_weight="900", color=TEXT_COLOR, font_size="md", letter_spacing="0.05em"),
                    align="center",
                    spacing="3",
                ),
                width="100%",
                margin_bottom="4"
            ),
            rx.grid(
                # Card 1: Avg Delivery Cost
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("indian-rupee", size=14, color="gray"),
                            rx.text("AVG DELIVERY COST", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["avg_cost"], size="6", color="white", font_weight="900"),
                        rx.text("per shipment", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(255,255,255,0.02)", 
                    padding="4", 
                    border_radius="lg",
                    border=f"1px solid {BORDER_COLOR}",
                    width="100%"
                ),
                # Card 2: Avg Delivery Time
                rx.box(
                     rx.vstack(
                        rx.hstack(
                            rx.icon("clock", size=14, color="gray"),
                            rx.text("AVERAGE DELIVERY TIME", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["avg_time"], size="6", color="white", font_weight="900"),
                        rx.text("pickup to delivered", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(255,255,255,0.02)", 
                    padding="4", 
                    border_radius="lg",
                    border=f"1px solid {BORDER_COLOR}",
                    width="100%"
                ),
                # Card 3: Successful Delivery Rate (Green)
                rx.box(
                     rx.vstack(
                        rx.hstack(
                            rx.icon("circle_check", size=14, color="#48BB78"),
                            rx.text("SUCCESSFUL DELIVERY RATE", font_size="xs", font_weight="bold", color="#48BB78", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["success_rate"], size="6", color="white", font_weight="900"), 
                        rx.text("delivery rate", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(72, 187, 120, 0.05)", # Dark Green tint
                    padding="4", 
                    border_radius="lg",
                    border="1px solid #2F855A",
                    width="100%"
                ),
                # Card 4: Return Rate (Red)
                 rx.box(
                     rx.vstack(
                        rx.hstack(
                            rx.icon("rotate_cw", size=14, color="#F56565"),
                            rx.text("RETURN RATE", font_size="xs", font_weight="bold", color="#F56565", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["return_rate"], size="6", color="white", font_weight="900"), 
                        rx.text("of total orders", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(245, 101, 101, 0.05)", # Dark Red tint
                    padding="4", 
                    border_radius="lg",
                    border="1px solid #9B2C2C",
                    width="100%"
                ),
                columns={"initial": "1", "sm": "1", "lg": "2"},
                spacing="4",
                width="100%"
            ),
             width="100%"
        ),
        bg=CARD_BG,
        padding="24px", 
        border_radius="xl",
        box_shadow="lg",
        width="100%",
        border=f"1px solid {BORDER_COLOR}"
    )

def no_data_view() -> rx.Component:
    """The empty state view shown when no data is loaded."""
    return rx.center(
        rx.vstack(
            rx.heading("Upload Your Data", size="8", color="#1A202C", margin_bottom="8px"),
            rx.text(
                "Follow the steps to upload Sales and Courier data.",
                color="#718096",
                font_size="16px",
                margin_bottom="32px",
            ),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("file-spreadsheet", size=24), 
                            rx.text("1. Sales Data", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="sales", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("truck", size=24), 
                            rx.text("2. Courier Data", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="courier", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("bar-chart-2", size=24), 
                            rx.text("3. Analyze", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="analyze", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    justify="center", # Center the tabs
                    spacing="8", # Substantial space between tabs
                    margin_bottom="32px",
                ),
                
                # TAB 1: SALES DATA
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("file-spreadsheet", size=32, color="#5B45FF"),
                                rx.text("Upload Sales Data Excel File", weight="bold", size="4", color="#1A202C"),
                                rx.text("Required for dashboard visualization", size="2", color="#718096"),
                                rx.cond(
                                    State.sales_data_uploaded,
                                    rx.badge("✅ File Uploaded Successfully", color_scheme="green", variant="solid", size="3"),
                                    rx.fragment()
                                ),
                                rx.upload(
                                     rx.button(
                                        "Select Sales File",
                                        size="3",
                                        variant="solid", # Solid for better visibility on white
                                        color_scheme="indigo",
                                        width="100%",
                                    ),
                                    id="sales_tab_upload",
                                    accept={
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], 
                                        "application/vnd.ms-excel": [".xls"]
                                    },
                                    max_files=1,
                                    on_drop=State.handle_sales_upload,
                                    border="1px dashed #CBD5E0",
                                    padding="32px",
                                    border_radius="lg",
                                    width="100%",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            padding="32px",
                            bg="#F7FAFC",
                            border_radius="xl",
                            width="100%",
                            border="1px solid #E2E8F0", # Add border for definition
                        ),
                    ),
                    value="sales",
                    padding="24px",
                ),
                
                # TAB 2: COURIER DATA
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("truck", size=32, color="#3182CE"),
                                rx.text("Upload Courier Data Excel File", weight="bold", size="4", color="#1A202C"),
                                rx.text("Required for courier performance metrics", size="2", color="#718096"),
                                rx.cond(
                                    State.courier_data_uploaded,
                                    rx.badge("✅ File Uploaded Successfully", color_scheme="green", variant="solid", size="3"),
                                    rx.fragment()
                                ),
                                rx.upload(
                                     rx.button(
                                        "Select Courier File",
                                        size="3",
                                        variant="solid", # Solid
                                        color_scheme="blue",
                                        width="100%",
                                    ),
                                    id="courier_tab_upload",
                                    accept={
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], 
                                        "application/vnd.ms-excel": [".xls"]
                                    },
                                    max_files=1,
                                    on_drop=State.handle_courier_upload,
                                    border="1px dashed #CBD5E0",
                                    padding="32px",
                                    border_radius="lg",
                                    width="100%",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            padding="32px",
                            bg="#F7FAFC",
                            border_radius="xl",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                    ),
                    value="courier",
                    padding="24px",
                ),

                # TAB 3: ANALYZE
                rx.tabs.content(
                     rx.vstack(
                        rx.heading("Ready to Analyze?", size="6", color="#1A202C"),
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Sales Data Status:", weight="bold", color="#1A202C"),
                                    rx.cond(
                                        State.sales_data_uploaded,
                                        rx.badge("Ready", color_scheme="green", variant="solid"),
                                        rx.badge("Missing", color_scheme="red", variant="solid"),
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("Courier Data Status:", weight="bold", color="#1A202C"),
                                    rx.cond(
                                        State.courier_data_uploaded,
                                        rx.badge("Ready", color_scheme="green", variant="solid"),
                                        rx.badge("Optional", color_scheme="gray", variant="solid"),
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="4",
                            ),
                            padding="24px",
                            bg="#F7FAFC",
                            border_radius="lg",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                        rx.button(
                            "Launch Dashboard 🚀", 
                            on_click=State.start_analysis,
                            size="4",
                            width="100%",
                            # disabled=~State.sales_data_uploaded, # Removed disabling to ensure visibility
                            color_scheme="purple",
                            variant="solid",
                            opacity=rx.cond(State.sales_data_uploaded, "1", "0.5"), # Visual cue instead via opacity but completely visible
                            cursor=rx.cond(State.sales_data_uploaded, "pointer", "not-allowed"),
                        ),
                        spacing="6",
                        align="center",
                        width="100%",
                    ),
                    value="analyze",
                    padding="24px",
                ),
                
                defaultValue="sales",
                width="100%",
            ),

            # Error message
            rx.cond(
                State.deployment_status != "",
                rx.center( # Wrap in center
                    rx.callout.root(
                        rx.callout.text(State.deployment_status),
                        color_scheme="red",
                        role="alert",
                        margin_top="16px",
                    ),
                    width="100%", # Center needs width
                ),
            ),
            align="center",
            width="100%",
            max_width="1000px", # Increased from 600px to accommodate large tabs
        ),
        width="100%",
        height="100vh",
        background_color="white", # Explicit white background, so we force dark text everywhere above
    )

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

def placeholder_tab(title: str) -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.icon("construction", size=48, color="#555"),
            rx.heading(title, size="6", color="white"),
            rx.text("Module under development", color="gray.500"),
            spacing="4",
            align="center"
        ),
        height="50vh",
        width="100%"
    )

def index() -> rx.Component:
    return rx.box(
        rx.cond(
            # CONDITIONAL: Show No Data View if dashboard is not started
            ~State.show_dashboard,
            no_data_view(),
            # ELSE: Show New Enterprise Layout
            rx.box(
                date_picker_modal(),
                # 1. Main Header
                rx.box(
                    rx.center( # Force centering using rx.center wrapper
                        rx.vstack(
                            rx.hstack(
                                rx.icon("database", size=20, color="white"),
                                rx.heading("ENTERPRISE INTELLIGENCE SUITE", size="4", color="white", font_weight="900", letter_spacing="0.05em"),
                                align="center",
                                spacing="3"
                            ),
                            rx.badge("FULL-SPECTRUM STRATEGIC DASHBOARD V10.0", color_scheme="gray", variant="soft", size="1"),
                            align="center",
                            spacing="1",
                        ),
                        width="100%"
                    ),
                    rx.box(
                        rx.hstack(
                             rx.button("Code", variant="outline", size="1", color_scheme="gray"),
                             rx.button("Preview", variant="solid", size="1", color_scheme="blue"),
                             rx.button("Share", variant="solid", size="1", color_scheme="blue"),
                             spacing="2"
                        ),
                        position="absolute",
                        right="4",
                        top="50%",
                        transform="translateY(-50%)",
                    ),
                    width="100%",
                    padding="4",
                    bg="#000000",
                    border_bottom=f"1px solid {BORDER_COLOR}",
                    position="relative",
                ),
                
                # 2. Tabs Navigation
                rx.tabs.root(
                    rx.tabs.list(
                        rx.tabs.trigger("OVERVIEW", value="overview", color="white", font_weight="bold", padding_x="4", font_size="19px"),
                        rx.tabs.trigger("PREDICTIVE ENGINE", value="predictive", color="gray.300", font_weight="medium", padding_x="4", font_size="19px"),
                        rx.tabs.trigger("STRATEGY LAB", value="strategy", color="gray.300", font_weight="medium", padding_x="4", font_size="19px"),
                        rx.tabs.trigger("FINANCIAL AUDIT", value="finance", color="gray.300", font_weight="medium", padding_x="4", font_size="19px"),
                        rx.tabs.trigger("OPERATIONS LAB", value="operations", color="gray.300", font_weight="medium", padding_x="4", font_size="19px"),
                        rx.tabs.trigger("CUSTOMER SCIENCE", value="customer", color="gray.300", font_weight="medium", padding_x="4", font_size="19px"),
                        bg="#000000",
                        padding_y="2",
                        border_bottom=f"1px solid {BORDER_COLOR}",
                        justify="center",
                        width="100%", # Force full width for centering
                        max_width="1900px",
                        margin_x="auto"
                    ),
                    
                    # 3. Filter Bar (Sticky)
                    rx.box(
                         horizontal_filter_bar(),
                         position="sticky",
                         top="0",
                         z_index="50",
                         width="100%"
                    ),
                    
                    # 4. AI Assistant
                    rx.box(
                         ai_chat_component(),
                         padding="4",
                         bg="#111111",
                         border_bottom=f"1px solid {BORDER_COLOR}"
                    ),

                    # 5. Tab Content Areas
                    rx.box(
                        rx.tabs.content(
                            overview_tab_content(),
                            value="overview",
                            padding="6",
                        ),
                        rx.tabs.content(placeholder_tab("Predictive Engine"), value="predictive"),
                        rx.tabs.content(placeholder_tab("Strategy Lab"), value="strategy"),
                        rx.tabs.content(placeholder_tab("Financial Audit"), value="finance"),
                        rx.tabs.content(placeholder_tab("Operations Lab"), value="operations"),
                        rx.tabs.content(
                            customer_tab_content(),
                            value="customer",
                            padding="6"
                        ),
                        
                        bg=CONTENT_BG,
                        min_height="calc(100vh - 150px)", # Adjust for headers
                        width="100%",
                        max_width="1900px", # Limit width for readability
                        margin_x="auto"
                    ),
                    
                    defaultValue="overview",
                    width="100%",
                ),

                width="100%",
                bg=CONTENT_BG,
            )
        ),
        width="100%",
        min_height="100vh",
        on_mount=State.load_data,
        bg=CONTENT_BG
    )
