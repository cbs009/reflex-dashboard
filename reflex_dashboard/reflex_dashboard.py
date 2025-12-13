import reflex as rx
import pandas as pd
import os
import google.generativeai as genai
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
from rxconfig import config

class State(rx.State):
    """The app state."""
    # Raw Data
    _df: pd.DataFrame = pd.DataFrame()
    
    # Filter Options
    months: list[str] = []
    states: list[str] = []
    brands: list[str] = []
    channels: list[str] = []
    supply_types: list[str] = []
    
    # Selected Filters
    selected_months: list[str] = []
    selected_states: list[str] = []
    selected_brands: list[str] = []
    selected_channels: list[str] = []
    selected_supply_types: list[str] = []
    
    # Sidebar State
    is_sidebar_open: bool = True

    # Load data

    
    def load_data(self):
        try:
            # Resolve path relative to this file
            base_path = os.path.dirname(os.path.realpath(__file__))
            file_path = os.path.join(base_path, "..", "assets", "Uoload_ecom_sale.xlsx")
            print(f"Loading data from: {file_path}")
            self._df = pd.read_excel(file_path)
            print(f"Data loaded. Rows: {len(self._df)}")
            
            # Column Mapping for Sales_Data.csv
            # Force all columns to uppercase and strip whitespace for consistent matching
            self._df.columns = self._df.columns.str.upper().str.strip()
            
            column_mapping = {
                "BILLING DATE": "Month",
                "TOTAL VALUE": "Sales Amount",
                "BRAND DESCRIPTION": "Brand",
                "SKU QTY": "Quantity",
                "CHANNEL": "Channel",
                "PRODUCT": "Product",
                "CUSTOMER STATE": "CUSTOMER STATE", # Ensure this matches code usage
                "TYPE OF SUPPLY": "TYPE OF SUPPLY",
                "DOCUMENT DESCRIPTION": "DOCUMENT DESCRIPTION",
                "BILLING DOCUMENT": "BILLING DOCUMENT",
            }
            self._df = self._df.rename(columns=column_mapping)
            # Remove duplicate columns to prevent "Grouper not 1-dimensional" errors
            self._df = self._df.loc[:, ~self._df.columns.duplicated()]

            # Clean and Convert Data
            
            # 1. Force categorical columns to string to avoid mixed types and comparison errors
            for col in ["Brand", "Channel", "CUSTOMER STATE", "TYPE OF SUPPLY", "Product"]:
                if col in self._df.columns:
                    self._df[col] = self._df[col].astype(str).fillna("").str.strip()
                    if col == "TYPE OF SUPPLY":
                        # Standardize B2B/B2C
                        self._df[col] = self._df[col].str.upper().replace({
                            "BUSINESS TO BUSINESS": "B2B",
                            "BUSINESS TO CONSUMER": "B2C",
                            "DIRECT": "B2C", # Assumption if Direct exists
                            "DEALER": "B2B", # Assumption
                        })

            # Handle Sales Amount (remove commas, convert to numeric)
            if self._df["Sales Amount"].dtype == "object":
                self._df["Sales Amount"] = self._df["Sales Amount"].astype(str).str.replace(",", "", regex=False)
            self._df["Sales Amount"] = pd.to_numeric(self._df["Sales Amount"], errors="coerce").fillna(0)
            
            # Handle Quantity
            if self._df["Quantity"].dtype == "object":
                self._df["Quantity"] = self._df["Quantity"].astype(str).str.replace(",", "", regex=False)
            self._df["Quantity"] = pd.to_numeric(self._df["Quantity"], errors="coerce").fillna(0)

            # Handle Discount Amount
            if "DISCOUNT AMOUNT" in self._df.columns:
                if self._df["DISCOUNT AMOUNT"].dtype == "object":
                    self._df["DISCOUNT AMOUNT"] = self._df["DISCOUNT AMOUNT"].astype(str).str.replace(",", "", regex=False)
                self._df["DISCOUNT AMOUNT"] = pd.to_numeric(self._df["DISCOUNT AMOUNT"], errors="coerce").fillna(0)

            # Handle Date (19-04-2025 -> datetime -> YYYY-MM)
            self._df["Month"] = pd.to_datetime(self._df["Month"], format="%d-%m-%Y", errors="coerce")
            # We need Month to be Datetime for operations, but maybe we want to normalize it to start of month
            self._df["Month_Date"] = self._df["Month"].dt.to_period("M").dt.to_timestamp()
            self._df["Month_Label"] = self._df["Month_Date"].dt.strftime('%B-%Y')
            
            # Populate Filter Options (Categorical columns are now guaranteed strings)
            self.months = sorted([m for m in self._df['Month_Label'].unique().tolist() if m is not None], key=lambda x: pd.to_datetime(x, format='%B-%Y', errors='coerce'))
            self.states = sorted(self._df['CUSTOMER STATE'].unique().tolist())
            self.brands = sorted(self._df['Brand'].unique().tolist())
            self.channels = sorted(self._df['Channel'].unique().tolist())
            if 'TYPE OF SUPPLY' in self._df.columns:
                self.supply_types = sorted(self._df['TYPE OF SUPPLY'].unique().tolist())
            
            # Default Selections (All)
            self.selected_months = self.months
            self.selected_states = self.states
            self.selected_brands = self.brands
            self.selected_channels = self.channels
            self.selected_supply_types = self.supply_types
            
        except Exception as e:
            print(f"Error loading data: {e}")

    @rx.var
    def filtered_df(self) -> pd.DataFrame:
        if self._df.empty:
            return pd.DataFrame()
        
        # Apply Filters
        df = self._df[
            (self._df['Month_Label'].isin(self.selected_months)) &
            (self._df['CUSTOMER STATE'].isin(self.selected_states)) &
            (self._df['Brand'].isin(self.selected_brands)) &
            (self._df['Channel'].isin(self.selected_channels))
        ]
        
        if self.selected_supply_types and 'TYPE OF SUPPLY' in df.columns:
             df = df[df['TYPE OF SUPPLY'].isin(self.selected_supply_types)]
             
        return df

    @rx.var
    def total_sales(self) -> str:
        if self.filtered_df.empty:
            return "₹0.00 Cr"
        val = self.filtered_df["Sales Amount"].sum() / 10000000
        return f"₹{val:,.2f} Cr"

    @rx.var
    def average_monthly_sale(self) -> str:
        if self.filtered_df.empty:
            return "₹0.00 Cr"
        total_sales = self.filtered_df["Sales Amount"].sum() / 10000000
        unique_months = self.filtered_df["Month_Label"].nunique()
        if unique_months == 0:
            return "₹0.00 Cr"
        avg = total_sales / unique_months
        return f"₹{avg:,.2f} Cr"

    @rx.var
    def total_invoices(self) -> str:
        if self.filtered_df.empty:
            return "0"
        # Count only standard Sales Invoices (exclude Returns)
        invoices = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] != "Sales Return"]
        return f"{invoices['BILLING DOCUMENT'].nunique():,}"
        
    @rx.var
    def total_sales_return(self) -> str:
        if self.filtered_df.empty:
            return "0"
        # Count unique Return Invoices
        returns = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] == "Sales Return"]
        return f"{returns['BILLING DOCUMENT'].nunique():,}"

    @rx.var
    def total_b2b_sales(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns:
            return "B2B: ₹0.00 Cr"
        val = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]["Sales Amount"].sum() / 10000000
        return f"B2B: ₹{val:,.2f} Cr"

    @rx.var
    def total_b2c_sales(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns:
            return "B2C: ₹0.00 Cr"
        val = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]["Sales Amount"].sum() / 10000000
        return f"B2C: ₹{val:,.2f} Cr"

    # Trend Indicators
    def calculate_mom(self, df) -> str:
        """Calculates Month-over-Month growth for the given dataframe."""
        if df.empty or "Month_Date" not in df.columns:
            return ""

        # Get monthly sums
        monthly_sales = df.groupby("Month_Date")["Sales Amount"].sum().sort_index()
        
        if len(monthly_sales) < 2:
            return ""
            
        # Get last two months
        current_month = monthly_sales.iloc[-1]
        previous_month = monthly_sales.iloc[-2]
        
        if previous_month == 0:
            return "↑ 100% MoM" # Avoid division by zero
            
        growth = ((current_month - previous_month) / previous_month) * 100
        direction = "↑" if growth >= 0 else "↓"
        return f"{direction} {abs(growth):.1f}% MoM"

    @rx.var
    def total_sales_trend(self) -> str:
        return self.calculate_mom(self.filtered_df)

    @rx.var
    def b2b_trend(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return ""
        df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]
        return self.calculate_mom(df)

    @rx.var
    def b2c_trend(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return ""
        df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        return self.calculate_mom(df)

    @rx.var
    def average_monthly_sale_trend(self) -> str:
        # For average monthly sale, MoM of the average itself might be noisy.
        # Often it tracks the same trend as total sales if the # of months is constant in the window.
        # Let's use total sales trend for simplicity or implement specific logic if requested.
        return self.total_sales_trend 

    @rx.var
    def total_invoices_trend(self) -> str:
        # Similar logic for invoices
        if self.filtered_df.empty or "Month_Date" not in self.filtered_df.columns:
            return ""
        
        monthly_inv = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] != "Sales Return"] \
                        .groupby("Month_Date")["BILLING DOCUMENT"].nunique().sort_index()
                        
        if len(monthly_inv) < 2:
            return ""
            
        curr = monthly_inv.iloc[-1]
        prev = monthly_inv.iloc[-2]
        
        if prev == 0: return ""
        growth = ((curr - prev) / prev) * 100
        direction = "↑" if growth >= 0 else "↓"
        return f"{direction} {abs(growth):.1f}% MoM"
        
    @rx.var
    def total_sales_return_trend(self) -> str:
         return "" # Keep simple or implement logic

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
                response_text = "Please set your GEMINI_API_KEY in the code to use this feature."
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

    # --- Analytics Computed Vars ---

    @rx.var
    def product_data(self) -> list[dict]:
        """Top 10 Products + Others"""
        if self.filtered_df.empty:
            return []
        
        df = self.filtered_df.copy()
        if "Product" not in df.columns:
            return []
            
        total_revenue = df["Sales Amount"].sum()
        prod_grp = df.groupby("Product")["Sales Amount"].sum().reset_index().sort_values("Sales Amount", ascending=False)
        
        top_10 = prod_grp.head(10).to_dict("records")
        others_val = prod_grp.iloc[10:]["Sales Amount"].sum() if len(prod_grp) > 10 else 0
        
        results = []
        for i, r in enumerate(top_10):
            val = r["Sales Amount"]
            pct = (val / total_revenue * 100) if total_revenue else 0
            
            # Styling logic
            rank_color = CHART_COLORS[i % len(CHART_COLORS)]
            is_even = i % 2 == 0
            row_bg = "rgba(255,255,255,0.03)" if is_even else "transparent"
            
            results.append({
                "rank": str(i+1),
                "label": str(r["Product"]),
                "formatted_value": f"₹{val / 10000000:.2f} Cr",
                "formatted_pct": f"{pct:.1f}%",
                "rank_bg": rank_color,
                "row_bg": row_bg,
            })
            
        if others_val > 0:
            pct_other = (others_val / total_revenue * 100) if total_revenue else 0
            results.append({
                "rank": "-",
                "label": "Other Products",
                "formatted_value": f"₹{others_val / 10000000:.2f} Cr",
                "formatted_pct": f"{pct_other:.1f}%",
                "rank_bg": "#718096", # Gray for others
                "row_bg": "transparent",
            })
            
        return results

    @rx.var
    def b2c_data(self) -> list[dict]:
        """B2C Average Order Value by Channel"""
        if self.filtered_df.empty:
            return []
            
        df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        if df.empty:
            return []
            
        stats = df.groupby("Channel").agg(
            sales=("Sales Amount", "sum"),
            orders=("BILLING DOCUMENT", "nunique")
        ).reset_index()
        
        stats["aov"] = stats.apply(lambda x: x["sales"] / x["orders"] if x["orders"] > 0 else 0, axis=1)
        stats = stats.sort_values("aov", ascending=False)
        
        results = []
        for i, r in enumerate(stats.to_dict("records")):
            results.append({
                "channel": str(r["Channel"]),
                "formatted_sales": f"₹{r['sales'] / 10000000:.2f} Cr",
                "orders": f"{r['orders']:,.0f}",
                "formatted_aov": f"₹{r['aov']:,.0f}",
                "channel_color": CHART_COLORS[i % len(CHART_COLORS)],
            })
        return results

    @rx.var
    def state_data(self) -> list[dict]:
        """Top-selling B2C Product per State"""
        if self.filtered_df.empty:
            return []
            
        df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        if df.empty:
            return []
            
        # Group by State and Product
        state_prod = df.groupby(["CUSTOMER STATE", "Product"])["Sales Amount"].sum().reset_index()
        # Find product with max sales for each state
        # idx = state_prod.groupby("CUSTOMER STATE")["Sales Amount"].idxmax()
        # top_per_state = state_prod.loc[idx].sort_values("Sales Amount", ascending=False)
        # Using sort_values + drop_duplicates is safer if idxmax is tricky
        top_per_state = state_prod.sort_values("Sales Amount", ascending=False).drop_duplicates(["CUSTOMER STATE"])
        
        # Calculate total B2C sales per state for contribution %
        state_total_sales = df.groupby("CUSTOMER STATE")["Sales Amount"].sum().to_dict()
        
        results = []
        for r in top_per_state.to_dict("records"):
            state_name = r["CUSTOMER STATE"]
            prod_sales = r["Sales Amount"]
            total_state_sales = state_total_sales.get(state_name, 0)
            pct_contribution = (prod_sales / total_state_sales * 100) if total_state_sales > 0 else 0
            
            results.append({
                "state": str(state_name),
                "product": str(r["Product"]),
                "formatted_sales": f"₹{prod_sales / 100000:.2f} L",
                "formatted_pct": f"{pct_contribution:.1f}%",
                "formatted_total_sales": f"₹{total_state_sales / 100000:.2f} L" 
            })
        return results

    @rx.var
    def total_product_revenue(self) -> str:
        if self.filtered_df.empty: 
            return "₹0.00 Cr"
        total = self.filtered_df["Sales Amount"].sum()
        return f"₹{total / 10000000:.2f} Cr"

    @rx.var
    def monthly_sales_data(self) -> list[dict]:
        if self.filtered_df.empty:
            return []
        data = self.filtered_df.groupby("Month_Date")["Sales Amount"].sum().reset_index()
        data["Month"] = data["Month_Date"].dt.strftime('%b-%Y')
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        return data.to_dict("records")

    @rx.var
    def state_sales_data(self) -> list[dict]:
        if self.filtered_df.empty:
            return []
        data = self.filtered_df.groupby("CUSTOMER STATE")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        # Top 10 logic
        if len(data) > 10:
            top_10 = data.head(10)
            others_val = data.iloc[10:]["Sales Amount"].sum()
            others = pd.DataFrame([{'CUSTOMER STATE': 'Other', 'Sales Amount': others_val}])
            data = pd.concat([top_10, others], ignore_index=True)
            
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        records = data.to_dict("records")
        # Ensure strict descending order but keep "Other" at the bottom
        records.sort(key=lambda x: (x["CUSTOMER STATE"] != "Other", x["Sales Amount"]), reverse=True)
        
        for i, r in enumerate(records):
            r["fill"] = CHART_COLORS[i % len(CHART_COLORS)]
        return records

    @rx.var
    def state_legend_items(self) -> list[dict]:
        return [
            {"value": item["CUSTOMER STATE"], "type": "square", "color": item["fill"]}
            for item in self.state_sales_data
        ]
        
    @rx.var
    def brand_sales_data(self) -> list[dict]:
        if self.filtered_df.empty:
            return []
        data = self.filtered_df.groupby("Product")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        # Top 5 logic
        if len(data) > 5:
            top_5 = data.head(5)
            others_val = data.iloc[5:]["Sales Amount"].sum()
            others = pd.DataFrame([{'Product': 'Other', 'Sales Amount': others_val}])
            data = pd.concat([top_5, others], ignore_index=True)
            
        data = data.sort_values("Sales Amount", ascending=False)
        
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        # Recharts pie chart needs 'name' and 'value' usually, but we can map
        data = data.rename(columns={"Product": "name", "Sales Amount": "value"})
        
        # Add Colors and Percentages
        total_val = data["value"].sum()
        records = data.to_dict("records")
        # Ensure strict descending order (treat 'Other' like any other value)
        records.sort(key=lambda x: x["value"], reverse=True)
        
        for i, r in enumerate(records):
            r["fill"] = CHART_COLORS[i % len(CHART_COLORS)]
            pct = (r["value"] / total_val * 100) if total_val > 0 else 0
            # Use zero-width space to force correct sorting in frontend
            r["name"] = f"{'\u200b'*i}{pct:.0f}% : {r['name']} (₹{r['value']} Cr)"
            
        return records

    @rx.var
    def supply_sales_data(self) -> list[dict]:
        if self.filtered_df.empty:
            return []
        if 'TYPE OF SUPPLY' not in self.filtered_df.columns:
            return []
        data = self.filtered_df.groupby("TYPE OF SUPPLY")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        data = data.rename(columns={"TYPE OF SUPPLY": "name", "Sales Amount": "value"})
        
        # Add Colors and Percentages
        total_val = data["value"].sum()
        records = data.to_dict("records")
        records.sort(key=lambda x: x["value"], reverse=True)
        
        for i, r in enumerate(records):
            r["fill"] = CHART_COLORS[i % len(CHART_COLORS)]
            pct = (r["value"] / total_val * 100) if total_val > 0 else 0
            # Use zero-width space to force correct sorting in frontend
            r["name"] = f"{'\u200b'*i}{pct:.0f}% : {r['name']}"
            
        return records


    # @rx.var
    # def summary_brand_data(self) -> list[dict]:
    #     if self.filtered_df.empty:
    #         return []
    #     # Group by Month, Channel, Brand
    #     # Sort by Month descending
    #     data = self.filtered_df.groupby(["Month_Label", "Month_Date", "Channel", "Brand"])["Sales Amount"].sum().reset_index()
    #     data = data.sort_values("Month_Date", ascending=False)
    #     data["Sales Amount"] = data["Sales Amount"].apply(lambda x: f"₹{x:,.2f}")
    #     return data.to_dict("records")

    # @rx.var
    # def summary_state_data(self) -> list[dict]:
    #     if self.filtered_df.empty:
    #         return []
    #     # Group by Month, Channel, State
    #     data = self.filtered_df.groupby(["Month_Label", "Month_Date", "Channel", "CUSTOMER STATE"])["Sales Amount"].sum().reset_index()
    #     data = data.sort_values("Month_Date", ascending=False)
    #     data["Sales Amount"] = data["Sales Amount"].apply(lambda x: f"₹{x:,.2f}")
    #     return data.to_dict("records")

    @rx.var
    def monthly_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
        
        data = self.filtered_df.groupby("Month_Date")["Sales Amount"].sum().reset_index()
        data["Month"] = data["Month_Date"].dt.strftime('%b-%Y')
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        
        # Create colors for each point
        marker_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(data))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data["Month"],
            y=data["Sales Amount"],
            mode='lines+markers+text',
            text=data["Sales Amount"],
            textposition='middle center',
            textfont=dict(
                size=10, 
                color='white', 
                weight='bold'
            ),
            marker=dict(
                size=35,
                color=marker_colors,
                symbol='circle',
                line=dict(width=2, color='white'),
                opacity=1
            ),
            line=dict(
                color=ACCENT_COLOR,
                width=3
            ),
            hoverinfo='x+y',
        ))

        fig.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            hovermode="x unified",
            xaxis=dict(
                showgrid=True, 
                gridwidth=1, 
                gridcolor="#4A5568",
                showline=False
            ),
            yaxis=dict(
                showgrid=True, 
                gridwidth=1, 
                gridcolor="#4A5568",
                showline=False,
                showticklabels=False # Hide y-axis labels as values are in bubbles
            )
        )
        return fig

    @rx.var
    def state_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
            
        data = self.filtered_df.groupby("CUSTOMER STATE")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        if len(data) > 10:
            top_10 = data.head(10)
            others_val = data.iloc[10:]["Sales Amount"].sum()
            others = pd.DataFrame([{'CUSTOMER STATE': 'Other states', 'Sales Amount': others_val}])
            data = pd.concat([top_10, others], ignore_index=True)
            
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        # Sort for display
        data = data.sort_values("Sales Amount", ascending=True) 
        
        fig = px.treemap(
            data,
            path=["CUSTOMER STATE"],
            values="Sales Amount",
            color="CUSTOMER STATE",
            hover_data=['Sales Amount'],
            color_discrete_sequence=CHART_COLORS,
            color_discrete_map={"Other states": "#2D3748"}, # Dark Gray for "Other states"
            template="plotly_dark",
        )
        
        fig.update_traces(
            textinfo="label+value+percent entry",
            textfont=dict(size=14, color="white"),
            marker=dict(line=dict(width=1, color='white')),
            textposition="middle center"
        )
        
        fig.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=0, r=0, t=0, b=0), # Edge to Edge
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#4A5568")
        return fig

    @rx.var
    def product_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
            
        data = self.filtered_df.groupby("Product")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        if len(data) > 5:
            top_5 = data.head(5)
            others_val = data.iloc[5:]["Sales Amount"].sum()
            others = pd.DataFrame([{'Product': 'Other', 'Sales Amount': others_val}])
            data = pd.concat([top_5, others], ignore_index=True)
            
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        
        # Calculate Total for Center Text
        total_sales_val = data["Sales Amount"].sum()
        
        fig = px.pie(
            data,
            names="Product",
            values="Sales Amount",
            template="plotly_dark",
            hole=0.5 # Increased hole size for text
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            sort=True, 
            direction='clockwise'
        )
        fig.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            annotations=[dict(text=f"Total Sales<br>{total_sales_val:.2f} Cr", x=0.5, y=0.5, font_size=16, showarrow=False, font_weight="bold", font_color="white")]
        )
        return fig

    @rx.var
    def supply_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns:
            return go.Figure()
            
        data = self.filtered_df.groupby("TYPE OF SUPPLY")["Sales Amount"].sum().reset_index()
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        
        # Calculate Total for Center Text
        total_sales_val = data["Sales Amount"].sum()
        
        fig = px.pie(
            data,
            names="TYPE OF SUPPLY",
            values="Sales Amount",
            template="plotly_dark",
            hole=0.5 # Match Product chart
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            texttemplate='%{percent}<br>(%{value:.2f} Cr)',
            sort=True
        )
        fig.update_layout(
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            annotations=[dict(text=f"Total Sales<br>{total_sales_val:.2f} Cr", x=0.5, y=0.5, font_size=16, showarrow=False, font_weight="bold", font_color="white")]
        )
        return fig

    # Helper properties for Select All/None logic
    def toggle_all_months(self, select: bool):
        self.selected_months = self.months if select else []
    
    def toggle_all_states(self, select: bool):
        self.selected_states = self.states if select else []
        
    def toggle_all_brands(self, select: bool):
        self.selected_brands = self.brands if select else []
        
    def toggle_all_channels(self, select: bool):
        self.selected_channels = self.channels if select else []
        
    def toggle_all_supply(self, select: bool):
        self.selected_supply_types = self.supply_types if select else []

    # Toggle Individual Filters
    def toggle_month(self, month: str, checked: bool):
        if checked:
            self.selected_months = self.selected_months + [month]
        else:
            self.selected_months = [m for m in self.selected_months if m != month]

    def toggle_state(self, state: str, checked: bool):
        if checked:
            self.selected_states = self.selected_states + [state]
        else:
            self.selected_states = [s for s in self.selected_states if s != state]

    def toggle_brand(self, brand: str, checked: bool):
        if checked:
            self.selected_brands = self.selected_brands + [brand]
        else:
            self.selected_brands = [b for b in self.selected_brands if b != brand]

    def toggle_channel(self, channel: str, checked: bool):
        if checked:
            self.selected_channels = self.selected_channels + [channel]
        else:
            self.selected_channels = [c for c in self.selected_channels if c != channel]
            
    def toggle_supply(self, supply: str, checked: bool):
        if checked:
            self.selected_supply_types = self.selected_supply_types + [supply]
        else:
            self.selected_supply_types = [s for s in self.selected_supply_types if s != supply]

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open


