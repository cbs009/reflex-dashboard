import sys
import os

print(f"Python Executable: {sys.executable}")
print(f"Sys Path: {sys.path}")

try:
    import google.genai
    print("SUCCESS: google-genai imported.")
except ImportError as e:
    print(f"FAILURE: {e}")

try:
    import google.generativeai
    print("WARNING: google.generativeai is still importable (might be expected if not uninstalled or cached).")
except ImportError:
    print("INFO: google.generativeai not found (expected).")
