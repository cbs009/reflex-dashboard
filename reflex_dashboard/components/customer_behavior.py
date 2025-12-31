import reflex as rx
from ..state.customer import CustomerBehaviorState
from ..colors import CARD_BG, BORDER_COLOR, TEXT_COLOR

def subsection_header(title: str, subtitle: str = "") -> rx.Component:
    return rx.vstack(
        rx.heading(title, size="4", color="white", font_weight="bold"),
        rx.cond(
            subtitle != "",
            rx.text(subtitle, size="2", color="gray.400"),
            rx.fragment()
        ),
        spacing="1",
        margin_bottom="4"
    )

def aov_calculator_card() -> rx.Component:
    return rx.box(
        subsection_header("Purchasing Depth", "Key Metric: Average Order Value (AOV)"),
        rx.text("AOV = Total Revenue / Total Orders", color="gray.500", font_size="xs", margin_bottom="4"),
        rx.text("Measures the spending power per transaction.", color="gray.400", font_size="sm", margin_bottom="4"),
        
        rx.vstack(
            rx.text("Try it:", color="white", font_weight="bold", font_size="sm"),
            rx.grid(
                rx.vstack(
                    rx.text("Rev ($)", color="gray.500", font_size="xs"),
                    rx.input(
                        placeholder="0.00", 
                        on_change=CustomerBehaviorState.set_aov_revenue,
                        bg="rgba(0,0,0,0.5)", 
                        border_color="gray.700",
                        color="white"
                    ),
                    spacing="1"
                ),
                rx.vstack(
                    rx.text("Orders", color="gray.500", font_size="xs"),
                    rx.input(
                        placeholder="0", 
                        on_change=CustomerBehaviorState.set_aov_orders,
                        bg="rgba(0,0,0,0.5)", 
                        border_color="gray.700",
                        color="white"
                    ),
                    spacing="1"
                ),
                columns="2",
                spacing="2",
                width="100%"
            ),
            rx.button(
                "Calculate", 
                on_click=CustomerBehaviorState.calculate_aov,
                width="100%", 
                color_scheme="blue",
                size="2"
            ),
            rx.center(
                rx.heading(
                    f"${CustomerBehaviorState.calculated_aov}", 
                    color="#48BB78", 
                    size="6",
                    font_weight="900"
                ),
                bg="rgba(72, 187, 120, 0.1)",
                padding="4",
                border_radius="md",
                width="100%",
                border="1px dashed #48BB78"
            ),
            spacing="4",
            width="100%"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        padding="6",
        border_radius="xl",
        height="100%"
    )

def basket_breadth_card() -> rx.Component:
    return rx.box(
        subsection_header("Basket Breadth", "Insight: Items per Basket (IPB)"),
        rx.vstack(
             rx.hstack(
                rx.icon("shopping-bag", size=24, color="#F6E05E"),
                rx.text("Items per Basket (IPB)", color="white", font_weight="bold", font_size="md"),
                align="center",
                spacing="3"
            ),
            rx.box(
                rx.text("High IPB: Indicates a 'one-stop shop' behavior (Complete restock).", color="gray.300", font_size="sm"),
                margin_top="2"
            ),
            rx.box(
                rx.text("Low IPB: Indicates 'specific intent' (e.g., buying just one specific SKU).", color="gray.300", font_size="sm"),
                margin_top="2"
            ),
            rx.divider(margin_y="4", border_color="gray.800"),
            rx.callout.root(
                rx.callout.icon(rx.icon("lightbulb")),
                rx.callout.text(
                    "Strategy: Bundle low-IPB items with bestsellers to increase basket size.",
                    color="white"
                ),
                color_scheme="yellow",
                variant="surface",
                size="1"
            ),
            spacing="2"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        padding="6",
        border_radius="xl",
        height="100%"
    )

def purchasing_rhythm_card() -> rx.Component:
    return rx.box(
        subsection_header("Purchasing Rhythm", "Timing: Time Between Purchases (TBP)"),
        rx.text("Crucial for FMCG. Helps define the 'nudge' window.", color="gray.400", font_size="sm", margin_bottom="4"),
        
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.box(rx.text("Purchase 1", font_size="xs", weight="bold"), bg="gray.700", padding="2", border_radius="md"),
                    rx.icon("arrow-right", color="gray.500"),
                    rx.box(
                        rx.text("7 Days (Avg)", font_size="xs", weight="bold", color="#00BFFF"), 
                        border="1px dashed #00BFFF", padding="2", border_radius="md"
                    ),
                    rx.icon("arrow-right", color="gray.500"),
                    rx.box(rx.text("Purchase 2", font_size="xs", weight="bold"), bg="gray.700", padding="2", border_radius="md"),
                    align="center",
                    spacing="2"
                ),
                 rx.text("If a user hasn't bought in 10 days, they are at risk.", color="#F56565", font_size="xs", font_style="italic")
            ),
            bg="rgba(0,0,0,0.3)",
            padding="4",
            border_radius="lg",
            width="100%"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        padding="6",
        border_radius="xl",
        height="100%"
    )