# Styling Constants - Dark Mode
# Styling Constants - Pitch Black Mode
# Deep/Dark Palette for better white text contrast
CHART_COLORS = ["#3182CE", "#2F855A", "#D69E2E", "#C05621", "#805AD5", "#2C7A7B", "#B7791F", "#2B6CB0", "#276749", "#975A16"]

SIDEBAR_BG = "#000000" # Pitch Black sidebar
CONTENT_BG = "#000000" # Pitch Black content
CARD_BG = "#111111" # Near Black for cards
TEXT_COLOR = "#f7fafc" # White/Light Gray
ACCENT_COLOR = "#63b3ed" # Light Blue

# --- UI Helpers ---

def table_container(title, subtitle, bg_color, content, footer=None):
    return rx.box(
        rx.flex(
            rx.box(
                rx.text(title, font_size="sm", font_weight="bold", color="white", text_align="center", width="100%"),
                rx.text(subtitle, font_size="10px", color="gray.400", text_align="center", width="100%"),
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            border_bottom="1px solid #4A5568",
            bg="rgba(255, 255, 255, 0.05)"
        ),
        content,
        footer if footer is not None else rx.fragment(),
        bg=CARD_BG,
        border_radius="xl",
        border="1px solid #4A5568",
        box_shadow="lg",
        # overflow="hidden" # Removed to allow scrolling if needed
    )

def trend_badge(trend: str, text_color: str = None, font_size: str = "0.7em"):
    """Helper to render the trend badge."""
    if trend is None:
        trend = ""
    if text_color is None:
        trend_color = rx.cond(trend.contains("-"), "#F56565", "#00C851")
    else:
        trend_color = text_color
        
    return rx.el.span(
        f"{trend}", 
        style={
            "backgroundColor": "white",
            "color": trend_color, 
            "fontSize": font_size, 
            "fontWeight": "bold", 
            "padding": "2px 6px",
            "borderRadius": "6px",
            "marginLeft": "8px",
            "position": "relative", 
            "top": "-2px", # Adjusted for alignment in various contexts
            "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
            "whiteSpace": "nowrap",
        }
    )

def kpi_card(title: str, value: str, trend: str, icon: str, color_scheme: str, bg_color: str = "rgba(255, 255, 255, 0.03)", align: str = "start", value_size: str = "6", title_size: str = "2", bottom_left: str = None, bottom_right: str = None, bottom_left_trend: str = None, bottom_right_trend: str = None, bottom_left_icon: str = None, bottom_right_icon: str = None, trend_inline: bool = False, subtitle: str = None):
    """
    A modern KPI card with:
    - Icon on the left (or top-right)
    - Value prominent
    - Title subtle
    - Subtitle option
    - Trend indicator
    - Optional bottom corners
    - Optional inline trend
    """
    # Color mapping for trends
    trend_color = rx.cond(trend.contains("-"), "#F56565", "#00C851")
    
    # If using a solid background, we might need to adjust text colors, but white usually works on colored BGs too.
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(title, size=title_size, font_weight="bold", color="gray.200"), # Lighter gray, bold for title
                    rx.cond(
                         subtitle is not None,
                         rx.text(subtitle, font_size="sm", color="white", opacity=0.9, font_weight="bold"),
                         rx.fragment()
                    ),
                    rx.heading(
                        value, 
                        rx.cond(
                            trend_inline,
                            rx.box(trend_badge(trend, font_size="0.5em"), display="inline-block", style={"verticalAlign": "middle", "marginTop": "-15px"}),
                            rx.fragment()
                        ),
                        size=value_size, 
                        font_weight="bold", 
                        color="white"
                    ),
                    align_items=align,
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    align == "start",
                    rx.box(
                         rx.spacer(),
                         rx.icon(icon, size=24, color=color_scheme, stroke_width=2),
                    ),
                    rx.fragment() 
                ),
                width="100%",
                align_items="center" if align == "center" else "start",
                justify_content="center" if align == "center" else "start",
            ),
            # If centered, maybe put icon above or hide it? Or keep it simple.
            # Let's keep the trend line only if not inline
            rx.cond(
                not trend_inline,
                rx.hstack(
                    rx.text(trend, color=trend_color, font_size="sm", font_weight="bold", text_align=align, width="100%"),
                    width="100%",
                    justify_content=align, # align start or center
                ),
                rx.fragment()
            ),
            
            # Bottom Corner Content (for Total Sales)
            rx.cond(
                bottom_left is not None,
                rx.flex(
                    rx.hstack(
                        rx.icon(bottom_left_icon, size=16, color="black") if bottom_left_icon is not None else rx.fragment(),
                        rx.text(bottom_left, font_size="xs", color="black", font_weight="bold"),
                        trend_badge(bottom_left_trend, text_color="black", font_size="0.85em") if bottom_left_trend is not None else rx.fragment(),
                        align="center",
                        spacing="1"
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.icon(bottom_right_icon, size=16, color="black") if bottom_right_icon is not None else rx.fragment(),
                        rx.text(bottom_right, font_size="xs", color="black", font_weight="bold"),
                        trend_badge(bottom_right_trend, text_color="black", font_size="0.85em") if bottom_right_trend is not None else rx.fragment(),
                        align="center",
                        spacing="1"
                    ),
                    width="100%",
                    justify="between",
                    padding_top="2",
                    padding_x="6" # Increased padding as requested
                ),
                rx.fragment()
            ),
            
            spacing="4",
            align_items=align,
            width="100%",
        ),
        padding="5",
        bg=bg_color,
        border=f"1px solid {color_scheme}" if bg_color != "rgba(255, 255, 255, 0.03)" else "1px solid rgba(255, 255, 255, 0.1)",
        border_radius="xl",
        width="100%",
        transition="transform 0.2s",
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": "lg",
        },
    )

