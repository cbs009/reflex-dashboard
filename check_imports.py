import sys
import os

try:
    print("Attempting to import reflex_dashboard...")
    from reflex_dashboard import reflex_dashboard
    print("Successfully imported reflex_dashboard!")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error during import: {e}")
    sys.exit(1)
