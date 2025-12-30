import reflex as rx
from .components.layouts import index
from .state import State

app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="amber", # Gold/Amber accent
        gray_color="slate",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap",
    ],
    style={
        "font_family": "Inter, sans-serif",
        "background_color": "#000000",
    }
)
app.add_page(index, title="Sales Dashboard")