def ai_chat_component():
    return rx.box(
        rx.vstack(
            rx.heading("Ask AI Assistant", size="4", color=ACCENT_COLOR, margin_bottom="2", width="100%", text_align="center"),
            rx.hstack(
                rx.input(
                    placeholder="Ask about your sales data...",
                    value=State.current_question,
                    on_change=State.set_current_question,
                    bg="gray.800",
                    color="white",
                    width="100%",
                    border="1px solid #4A5568",
                    text_align="center",
                ),
                rx.button(
                    "Send", 
                    on_click=State.ask_gemini,
                    color_scheme="blue",
                    is_loading=State.is_ai_thinking
                ),
                width="100%",
                padding_bottom="4"
            ),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(
                        State.chat_history,
                        lambda msg: rx.box(
                            rx.text(msg["text"], font_size="sm"),
                            bg=rx.cond(msg["role"] == "user", "blue.900", "gray.700"),
                            color=rx.cond(msg["role"] == "user", "blue.100", "white"),
                            padding="3",
                            align_self=rx.cond(msg["role"] == "user", "end", "start"),
                            max_width="80%",
                            border_radius="md",
                        )
                    ),
                    spacing="3",
                    align_items="stretch",
                    width="100%"
                ),
                height="200px",
                type="always",
                scrollbars="vertical",
                style={"paddingRight": "10px"}
            ),
            padding="4",
            bg=CARD_BG,
            border_radius="xl",
            border="1px solid #4A5568",
            box_shadow="lg"
        ),
        width="100%"
    )

