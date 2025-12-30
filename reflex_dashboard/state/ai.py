import reflex as rx
import os
import google.generativeai as genai
from typing import List, Dict
from .tables import TableState

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
            if not GEMINI_API_KEY:
                # Fallback to looking in os.environ for runtime if not loaded at top level
                # But it should be there.
                api_key = os.environ.get("GEMINI_API_KEY", "")
                if not api_key:
                    response_text = "Please set your GEMINI_API_KEY in the environment or code to use this feature."
                else:
                    genai.configure(api_key=api_key)
            else:
                genai.configure(api_key=GEMINI_API_KEY)
                
            model = genai.GenerativeModel('gemini-2.0-flash')
            
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
            
            response = model.generate_content(context)
            response_text = response.text

            self.chat_history.append({"role": "ai", "text": response_text})
        
        except Exception as e:
            self.chat_history.append({"role": "ai", "text": f"Error: {str(e)}"})
        
        self.is_ai_thinking = False
