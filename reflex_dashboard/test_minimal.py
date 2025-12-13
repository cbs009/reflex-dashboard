import reflex as rx
from rxconfig import config

class State(rx.State):
    pass

def index() -> rx.Component:
    return rx.center(
        rx.text("Hello World", font_size="2em"),
        rx.button("Test Button"),
        height="100vh",
    )

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="blue",
        gray_color="slate",
    )
)
app.add_page(index, title="Sales Dashboard")
