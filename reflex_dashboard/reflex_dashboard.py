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
    head_components=[
        rx.script(src="https://cdn.tailwindcss.com"),
    ],
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap",
        "https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=JetBrains+Mono:wght@400;700&display=swap",
        "/styles.css",
    ],
    style={
        "font_family": "Inter, sans-serif",
        "background_color": "#000000",
    }
)
app.add_page(index, title="Sales Dashboard")