import reflex as rx
from ..state import State
from ..colors import CARD_BG, TEXT_COLOR, BORDER_COLOR

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
                            rx.icon("indian-rupee", size=14, color="white"), # Changed to white
                            rx.text("AVG DELIVERY COST", font_size="xs", font_weight="bold", color="white", letter_spacing="0.1em"), # Changed to white
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["avg_cost"], size="6", color="white", font_weight="900"),
                        rx.text("per shipment", font_size="xs", color="white", font_weight="bold"), # Max visibility
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
                            rx.icon("clock", size=14, color="white"), 
                            rx.text("AVERAGE DELIVERY TIME", font_size="xs", font_weight="bold", color="white", letter_spacing="0.1em"), 
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["avg_time"], size="6", color="white", font_weight="900"),
                        rx.text("pickup to delivered", font_size="xs", color="white", font_weight="bold"), # Max visibility
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
                        rx.text("delivery rate", font_size="xs", color="white", font_weight="bold"), # Max visibility
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
                        rx.text("of total orders", font_size="xs", color="white", font_weight="bold"), # Max visibility
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