def loyalty_health_card() -> rx.Component:
    return rx.box(
        subsection_header("Loyalty Program Health", "Point Redemption Rate (PRR)"),
        rx.vstack(
            rx.text("PRR = Points Redeemed / Points Issued", color="gray.500", font_size="xs"),
            rx.text("A low PRR suggests the loyalty program isn't 'sticky' enough.", color="gray.400", font_size="sm"),
            
            rx.box(height="10px"),
            
            rx.text("Redemption Velocity", color="white", font_weight="bold", font_size="sm"),
            rx.box(
                rx.box(width="65%", height="100%", bg="#9D00FF", border_radius="full"),
                width="100%", height="8px", bg="gray.800", border_radius="full"
            ),
            rx.hstack(
                rx.text("Earn First Point", font_size="xs", color="gray.500"),
                rx.spacer(),
                rx.text("65% Speed Score", font_size="xs", color="#9D00FF", font_weight="bold"),
                rx.spacer(),
                rx.text("First Redemption", font_size="xs", color="gray.500"),
                width="100%"
            ),
             rx.text("Measures how fast a user engages with rewards after joining.", color="gray.500", font_size="xs", margin_top="2"),
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        padding="6",
        border_radius="xl",
        height="100%"
    )

def cohort_analysis_section() -> rx.Component:
    return rx.box(
        rx.heading("Cohort Analysis: The Gold Standard", size="5", color="white", margin_bottom="2"),
        rx.text("Cohort analysis groups users by their 'Acquisition Month' to track retention over time. This visualization prevents seasonal spikes from hiding long-term churn issues.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            rx.center(
                rx.plotly(data=CustomerBehaviorState.cohort_heatmap_chart, height="350px", width="100%"),
                width="100%",
                bg="#000000",
                padding="4",
                border_radius="xl",
                border=f"1px solid {BORDER_COLOR}"
            ),
            rx.vstack(
                rx.heading("Retention Heatmap", size="3", color="white"),
                rx.hstack(
                    rx.text("Low", color="gray.500", font_size="xs"),
                    rx.box(width="100px", height="8px", bg="linear-gradient(90deg, #0E1117, #48BB78)"),
                    rx.text("High", color="#48BB78", font_size="xs"),
                    align="center",
                    spacing="2"
                ),
                rx.text("Insight: Notice the drop in Month 3? This indicates a failure in the 'Early Loyalty' phase.", color="#F56565", font_weight="bold", font_size="sm", border_left="3px solid #F56565", padding_left="3"),
                 align="start",
                 justify="center",
                 padding="6",
                 bg=CARD_BG,
                 border_radius="xl",
                 border=f"1px solid {BORDER_COLOR}"
            ),
            columns={"initial": "1", "lg": "2"},
            spacing="4",
            width="100%"
        )
    )

