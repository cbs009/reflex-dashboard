import os
try:
    from google import genai
    print("SUCCESS: google-genai imported successfully.")
    
    # Try to instantiate client with specific version if relevant, or just generic
    # Note: Client requires api_key. We can mock it or check if it fails gracefully.
    try:
        client = genai.Client(api_key="TEST_KEY")
        print("SUCCESS: Client instantiated.")
    except Exception as e:
        print(f"Client instantiation check: {e}")

except ImportError:
    print("FAILURE: Could not import google.genai")
except Exception as e:
    print(f"FAILURE: Unexpected error: {e}")
