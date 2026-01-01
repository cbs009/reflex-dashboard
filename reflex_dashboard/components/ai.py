import reflex as rx
from ..state import State
from ..colors import ACCENT_COLOR, CARD_BG

def ai_chat_component():
    return rx.box(
        rx.vstack(
            rx.heading("Ask AI Assistant", size="4", color=ACCENT_COLOR, margin_bottom="2", width="100%", text_align="center"),
            rx.hstack(
                rx.input(
                    placeholder="Ask about your sales data...",
                    value=State.current_question,
                    on_change=State.set_current_question,
                    bg="gray.800",
                    color="rgb(160, 117, 139)", # User requested gray
                    font_weight="bold", # User requested bold
                    width="100%",
                    height="28px", 
                    border="1px solid #4A5568",
                    text_align="center",
                    font_size="sm", 
                ),
                rx.button(
                    "Send", 
                    on_click=State.ask_gemini,
                    color_scheme="blue",
                    height="28px", 
                    size="1", 
                    is_loading=State.is_ai_thinking
                ),
                width="50%", 
                margin_x="auto", 
                padding_bottom="4"
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        State.chat_history,
                        lambda msg: rx.box(
                            rx.text(msg["text"], font_size="sm"),
                            bg=rx.cond(msg["role"] == "user", "blue.900", "gray.700"),
                            color=rx.cond(msg["role"] == "user", "blue.100", "white"),
                            padding="3",
                            align_self=rx.cond(msg["role"] == "user", "end", "start"),
                            max_width="80%",
                            border_radius="md",
                        )
                    ),
                    spacing="3",
                    align_items="stretch",
                    width="100%"
                ),
                height="200px",
                type="always",
                scrollbars="vertical",
                style={"paddingRight": "10px"}
            ),
            padding="4",
            bg=CARD_BG,
            border_radius="xl",
            border="1px solid #4A5568",
            box_shadow="lg"
        ),
        width="100%"
    )

def ai_chef_placeholder():
    return rx.box(
        rx.vstack(
            rx.text("👨‍🍳🤖", font_size="3rem"),
            rx.text(
                rx.text("“Hey! Welcome to the ", as_="span"),
                rx.text("Data Kitchen! ", as_="span", font_weight="bold", color="green"), # Bold Green
                rx.text("Right now this area is empty — like biryani without spices! 🍚🥲 ", as_="span"),
                rx.text("Tap a tab", as_="span", font_weight="900", font_size="2rem", color="#FF0000", font_family="Inter", letter_spacing="1px"), # Big Bold Extreme Red
                rx.text(" above and I’ll whip up fresh recipes of ", as_="span"),
                rx.text("sales secrets, revenue magic, and sizzling insights!", as_="span", font_weight="bold", font_style="italic", color="#FF69B4", font_family="JetBrains Mono"), # Bold Italic Pink Mono
                rx.text(" 🔥📊 Your data is fresh… and I’m ready to cook something legendary!” ✨😎", as_="span"),
                text_align="center",
                font_size="1.2rem",
                width="85%",
                line_height="1.6",
            ),
            spacing="4",
            align_items="center",
        ),
        # 🌫 Premium Glass Look
        bg="rgba(255,255,255,0.08)",
        border_radius="1.7rem",
        padding="2.5rem",
        backdrop_filter="blur(14px)",
        box_shadow="0 8px 32px rgba(0,0,0,0.32)",
        border="1.2px solid rgba(255,255,255,0.18)",
        color="white",
        # 🎯 Bounce Pop Animation
        animation="popIn 0.7s ease-out",
        # Layout Fit
        display="flex",
        align_items="center",
        justify_content="center",
        width="100%",
        max_width="700px",  # Constrain width for aesthetics
        margin_x="auto",
        margin_y="auto",
        min_height="50vh",
    )