def sidebar_component() -> rx.Component:
    """The modern filter sidebar."""
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.icon("filter", size=20, color=ACCENT_COLOR),
                rx.heading("Filters", size="4", color="white"),
                align="center", 
                spacing="2",
                margin_bottom="6",
                padding_left="2"
            ),
            
            rx.accordion.root(
                # Month Filter
                rx.accordion.item(
                    header=rx.hstack(
                        rx.icon("calendar", size=18, color="cyan"),
                        rx.text("MONTH", font_weight="bold", color="gray.300", font_size="sm"),
                        align="center", spacing="2"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_months, color_scheme="cyan", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.months,
                                    lambda month: rx.checkbox(
                                        month,
                                        checked=State.selected_months.contains(month),
                                        on_change=lambda checked: State.toggle_month(month, checked),
                                        color_scheme="cyan",
                                        size="1"
                                    ),
                                ),
                                direction="column",
                                spacing="2",
                            ),
                            max_height="200px",
                            type="always",
                            scrollbars="vertical",
                        ),
                        spacing="2",
                        padding_left="2"
                    ),
                    value="month",
                    style={"_hover": {"bg": "rgba(255,255,255,0.02)"}}
                ),
                
                # State Filter
                rx.accordion.item(
                    header=rx.hstack(
                        rx.icon("map-pin", size=18, color="green"),
                        rx.text("STATE", font_weight="bold", color="gray.300", font_size="sm"),
                        align="center", spacing="2"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_states, color_scheme="green", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.states,
                                    lambda state: rx.checkbox(
                                        state,
                                        checked=State.selected_states.contains(state),
                                        on_change=lambda checked: State.toggle_state(state, checked),
                                        color_scheme="green",
                                        size="1"
                                    ),
                                ),
                                direction="column",
                                spacing="2",
                            ),
                            max_height="200px",
                            type="always",
                            scrollbars="vertical",
                        ),
                        spacing="2",
                        padding_left="2"
                    ),
                    value="state",
                    style={"_hover": {"bg": "rgba(255,255,255,0.02)"}}
                ),
                
                # Brand Filter
                rx.accordion.item(
                    header=rx.hstack(
                        rx.icon("tag", size=18, color="purple"),
                        rx.text("BRAND", font_weight="bold", color="gray.300", font_size="sm"),
                        align="center", spacing="2"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_brands, color_scheme="purple", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.brands,
                                    lambda brand: rx.checkbox(
                                        brand,
                                        checked=State.selected_brands.contains(brand),
                                        on_change=lambda checked: State.toggle_brand(brand, checked),
                                        color_scheme="purple",
                                        size="1"
                                    ),
                                ),
                                direction="column",
                                spacing="2",
                            ),
                            max_height="200px",
                            type="always",
                            scrollbars="vertical",
                        ),
                        spacing="2",
                        padding_left="2"
                    ),
                    value="brand",
                    style={"_hover": {"bg": "rgba(255,255,255,0.02)"}}
                ),
                
                # Channel Filter
                rx.accordion.item(
                    header=rx.hstack(
                        rx.icon("share-2", size=18, color="orange"),
                        rx.text("CHANNEL", font_weight="bold", color="gray.300", font_size="sm"),
                        align="center", spacing="2"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_channels, color_scheme="orange", size="1"),
                        rx.scroll_area( # Added scroll area just in case
                            rx.vstack(
                                rx.foreach(
                                    State.channels,
                                    lambda channel: rx.checkbox(
                                        channel,
                                        checked=State.selected_channels.contains(channel),
                                        on_change=lambda checked: State.toggle_channel(channel, checked),
                                        color_scheme="orange",
                                        size="1"
                                    ),
                                ),
                                direction="column",
                                spacing="2",
                            ),
                            max_height="200px",
                            type="always",
                            scrollbars="vertical",
                         ),
                        spacing="2",
                        padding_left="2"
                    ),
                    value="channel",
                    style={"_hover": {"bg": "rgba(255,255,255,0.02)"}}
                ),
                
                # Supply Type Filter
                rx.accordion.item(
                    header=rx.hstack(
                        rx.icon("truck", size=18, color="red"),
                        rx.text("SUPPLY TYPE", font_weight="bold", color="gray.300", font_size="sm"),
                        align="center", spacing="2"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_supply, color_scheme="red", size="1"),
                         rx.scroll_area( # Added scroll area just in case
                            rx.vstack(
                                rx.foreach(
                                    State.supply_types,
                                    lambda supply: rx.checkbox(
                                        supply,
                                        checked=State.selected_supply_types.contains(supply),
                                        on_change=lambda checked: State.toggle_supply(supply, checked),
                                        color_scheme="red",
                                        size="1"
                                    ),
                                ),
                                direction="column",
                                spacing="2",
                            ),
                            max_height="200px",
                            type="always",
                            scrollbars="vertical",
                        ),
                        spacing="2",
                        padding_left="2"
                    ),
                    value="supply",
                    style={"_hover": {"bg": "rgba(255,255,255,0.02)"}}
                ),
                
                type="multiple",
                collapsible=True,
                width="100%",
                variant="ghost", # Cleaner look than soft
            ),
            padding="6",
            width="100%",
        ),
        width=["100%", "280px"], # Slightly wider
        min_width=["100%", "280px"],
        bg="#111111", # Darker background
        height="100vh",
        display=rx.cond(State.is_sidebar_open, "block", "none"), 
        position="sticky",
        top="0",
        border_right="1px solid #333333",
        z_index="1000"
    )

