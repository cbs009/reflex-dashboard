import reflex as rx
import os
from google import genai
from typing import List, Dict
from .tables import TableState

from dotenv import load_dotenv

load_dotenv() # Explicitly load .env file

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

class AIState(TableState):
    # Chat State
    chat_history: List[Dict[str, str]] = []
    current_question: str = ""
    is_ai_thinking: bool = False

    def set_current_question(self, val: str):
        self.current_question = val

    async def ask_gemini(self):
        if not self.current_question:
            return

        question = self.current_question
        self.chat_history.append({"role": "user", "text": question})
        self.current_question = ""
        self.is_ai_thinking = True
        yield

        try:
            # Initialize Client
            api_key = GEMINI_API_KEY
            if not api_key:
                api_key = os.environ.get("GEMINI_API_KEY", "")
            
            if not api_key:
                response_text = "Please set your GEMINI_API_KEY in the environment or code to use this feature."
                self.chat_history.append({"role": "ai", "text": response_text})
                self.is_ai_thinking = False
                return

            client = genai.Client(api_key=api_key)
            
            context = "No data loaded yet."
            if not self.filtered_df.empty:
                # Create a summary context from valid filtered data
                df = self.filtered_df
                total_rev = df["Sales Amount"].sum()
                
                # Columns summary
                cols = ", ".join(df.columns)
                
                context = f"""
                You are a helpful data assistant. Analyze this sales data summary:
                - Total Revenue: ₹{total_rev / 10000000:.2f} Cr
                - Row Count: {len(df)}
                - Columns: {cols}
                
                User Question: {question}
                Answer concisely based on this context. 
                """
            else:
                context = f"User Question: {question}"
            
            # Generate content using the new SDK
            response = client.models.generate_content(
                model='gemini-3-pro-preview',
                contents=context
            )
            response_text = response.text

            self.chat_history.append({"role": "ai", "text": response_text})
        
        except Exception as e:
            self.chat_history.append({"role": "ai", "text": f"Error: {str(e)}"})
        
        self.is_ai_thinking = False
