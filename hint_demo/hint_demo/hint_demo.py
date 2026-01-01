import reflex as rx

# 🎬 Keyframe Animation — Bounce Pop
pop_in_keyframes = {
    "0%": {"transform": "scale(0.6)", "opacity": "0"},
    "60%": {"transform": "scale(1.08)", "opacity": "1"},
    "100%": {"transform": "scale(1.0)", "opacity": "1"},
}

def ai_chef_placeholder():
    return rx.box(
        rx.vstack(
            rx.text("👨‍🍳🤖", font_size="3rem"),
            rx.text(
                (
                    "“Hey! Welcome to the Data Kitchen! "
                    "Right now this area is empty — like biryani without spices! 🍚🥲 "
                    "Tap a tab above and I’ll whip up fresh recipes of sales secrets, revenue magic, "
                    "and sizzling insights! 🔥📊 "
                    "Your data is fresh… and I’m ready to cook something legendary!” ✨😎"
                ),
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
    )

def index():
    return rx.center(
        ai_chef_placeholder(),
        bg="#000000", # Pure black background to match dashboard
        height="100vh",
        width="100vw",
    )

# Add keyframes to global styles
style = {
    "@keyframes popIn": pop_in_keyframes
}

app = rx.App(style=style)
app.add_page(index)