def index() -> rx.Component:
    return rx.flex(
        # Sidebar
        sidebar_component(),
        
        # Main Content
        rx.box(
            rx.container(
                rx.vstack(
                    rx.hstack(
                        rx.button(
                            "☰ Filters", 
                            on_click=State.toggle_sidebar, 
                            color_scheme="gray", 
                            variant="outline",
                            size="2"
                        ),
                        rx.heading("📊 Interactive Sales Dashboard", size="8", color=TEXT_COLOR),
                        align="center",
                        margin_bottom="6"
                    ),
                    
                    rx.box(
                        ai_chat_component(),
                        width="100%",
                        margin_bottom="8"
                    ),
                    
                    # KPI Section
                    rx.vstack(
                        kpi_card(
                            title="TOTAL SALE",
                            subtitle="(Apr'25 - Nov'25)",
                            value=State.total_sales,
                            trend=State.total_sales_trend,
                            icon="dollar-sign",
                            color_scheme="#48BB78",
                            bg_color="#48BB78", 
                            align="center",
                            value_size="9", 
                            title_size="8", 
                            bottom_left=State.total_b2b_sales,
                            bottom_right=State.total_b2c_sales,
                            bottom_left_trend=State.b2b_trend,
                            bottom_right_trend=State.b2c_trend,
                            bottom_left_icon="briefcase", # Represents B2B/Trolly
                            bottom_right_icon="shopping-cart", # Represents B2C
                            trend_inline=True, # Trend in bracket inline
                        ),
                        rx.grid(
                            kpi_card(
                                title="B2B Revenue", 
                                value=State.average_monthly_sale,
                                trend=State.average_monthly_sale_trend, 
                                icon="briefcase",
                                color_scheme="#82ca9d", 
                            ),
                            kpi_card(
                                title="B2C Revenue", 
                                value=State.total_invoices, 
                                trend=State.total_invoices_trend,
                                icon="shopping-cart",
                                color_scheme="#ffc658", 
                            ),
                             kpi_card(
                                title="Return Rate",
                                value=State.total_sales_return,
                                trend=State.total_sales_return_trend,
                                icon="refresh-cw",
                                color_scheme="#ff8042", 
                            ),
                            columns={"initial": "1", "sm": "2", "lg": "3"},
                            spacing="4",
                            width="100%",
                        ),
                        spacing="4",
                        width="100%",
                    ),
                    
                    rx.separator(margin_y="6", color_scheme="gray"),
                    
                    # Charts Row 1
                    rx.grid(
                        rx.card(
                            rx.vstack(
                                rx.heading("Monthly Sales Trend (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                                rx.plotly(data=State.monthly_sales_chart, height="350px"),
                                width="100%",
                                align="center",
                            ),
                            bg=CARD_BG,
                            box_shadow="lg",
                             border="1px solid #4A5568",
                        ),
                        rx.card(
                            rx.vstack(
                                rx.heading("Sales by State Top -10 Distribution (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                                rx.plotly(data=State.state_sales_chart, height="500px"),
                                width="100%",
                                align="center",
                            ),
                            bg=CARD_BG,
                            box_shadow="lg",
                             border="1px solid #4A5568",
                        ),
                        columns="1",
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Charts Row 2
                    rx.grid(
                        rx.card(
                            rx.vstack(
                                rx.heading("Sales by Product - Top 5 (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),

                                rx.plotly(data=State.product_sales_chart, height="500px"),
                                width="100%",
                                align="center",
                            ),
                            bg=CARD_BG,
                            box_shadow="lg",
                             border="1px solid #4A5568",
                        ),
                         rx.card(
                            rx.vstack(
                                rx.heading("Sales by Supply Type (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                                rx.plotly(data=State.supply_sales_chart, height="500px"),
                                width="100%",
                                align="center",
                            ),
                            bg=CARD_BG,
                            box_shadow="lg",
                             border="1px solid #4A5568",
                        ),
                        columns="1",
                        spacing="4",
                        width="100%",
                    ),
                    
                    rx.separator(margin_y="6", color_scheme="gray"),

                    # --- AI & Advanced Analytics Section ---
                    
                    
                    # Top Products & B2C AOV Grid
                    rx.grid(
                        # Top Products Table
                        table_container(
                            "Product Sales Distribution", "Top 10 items & others contribution", "transparent",
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Rank", text_align="center"),
                                        rx.table.column_header_cell("Product Name", text_align="center"), # Center align
                                        rx.table.column_header_cell("Sales", text_align="center"), # shortened for space
                                        rx.table.column_header_cell("Contribution (in %)", text_align="center"), # Renamed
                                    ),
                                    bg="rgba(255,255,255,0.05)"
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.product_data,
                                        lambda row: rx.table.row(
                                            rx.table.cell(
                                                rx.center(
                                                    rx.text(row["rank"], font_weight="bold", color="white", font_size="xs"),
                                                    bg=row["rank_bg"],
                                                    width="24px",
                                                    height="24px",
                                                    border_radius="full",
                                                    margin_x="auto" # Center alignment fix
                                                ),
                                                text_align="center"
                                            ),
                                            rx.table.cell(rx.text(row["label"], font_size="xs", weight="medium", text_shadow="0px 1px 2px black"), text_align="center"), # Center align
                                            rx.table.cell(rx.text(row["formatted_value"], font_family="mono", font_size="xs", font_weight="bold", text_shadow="0px 1px 2px black"), text_align="center"),
                                            rx.table.cell(
                                                rx.badge(row["formatted_pct"], color_scheme="blue", variant="solid"),
                                                text_align="center"
                                            ),
                                            bg=row["row_bg"] # Banded lines
                                        )
                                    )
                                )
                            ),
                            # footer removed
                        ),
                        

                        columns={"initial": "1", "sm": "1", "lg": "1"}, # Changed to single column for top products
                        spacing="4",
                        width="100%",
                    ),
                    
                    rx.box(height="20px"),
                    
                    # B2C AOV Table in new row
                    rx.box(
                         table_container(
                            "B2C Average Order Value", "AOV by Channel (B2C Only)", "transparent",
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("Channel", text_align="center"),
                                        rx.table.column_header_cell("Sales", text_align="center"),
                                        rx.table.column_header_cell("Orders", text_align="center"),
                                        rx.table.column_header_cell("AOV", text_align="center"),
                                    ),
                                    bg="rgba(255,255,255,0.05)"
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.b2c_data,
                                        lambda row: rx.table.row(
                                            rx.table.cell(
                                                rx.text(
                                                    row["channel"], 
                                                    color=row["channel_color"], 
                                                    font_weight="bold", 
                                                    text_shadow="0px 1px 2px black"
                                                ), 
                                                text_align="center"
                                            ),
                                            rx.table.cell(rx.text(row["formatted_sales"], font_family="mono", font_size="xs"), text_align="center"),
                                            rx.table.cell(rx.text(row["orders"], font_family="mono", font_size="xs"), text_align="center"),
                                            rx.table.cell(rx.badge(row["formatted_aov"], color_scheme="green", variant="solid"), text_align="center"),
                                        )
                                    )
                                )
                            )
                        ),
                        width="100%",
                    ),
                    
                    rx.box(height="20px"),

                    # State Wise Table
                    rx.box(
                        table_container(
                            "State-wise Top Selling B2C Product", "Highest revenue product by state", "transparent",
                            rx.table.root(
                                rx.table.header(
                                    rx.table.row(
                                        rx.table.column_header_cell("State"),
                                        rx.table.column_header_cell("Top Product"),
                                        rx.table.column_header_cell("Sales", text_align="right"),
                                        rx.table.column_header_cell("% contribution to Sales in the State", text_align="center"),
                                        rx.table.column_header_cell("Total Sale in the State", text_align="center"),
                                    ),
                                    bg="rgba(255,255,255,0.05)"
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.state_data,
                                        lambda row: rx.table.row(
                                            rx.table.cell(rx.text(row["state"], font_weight="bold", font_size="xs")),
                                            rx.table.cell(rx.text(row["product"], font_size="xs")),
                                            rx.table.cell(rx.badge(row["formatted_sales"], color_scheme="blue", variant="solid"), text_align="right"),
                                            rx.table.cell(rx.badge(row["formatted_pct"], color_scheme="green", variant="outline"), text_align="center"),
                                            rx.table.cell(rx.badge(row["formatted_total_sales"], color_scheme="purple", variant="soft"), text_align="center"),
                                        )
                                    )
                                )
                            )
                        ),
                        width="100%",
                    ),




                    # rx.separator(margin_y="6", color_scheme="gray"),
                    
                    # # Summary Tables
                    # rx.heading("Detailed Breakdown: Channel vs Brand", size="5", color=TEXT_COLOR, width="100%", text_align="center"),
                    # rx.box(
                    #     rx.table.root(
                    #         rx.table.header(
                    #             rx.table.row(
                    #                 rx.table.column_header_cell("Month"),
                    #                 rx.table.column_header_cell("Channel"),
                    #                 rx.table.column_header_cell("Brand"),
                    #                 rx.table.column_header_cell("Sales"),
                    #             ),
                    #             bg="rgba(255,255,255,0.05)",
                    #         ),
                    #         rx.table.body(
                    #             rx.foreach(
                    #                 State.summary_brand_data,
                    #                 lambda row: rx.table.row(
                    #                     rx.table.cell(row["Month_Label"]),
                    #                     rx.table.cell(row["Channel"]),
                    #                     rx.table.cell(row["Brand"]),
                    #                     rx.table.cell(row["Sales Amount"]),
                    #                 )
                    #             )
                    #         ),
                    #         variant="surface",
                    #         size="1",
                    #     ),
                    #     width="100%",
                    #     overflow="auto",
                    #     max_height="400px",
                    #     border="1px solid #4A5568",
                    #     border_radius="8px",
                    # ),
                    
                    # rx.box(height="20px"),
                    
                    # rx.heading("Summary: Channel vs State", size="5", color=TEXT_COLOR, width="100%", text_align="center"),
                    # rx.box(
                    #     rx.table.root(
                    #         rx.table.header(
                    #             rx.table.row(
                    #                 rx.table.column_header_cell("Month"),
                    #                 rx.table.column_header_cell("Channel"),
                    #                 rx.table.column_header_cell("State"),
                    #                 rx.table.column_header_cell("Sales"),
                    #             ),
                    #             bg="rgba(255,255,255,0.05)",
                    #         ),
                    #         rx.table.body(
                    #             rx.foreach(
                    #                 State.summary_state_data,
                    #                 lambda row: rx.table.row(
                    #                     rx.table.cell(row["Month_Label"]),
                    #                     rx.table.cell(row["Channel"]),
                    #                     rx.table.cell(row["CUSTOMER STATE"]),
                    #                     rx.table.cell(row["Sales Amount"]),
                    #                 )
                    #             )
                    #         ),
                    #         variant="surface",
                    #         size="1",
                    #     ),
                    #     width="100%",
                    #     overflow="auto",
                    #     max_height="400px",
                    #     border="1px solid #4A5568",
                    #     border_radius="8px",
                    # ),

                    rx.box(height="40px"), # Bottom padding
                ),
                padding="6",
                max_width="1600px", 
            ),
            bg=CONTENT_BG,
            flex="1",
            height="100vh",
            overflow="auto",
        ),
        spacing="0",
        flex_direction=["column", "row"],
        height="100vh",
        width="100vw",
        on_mount=State.load_data,
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="blue",
        gray_color="slate",
    )
)
app.add_page(index, title="Sales Dashboard")