def predictive_ai_section() -> rx.Component:
    return rx.box(
        rx.heading("Transitioning to AI: Churn Prediction", size="5", color="white", margin_bottom="2"),
        rx.text("Moving from reactive analysis to proactive engineering. A true AI Engineer builds predictive models to identify who will churn before it happens using Machine Learning pipelines.", color="gray.400", margin_bottom="6"),
        
        rx.grid(
            # Left: Explanation & Feat Eng
            rx.vstack(
                rx.text("Feature Engineering for ML", color="white", font_weight="bold", font_size="md"),
                rx.text("Raw data must be transformed into 'features' for algorithms like XGBoost.", color="gray.400", font_size="sm"),
                
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Feature", color="white"),
                            rx.table.column_header_cell("Description", color="white"),
                        )
                    ),
                    rx.table.body(
                        rx.table.row(rx.table.cell("Recency (R)", color="gray.300"), rx.table.cell("Days since last purchase.", color="gray.500")),
                        rx.table.row(rx.table.cell("Frequency (F)", color="gray.300"), rx.table.cell("Total purchases in last 180 days.", color="gray.500")),
                        rx.table.row(rx.table.cell("Monetary (M)", color="gray.300"), rx.table.cell("Total lifetime spend.", color="gray.500")),
                        rx.table.row(rx.table.cell("Point Balance", color="gray.300"), rx.table.cell("Unspent loyalty points (retention signal).", color="gray.500")),
                    ),
                    width="100%",
                ),
                bg=CARD_BG,
                padding="6",
                border_radius="xl",
                border=f"1px solid {BORDER_COLOR}",
                height="100%"
            ),
            
            # Middle: Pipeline Flow
            rx.vstack(
                rx.text("The Predictive Pipeline", color="white", font_weight="bold", font_size="md", margin_bottom="4"),
                rx.vstack(
                    rx.box(rx.text("1. Labeling", weight="bold", color="#F6E05E"), rx.text("Define 'Churn' (e.g. No purchase > 30 days)", font_size="xs", color="gray.400"), bg="rgba(246, 224, 94, 0.1)", padding="3", border_radius="md", width="100%", border="1px dashed #F6E05E"),
                    rx.icon("arrow-down", color="gray.600"),
                    rx.box(rx.text("2. Training", weight="bold", color="#4299E1"), rx.text("Use 6-month historical data to predict past behavior.", font_size="xs", color="gray.400"), bg="rgba(66, 153, 225, 0.1)", padding="3", border_radius="md", width="100%", border="1px dashed #4299E1"),
                    rx.icon("arrow-down", color="gray.600"),
                    rx.box(rx.text("3. Inference", weight="bold", color="#48BB78"), rx.text("Apply model to current data for 'Probability Scores'.", font_size="xs", color="gray.400"), bg="rgba(72, 187, 120, 0.1)", padding="3", border_radius="md", width="100%", border="1px dashed #48BB78"),
                    align="center",
                    width="100%"
                ),
                bg=CARD_BG,
                padding="6",
                border_radius="xl",
                border=f"1px solid {BORDER_COLOR}",
                height="100%"
            ),

            # Right: Feature Importance Chart
            rx.vstack(
                rx.text("Model Output: Feature Importance", color="white", font_weight="bold", font_size="md"),
                rx.text("Which factors most strongly predict if a customer will leave?", color="gray.400", font_size="sm"),
                rx.plotly(data=CustomerBehaviorState.feature_importance_chart, height="300px", width="100%"),
                rx.button("Simulate Model Run", variant="outline", color_scheme="green", size="1", width="100%"),
                bg=CARD_BG,
                padding="6",
                border_radius="xl",
                border=f"1px solid {BORDER_COLOR}",
                height="100%"
            ),
            
            columns={"initial": "1", "xl": "3"},
            spacing="4",
            width="100%"
        )
    )

