import reflex as rx
from ..state import State
from .bistro import bistro_component


def intro_tab_content() -> rx.Component:
    return rx.vstack(
        rx.vstack(
             rx.heading("Welcome to Enterprise Intelligence", size="9", color="white", font_weight="900", text_align="center", letter_spacing="0.05em"),
             rx.text("Where raw data meets actionable insights (and some humor!)", color="gray.400", size="5"),
             
             rx.hstack(
                rx.image(src="/ai_cartoon.jpg", height="180px", border_radius="xl", border="2px solid #333"),
                rx.image(src="/ml_comic.png", height="180px", border_radius="xl", border="2px solid #333"),
                spacing="4",
                margin_y="4",
                wrap="wrap",
                justify="center"
             ),

            rx.vstack(
                rx.text('"Without data, you\'re just another person with an opinion." — W. Edwards Deming', color="#F56565", font_weight="bold", font_size="sm", text_align="center", font_family="Lettwestich"),
                rx.text('"We trust in God. All others must bring data." — W. Edwards Deming', color="#63B3ED", font_weight="bold", font_size="sm", text_align="center", font_family="Europa grotesk sh"),
                rx.text('"Better decisions begin with better questions."', color="#F6E05E", font_weight="bold", font_size="sm", text_align="center", font_family="Letterstich plain"),
                rx.text('"Gut feelings are strong, still stronger are data."', color="#68D391", font_weight="bold", font_size="sm", text_align="center", font_family="FF ifentification fivec"),
                spacing="2",
                align="center",
                bg="rgba(0,0,0,0.4)",
                padding="4",
                border_radius="xl",
                width="100%",
                max_width="800px",
                border="1px solid rgba(255,255,255,0.2)",
                backdrop_filter="blur(10px)"
            ),

            bistro_component(),

            spacing="2",
            align="center"
        ),
        height="100vh",
        width="100%",
        spacing="2",
        padding_x="4",
        padding_y="4",
        align="center",
        justify="start",
        overflow="hidden", # Prevent scrolling
    )
