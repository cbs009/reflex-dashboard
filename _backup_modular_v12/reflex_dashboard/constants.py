import os

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 

# Styling Constants - Enterprise v12 (Light/Slate Theme)
BG_COLOR = "#f8fafc"
SIDEBAR_BG = "#ffffff"
CARD_BG = "#ffffff"
TEXT_COLOR = "#0f172a"
TEXT_SECONDARY = "#64748b"

# Punchy Palette from Reference Image
ACCENT_BLUE = "#3b82f6"
ACCENT_EMERALD = "#10b981"
ACCENT_ROSE = "#e11d48"
ACCENT_AMBER = "#f59e0b"
ACCENT_INDIGO = "#6366f1"
ACCENT_NAVY = "#020617" # Deep Navy for Strategy Lab

BORDER_COLOR = "#e2e8f0"
CHART_COLORS = [ACCENT_INDIGO, ACCENT_EMERALD, ACCENT_AMBER, ACCENT_ROSE, ACCENT_BLUE]
