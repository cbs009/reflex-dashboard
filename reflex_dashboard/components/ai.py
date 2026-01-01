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