def strategic_recommendations_section() -> rx.Component:
    return rx.vstack(
        rx.heading("Strategic Recommendations", size="5", color="white"),
        rx.text("Data is useless without action. Here are three high-impact strategies derived from advanced analytics.", color="gray.400", margin_bottom="4"),
        
        rx.grid(
            # Card 1
            rx.box(
                rx.hstack(rx.icon("crosshair", color="#F6E05E", size=24), rx.heading("Micro-Segmentation", size="3", color="white"), spacing="3", align="center", margin_bottom="3"),
                rx.text("Move beyond 'Champions'. Use K-Means Clustering to find hidden groups like 'High-Value Occasional Buyers'.", color="gray.400", font_size="sm", margin_bottom="3"),
                rx.box(rx.text("Action: Create specific campaigns for festival seasons targeting this cluster.", font_weight="bold", color="white", font_size="xs"), bg="rgba(246, 224, 94, 0.1)", padding="3", border_radius="md"),
                bg=CARD_BG, padding="6", border_radius="xl", border=f"1px solid {BORDER_COLOR}"
            ),
            # Card 2
            rx.box(
                rx.hstack(rx.icon("zap", color="#4299E1", size=24), rx.heading("Next Best Action (NBA)", size="3", color="white"), spacing="3", align="center", margin_bottom="3"),
                rx.text("Don't send generic coupons. Use Market Basket Analysis to predict the exact SKU a customer wants next.", color="gray.400", font_size="sm", margin_bottom="3"),
                rx.box(rx.text("Action: If they bought 'Product A', recommend 'Product B' (80% affinity).", font_weight="bold", color="white", font_size="xs"), bg="rgba(66, 153, 225, 0.1)", padding="3", border_radius="md"),
                bg=CARD_BG, padding="6", border_radius="xl", border=f"1px solid {BORDER_COLOR}"
            ),
            # Card 3
            rx.box(
                rx.hstack(rx.icon("wallet", color="#48BB78", size=24), rx.heading("Wallet Share Analysis", size="3", color="white"), spacing="3", align="center", margin_bottom="3"),
                rx.text("Estimate your share of the customer's total category budget compared to competitors.", color="gray.400", font_size="sm", margin_bottom="3"),
                rx.box(rx.text("Action: Identify high-spending users with low wallet share and target aggressively.", font_weight="bold", color="white", font_size="xs"), bg="rgba(72, 187, 120, 0.1)", padding="3", border_radius="md"),
                bg=CARD_BG, padding="6", border_radius="xl", border=f"1px solid {BORDER_COLOR}"
            ),
            columns={"initial": "1", "lg": "3"},
            spacing="4",
            width="100%"
        ),
        width="100%",
        spacing="4"
    )

def behavioral_metrics_section() -> rx.Component:
    """The main container for the new Behavioral Metrics section."""
    return rx.vstack(
        rx.divider(margin_y="8", border_color="gray.800"),
        rx.heading("Beyond the Dashboard: Behavioral Metrics", size="7", color="white", margin_bottom="6"),
        rx.text("Current reporting often focuses on 'what' happened. To understand the 'how' and 'why', we must analyze the depth and rhythm of transactions.", color="gray.400", font_size="lg", margin_bottom="8"),
        
        # Row 1: Interactive Cards
        rx.grid(
            aov_calculator_card(),
            basket_breadth_card(),
            purchasing_rhythm_card(),
            loyalty_health_card(),
            columns={"initial": "1", "md": "2", "xl": "4"},
            spacing="4",
            width="100%"
        ),
        
        rx.box(height="40px"),
        
        # Row 2: Cohort Analysis
        cohort_analysis_section(),
        
        rx.box(height="40px"),
        
        # Row 3: Predictive AI
        predictive_ai_section(),
        
        rx.box(height="40px"),
        
        # Row 4: Strategic Recs
        strategic_recommendations_section(),
        
        rx.box(height="60px"), # Bottom padding
        
        width="100%",
        spacing="6"
    )
