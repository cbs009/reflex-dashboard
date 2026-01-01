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
        "@keyframes popIn": {
            "0%": {"transform": "scale(0.6)", "opacity": "0"},
            "60%": {"transform": "scale(1.08)", "opacity": "1"},
            "100%": {"transform": "scale(1.0)", "opacity": "1"},
        },
    }
)
app.add_page(index, title="Sales Dashboard")