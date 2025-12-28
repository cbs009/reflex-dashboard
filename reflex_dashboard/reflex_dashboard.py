import reflex as rx
import sys
import os

# --- STRICT VIRTUAL ENVIRONMENT ENFORCEMENT ---
# (DISABLED FOR DEPLOYMENT Compatibility)
# if "reflex_dashboard_virtual" not in sys.prefix:
#     print("\n" + "="*80)
#     print("❌ CRITICAL ERROR: VIRTUAL ENVIRONMENT MISMATCH")
#     print("="*80)
#     print(f"This project requires the 'reflex_dashboard_virtual' environment.")
#     print(f"Current detected environment: {sys.prefix}")
#     print("\nPlease activate the correct environment before running:")
#     print("   source reflex_dashboard_virtual/bin/activate")
#     print("="*80 + "\n")
#     sys.exit(1)
# -----------------------------------------------

import pandas as pd
import os
import datetime
import calendar
import google.generativeai as genai
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go

# --- Configuration ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
from rxconfig import config

class MonthlyValue(rx.Base):
    month: str
    value: str
    is_shaded: bool = False

class StateSummary(rx.Base):
    state: str
    monthly_values: list[MonthlyValue]
    total_value: str

class ChannelSummary(rx.Base):
    channel: str
    monthly_values: list[MonthlyValue]
    total_value: str
    children: list[StateSummary]
    is_total: bool = False

class InvRetChannel(rx.Base):
    channel: str
    inv: str = "-"
    ret: str = "-"
    ret_color: str = "black"
    val: str = "" # For pct row
    color: str = ""

class InvRetRow(rx.Base):
    month: str
    channels: list[InvRetChannel]
    grand_total_inv: str = "-"
    grand_total_ret: str = "-"
    grand_total_val: str = "" # For pct row
    is_pct: bool = False
    is_total: bool = False

class State(rx.State):
    """The app state."""
    # Raw Data
    _df: pd.DataFrame = pd.DataFrame()
    _courier_df: pd.DataFrame = pd.DataFrame()
    
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
    
    # Date Range Filter
    start_date: str = ""
    end_date: str = ""

    def set_start_date(self, val: str):
        self.start_date = val
        
    def set_end_date(self, val: str):
        self.end_date = val

    # --- Custom Date Picker State ---
    show_picker: bool = False
    picker_target: str = "start" # "start" or "end"
    picker_view_date: str = "" # The month we are looking at
    picker_temp_date: str = "" # The date currently selected in the picker (before OK)

    def open_picker(self, target: str):
        self.picker_target = target
        current_val = self.start_date if target == "start" else self.end_date
        
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        if current_val:
            self.picker_view_date = current_val
            self.picker_temp_date = current_val
        else:
            self.picker_view_date = today_str
            self.picker_temp_date = today_str
            
        self.show_picker = True

    def close_picker(self):
        self.show_picker = False

    def picker_prev_month(self):
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            first = dt.replace(day=1)
            prev = first - datetime.timedelta(days=1)
            self.picker_view_date = prev.strftime("%Y-%m-%d")
        except:
             pass

    def picker_next_month(self):
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            days_in_month = calendar.monthrange(dt.year, dt.month)[1]
            next_month = dt + datetime.timedelta(days=days_in_month)
            self.picker_view_date = next_month.replace(day=1).strftime("%Y-%m-%d")
        except:
            pass
    
    def picker_select_date(self, date_str: str):
        self.picker_temp_date = date_str

    def picker_confirm(self):
        if self.picker_target == "start":
            self.set_start_date(self.picker_temp_date)
        else:
            self.set_end_date(self.picker_temp_date)
        self.show_picker = False

    @rx.var
    def picker_calendar_grid(self) -> list[dict]:
        """Returns the grid for the current view month."""
        if not self.picker_view_date: return []
        try:
            dt = datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d")
            year = dt.year
            month = dt.month
            
            c = calendar.Calendar(firstweekday=6) # Sunday start
            
            grid = []
            for date_obj in c.itermonthdates(year, month):
                is_current_month = (date_obj.month == month)
                date_str = date_obj.strftime("%Y-%m-%d")
                
                # Check strict equality for today and selected
                # We return simple types
                grid.append({
                    "day": date_obj.day,
                    "date_str": date_str,
                    "is_current_month": is_current_month,
                    "is_selected": (date_str == self.picker_temp_date),
                    # "is_today": (date_str == datetime.date.today().strftime("%Y-%m-%d")) # Optional
                })
                
            return grid
        except:
            return []
        
    @rx.var
    def picker_display_year(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%Y") 
        except:
            return ""

    @rx.var
    def picker_display_date_formatted(self) -> str:
        if not self.picker_temp_date: return "Select date"
        try:
             # Keep this for compatibility if used elsewhere, but we primarily use the split ones below
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%a, %b %d")
        except:
            return "Select date"

    @rx.var
    def picker_display_weekday(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%A")
        except:
            return ""

    @rx.var
    def picker_display_day(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%d")
        except:
            return ""

    @rx.var
    def picker_display_month(self) -> str:
        if not self.picker_temp_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_temp_date, "%Y-%m-%d").strftime("%B")
        except:
            return ""

    @rx.var
    def picker_month_year_title(self) -> str:
        if not self.picker_view_date: return ""
        try:
            return datetime.datetime.strptime(self.picker_view_date, "%Y-%m-%d").strftime("%B %Y")
        except:
            return ""
    
    # Sidebar State
    is_sidebar_open: bool = True

    def toggle_sidebar(self):
        self.is_sidebar_open = not self.is_sidebar_open
    
    # Debug / Deployment Status
    deployment_status: str = ""

    # Load data

    
    # Upload State
    is_upload_modal_open: bool = True
    sales_data_uploaded: bool = False
    courier_data_uploaded: bool = False

    # Load data
    async def handle_sales_upload(self, files: list[rx.UploadFile]):
        """Handle sales data upload."""
        if not files:
            return

        for file in files:
            try:
                upload_data = await file.read()
                
                # Save to a temporary file or read directly if pandas supports bytes (it does for read_excel with engine openpyxl usually, or BytesIO)
                # For simplicity and robustness with read_excel, let's wrap in BytesIO
                import io
                df = pd.read_excel(io.BytesIO(upload_data))
                
                self.process_sales_data(df)
                self.sales_data_uploaded = True
                
                if self.courier_data_uploaded:
                    self.deployment_status = "All Files Uploaded Successfully"
                else:
                    self.deployment_status = "Sales Data Uploaded Successfully"
                    
            except Exception as e:
                print(f"Error processing sales upload: {e}")
                self.deployment_status = f"Error: {str(e)}"

    async def handle_courier_upload(self, files: list[rx.UploadFile]):
        """Handle courier data upload."""
        if not files:
             return

        for file in files:
            try:
                upload_data = await file.read()
                import io
                df = pd.read_excel(io.BytesIO(upload_data))
                self.process_courier_data(df)
                self.courier_data_uploaded = True
                
                if self.sales_data_uploaded:
                    self.deployment_status = "All Files Uploaded Successfully"
                else:
                    self.deployment_status = "Courier Data Uploaded Successfully"

            except Exception as e:
                print(f"Error processing courier upload: {e}")
                self.deployment_status = f"Error: {str(e)}"

    def download_sample_sales(self):
        """Download sample sales data."""
        return rx.download(url="/Uoload_ecom_sale.xlsx", filename="Sales_Data_Sample.xlsx")

    def download_sample_courier(self):
        """Download sample courier data."""
        return rx.download(url="/Courier_details.xlsx", filename="Courier_Data_Sample.xlsx")

    def process_sales_data(self, df: pd.DataFrame):
        """Process loaded sales dataframe."""
        try:
            # Usage of local temp_df prevents reactive state triggers during intermediate steps
            temp_df = df.copy()
            print(f"Data processed. Rows: {len(temp_df)}")
            
            # Column Mapping for Sales_Data.csv
            # Force all columns to uppercase and strip whitespace for consistent matching
            temp_df.columns = temp_df.columns.str.upper().str.strip()
            
            column_mapping = {
                "BILLING DATE": "Billing_Date", # Renamed from Month to avoid confusion
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
            
            # VALIDATION: Check if this looks like a sales file
            # We expect at least TOTAL VALUE or Sales Amount
            if "TOTAL VALUE" not in temp_df.columns and "Sales Amount" not in temp_df.columns:
                 raise ValueError("Invalid Sales File. Missing 'TOTAL VALUE' column. Did you upload the Courier file by mistake?")

            temp_df = temp_df.rename(columns=column_mapping)
            # Remove duplicate columns to prevent "Grouper not 1-dimensional" errors
            temp_df = temp_df.loc[:, ~temp_df.columns.duplicated()]

            # Clean and Convert Data
            
            # 1. Force categorical columns to string to avoid mixed types and comparison errors
            for col in ["Brand", "Channel", "CUSTOMER STATE", "TYPE OF SUPPLY", "Product"]:
                if col in temp_df.columns:
                    temp_df[col] = temp_df[col].astype(str).fillna("").str.strip()
                    if col == "TYPE OF SUPPLY":
                        # Standardize B2B/B2C
                        temp_df[col] = temp_df[col].str.upper().replace({
                            "BUSINESS TO BUSINESS": "B2B",
                            "BUSINESS TO CONSUMER": "B2C",
                            "DIRECT": "B2C", # Assumption if Direct exists
                            "DEALER": "B2B", # Assumption
                        })
                    if col == "Channel":
                        # Standardize Channel Names
                        def map_channel(val):
                            v_upper = val.upper()
                            if "AMAZON" in v_upper: return "Amazon"
                            if "FLIPKART" in v_upper: return "Flipkart"
                            if "RCLUB" in v_upper: return "Rclub.in"
                            if "BUSINESS CLUB" in v_upper: return "Rajnigandha Business Club" 
                            if "RAJNIGANDHA" in v_upper: return "Rajnigandha.com"
                            if "B2B" in v_upper or "DEALER" in v_upper: return "B2B" 
                            return val 
                            
                        temp_df[col] = temp_df[col].apply(map_channel)

            # Handle Sales Amount
            if temp_df["Sales Amount"].dtype == "object":
                temp_df["Sales Amount"] = temp_df["Sales Amount"].astype(str).str.replace(",", "", regex=False)
            temp_df["Sales Amount"] = pd.to_numeric(temp_df["Sales Amount"], errors="coerce").fillna(0)
            
            # Handle Quantity
            if temp_df["Quantity"].dtype == "object":
                temp_df["Quantity"] = temp_df["Quantity"].astype(str).str.replace(",", "", regex=False)
            temp_df["Quantity"] = pd.to_numeric(temp_df["Quantity"], errors="coerce").fillna(0)

            # Handle Discount Amount
            if "DISCOUNT AMOUNT" in temp_df.columns:
                if temp_df["DISCOUNT AMOUNT"].dtype == "object":
                    temp_df["DISCOUNT AMOUNT"] = temp_df["DISCOUNT AMOUNT"].astype(str).str.replace(",", "", regex=False)
                temp_df["DISCOUNT AMOUNT"] = pd.to_numeric(temp_df["DISCOUNT AMOUNT"], errors="coerce").fillna(0)

            # Handle Date
            temp_df["Billing_Date"] = pd.to_datetime(temp_df["Billing_Date"], format="%d-%m-%Y", errors="coerce")
            temp_df["Month_Date"] = temp_df["Billing_Date"].dt.to_period("M").dt.to_timestamp()
            temp_df["Month_Label"] = temp_df["Month_Date"].dt.strftime('%B-%Y')
            
            # Populate Filter Options
            self.months = sorted([m for m in temp_df['Month_Label'].unique().tolist() if m is not None], key=lambda x: pd.to_datetime(x, format='%B-%Y', errors='coerce'))
            self.states = sorted(temp_df['CUSTOMER STATE'].unique().tolist())
            self.brands = sorted(temp_df['Brand'].unique().tolist())
            self.channels = sorted(temp_df['Channel'].unique().tolist())
            if 'TYPE OF SUPPLY' in temp_df.columns:
                self.supply_types = sorted(temp_df['TYPE OF SUPPLY'].unique().tolist())
            
            # Default Selections (All)
            # Default Selections (All)
            self.selected_months = self.months
            self.selected_states = self.states
            self.selected_brands = self.brands
            self.selected_channels = self.channels
            self.selected_supply_types = self.supply_types
            
            # Date Range Initialization
            if not temp_df["Billing_Date"].isnull().all():
                 min_d = temp_df["Billing_Date"].min()
                 max_d = temp_df["Billing_Date"].max()
                 self.start_date = min_d.strftime("%Y-%m-%d")
                 self.end_date = max_d.strftime("%Y-%m-%d")
            else:
                 self.start_date = ""
                 self.end_date = ""

            # ATOMIC UPDATE
            self._df = temp_df
            
        except Exception as e:
            print(f"Error processing sales data: {e}")
            self.deployment_status += f" [Data Processing Error: {str(e)}] "
            
        except Exception as e:
            print(f"Error processing sales data: {e}")
            self.deployment_status += f" [Data Processing Error: {str(e)}] "

    def process_courier_data(self, df: pd.DataFrame):
        try:
            temp_df = df.copy()
            # Normalize columns to lowercase to ensure 'gross_amount' etc match
            temp_df.columns = temp_df.columns.str.lower().str.strip()
            
            # VALIDATION: Check for expected courier columns
            # Based on courier_metrics usage: gross_amount, waybill_num, fpd, pickup_date, status
            required_cols = ["gross_amount", "waybill_num", "status"]
            missing = [col for col in required_cols if col not in temp_df.columns]
            
            if missing:
                 raise ValueError(f"Invalid Courier File. Missing columns: {missing}. Did you upload the Sales file by mistake?")
            
            # If any specific processing needed for courier, do it here on temp_df
            self._courier_df = temp_df
            print(f"DEBUG: Courier Data Processed. Shape: {self._courier_df.shape}")
        except Exception as e:
            print(f"DEBUG: Error processing courier data: {str(e)}")
            self.deployment_status = f"Error: {str(e)}"

    def close_upload_modal(self):
        self.is_upload_modal_open = False
        
    # --- New Tabbed Workflow State ---
    show_dashboard: bool = False
    
    def start_analysis(self):
        """Switch to dashboard view."""
        if not self.sales_data_uploaded:
             self.deployment_status = "Please upload Sales Data before launching."
             return
        self.show_dashboard = True

    @rx.var
    def dashboard_title(self) -> str:
        """Get dynamic dashboard title with date range."""
        base_title = "📊 Interactive Sales Dashboard"
        
        if getattr(self, "_df", None) is None or self._df.empty:
            return base_title
            
        try:
             # Ensure Billing_Date is datetime
             df = self._df.copy()
             if not pd.api.types.is_datetime64_any_dtype(df["Billing_Date"]):
                 df["Billing_Date"] = pd.to_datetime(df["Billing_Date"], errors="coerce")
             
             min_date = df["Billing_Date"].min()
             max_date = df["Billing_Date"].max()
             
             if pd.isnull(min_date) or pd.isnull(max_date):
                 return base_title
                 
             # Format: April'25 - November'25
             start_str = min_date.strftime("%B'%y")
             end_str = max_date.strftime("%B'%y")
             
             return f"{base_title} ({start_str} - {end_str})"
        except Exception:
            return base_title


    def load_data(self):
        """Legacy load_data - now just internal cleanup or optional pre-load if needed."""
        # We don't auto-load from disk anymore as per requirement.
        # But we initialize empty
        pass


    @rx.var
    def courier_metrics(self) -> dict:
        """Calculates performance metrics for Courier Service."""
        if getattr(self, "_courier_df", None) is None or self._courier_df.empty:
            return {
                "avg_cost": "₹0.0",
                "avg_time": "0.0 days",
                "success_rate": "0.0%",
                "return_rate": "0.0%"
            }
            
        df = self._courier_df.copy()
        
        # 1. Avg Delivery Cost = sum of gross_amount divided by count of waybill_num
        total_gross = df["gross_amount"].sum()
        total_waybills = df["waybill_num"].nunique() # Using nunique to be safe, or just len(df) if unique
        avg_cost = divmod(total_gross, total_waybills)[0] + (total_gross / total_waybills % 1) if total_waybills > 0 else 0
        avg_cost = total_gross / total_waybills if total_waybills > 0 else 0
        
        # 2. Avg Delivery Time = fpd - pickup_date
        # Only where fpd is present (implies delivered or attempted)
        time_df = df.dropna(subset=["fpd", "pickup_date"]).copy()
        avg_time = 0
        if not time_df.empty:
            # Ensure datetime
            time_df["pickup_date"] = pd.to_datetime(time_df["pickup_date"])
            time_df["fpd"] = pd.to_datetime(time_df["fpd"])
            
            # Calculate duration in days
            # User formula: fpd - pickup_date
            duration = (time_df["fpd"] - time_df["pickup_date"]).dt.total_seconds() / (24 * 3600)
            avg_time = duration.mean()
            
        # 3. Successful Delivery Rate = (Number of Successful Deliveries / Total Number of Deliveries) × 100%
        # Successful = status 'Delivered'
        # Total = Total rows
        total_orders = len(df)
        success_count = len(df[df["status"] == "Delivered"])
        success_rate = (success_count / total_orders * 100) if total_orders > 0 else 0
        
        # 4. Return Rate = (Number of courier Returned / Total Number of courier) x 100
        # Returned = status 'RTO'
        bfs_count = len(df[df["status"] == "RTO"]) 
        return_rate = (bfs_count / total_orders * 100) if total_orders > 0 else 0

        return {
            "avg_cost": f"₹{avg_cost:.1f}",
            "avg_time": f"{avg_time:.1f} days",
            "success_rate": f"{success_rate:.1f}%",
            "return_rate": f"{return_rate:.1f}%"
        }

    @rx.var
    def filtered_df(self) -> pd.DataFrame:
        if self._df.empty:
            return pd.DataFrame()
        
        # Apply Filters
        # Apply Filters
        # Ensure Billing_Date is datetime for comparison
        # We rely on Billing_Date being correctly set in process_sales_data
        
        mask = (
            (self._df['CUSTOMER STATE'].isin(self.selected_states)) &
            (self._df['Brand'].isin(self.selected_brands)) &
            (self._df['Channel'].isin(self.selected_channels))
        )
        
        if self.start_date and self.end_date:
             mask = mask & (self._df['Billing_Date'] >= self.start_date) & (self._df['Billing_Date'] <= self.end_date)
             
        df = self._df[mask]
        
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
        template="plotly_dark",
        height=400, # Explicit height override
        paper_bgcolor="rgba(0,0,0,0)", # Transparent to let card bg show
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT_COLOR,
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode="x unified",
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor=BORDER_COLOR,
            showline=False
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor=BORDER_COLOR,
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
            height=580, # Explicit height override
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
            height=580, # Explicit height override
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
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
            height=580, # Explicit height override
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
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

    # --- New KPI Calculations ---

    @rx.var
    def days_in_range(self) -> int:
        if self.filtered_df.empty or "Billing_Date" not in self.filtered_df.columns:
            return 1
        
        # Calculate days based on selected month range
        # We use the min and max month
        min_date = self.filtered_df["Billing_Date"].min()
        max_date = self.filtered_df["Billing_Date"].max()
        
        if pd.isna(min_date) or pd.isna(max_date):
            return 1
            
        # Add roughly one month (30 days) to the max date to cover the end of the month
        # Since Month is just the 1st of the month.
        delta = (max_date - min_date).days + 30 
        return delta if delta > 0 else 1

    @rx.var
    def daily_sales_velocity_data(self) -> Dict[str, str]:
        if self.filtered_df.empty:
             return {"total": "₹0 L", "b2b": "₹0 L", "b2c": "₹0 L"}
        
        total_sales = self.filtered_df["Sales Amount"].sum()
        
        # User defined: "total sales divided by unique number of billing date"
        # "Billing_Date" column holds the billing date as datetime
        days = self.filtered_df["Billing_Date"].nunique()
        
        daily_velocity = total_sales / days if days > 0 else 0
        
        # B2B/B2C Breakdown
        if "TYPE OF SUPPLY" in self.filtered_df.columns:
            b2b_sales = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]["Sales Amount"].sum()
            b2c_sales = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]["Sales Amount"].sum()
        else:
            b2b_sales = 0
            b2c_sales = 0
            
        b2b_daily = b2b_sales / days if days > 0 else 0
        b2c_daily = b2c_sales / days if days > 0 else 0
        
        # Format as Lacs (L)
        return {
            "total": f"₹{daily_velocity/100000:,.2f} L",
            "b2b": f"₹{b2b_daily/100000:,.2f}L",
            "b2c": f"₹{b2c_daily/100000:,.2f}L"
        }

    @rx.var
    def invoice_stats(self) -> Dict[str, str]:
        if self.filtered_df.empty:
            return {"count": "0", "daily_avg": "0"}
            
        invoices = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] != "Sales Return"]
        unique_invoices = invoices["BILLING DOCUMENT"].nunique()
        
        # User defined: "Unique BILLING DOCUMENT ... divided by Count of unique BILLING DATE"
        days = self.filtered_df["Billing_Date"].nunique()
        
        daily_avg = unique_invoices / days if days > 0 else 0
        
        return {
            "count": f"{unique_invoices:,}",
            "daily_avg": f"~{int(daily_avg)}"
        }

    @rx.var
    def return_breakdown(self) -> List[Dict[str, str]]:
        if self.filtered_df.empty:
            return []
            
        # Filter for B2C specifically as per card title "B2C RETURN RATE"
        # And also ensure "TYPE OF SUPPLY" column exists
        if "TYPE OF SUPPLY" not in self.filtered_df.columns:
             return []
             
        b2c_df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        
        if b2c_df.empty:
            return []
            
        breakdown = []
        present_channels = b2c_df["Channel"].unique()
        
        for ch in present_channels:
            ch_data = b2c_df[b2c_df["Channel"] == ch]
            ch_invoices = ch_data[ch_data["DOCUMENT DESCRIPTION"] != "Sales Return"]["BILLING DOCUMENT"].nunique()
            ch_returns = ch_data[ch_data["DOCUMENT DESCRIPTION"] == "Sales Return"]["BILLING DOCUMENT"].nunique()
            
            ch_rate = (ch_returns / ch_invoices * 100) if ch_invoices > 0 else 0.0
            
            if ch_rate > 0: # Only show significant ones
                breakdown.append({
                    "channel": str(ch),
                    "rate": str(ch_rate), # for sorting if needed, but we formatted it
                    "formatted_rate": f"{ch_rate:.2f}%"
                })
        
        # Sort by rate numerically
        breakdown.sort(key=lambda x: float(x["rate"]), reverse=True)
        return breakdown[:5]

    @rx.var
    def return_metrics(self) -> Dict[str, str]:
        if self.filtered_df.empty:
             return {"count": "0", "rate_pct": "0.00%", "val_cr": "₹0.00 Cr"}
        
        # Returns
        returns_df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] == "Sales Return"]
        unique_returns = returns_df["BILLING DOCUMENT"].nunique()
        
        # Total Invoices (for rate)
        invoices_df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] != "Sales Return"]
        total_invoices_count = invoices_df["BILLING DOCUMENT"].nunique()
        
        rate = (unique_returns / total_invoices_count * 100) if total_invoices_count > 0 else 0.0
        
        return_sum = returns_df["Sales Amount"].sum()
        return_val = return_sum / 10000000 # Crores
        
        return {
            "count": f"{unique_returns:,}",
            "rate_pct": f"{rate:.2f}%",
            "val_cr": f"₹{return_val:,.2f} Cr"
        }

    @rx.var
    def pareto_top_products(self) -> List[Dict[str, str]]:
        if self.filtered_df.empty:
            return []
            
        sales_df = self.filtered_df[self.filtered_df["Sales Amount"] > 0]
        if sales_df.empty:
             return []
             
        product_sales = sales_df.groupby("Product")["Sales Amount"].sum().sort_values(ascending=False).reset_index()
        total_sales = product_sales["Sales Amount"].sum()
        
        if total_sales <= 0:
            return []
            
        top_5 = product_sales.head(5).to_dict('records')
        formatted_top_5 = []
        for i, row in enumerate(top_5):
            contribution = (row["Sales Amount"] / total_sales * 100)
            val_cr = row["Sales Amount"] / 10000000
            formatted_top_5.append({
                "rank": str(i+1),
                "name": str(row["Product"]),
                "pct": f"{contribution:.1f}%",
                "value_cr": f"₹{val_cr:,.2f} Cr"
            })
        return formatted_top_5

    @rx.var
    def pareto_stats(self) -> Dict[str, Any]:
        if self.filtered_df.empty:
             return {"count_80": 0, "pct_catalog": "0.0%"}
             
        sales_df = self.filtered_df[self.filtered_df["Sales Amount"] > 0]
        
        product_sales = sales_df.groupby("Product")["Sales Amount"].sum().sort_values(ascending=False).reset_index()
        total_sales = product_sales["Sales Amount"].sum()
        
        if total_sales <= 0:
            return {"count_80": 0, "pct_catalog": "0.0%"}
            
        product_sales["cumulative_sales"] = product_sales["Sales Amount"].cumsum()
        product_sales["cumulative_pct"] = product_sales["cumulative_sales"] / total_sales
        
        cutoff_mask = product_sales["cumulative_pct"] <= 0.80
        count_80 = cutoff_mask.sum()
        
        if count_80 == 0 and not product_sales.empty:
             count_80 = 1
        elif count_80 < len(product_sales):
             count_80 += 1
             
        total_products = len(product_sales)
        pct_catalog = (count_80 / total_products * 100) if total_products > 0 else 0
        
        return {
            "count_80": str(count_80),
            "pct_catalog": f"({pct_catalog:.1f}% of catalog)"
        }


    @rx.var
    def avg_monthly_b2b(self) -> str:
        if self.filtered_df.empty:
            return "₹0.00 Cr"
        b2b_df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]
        total_sales = b2b_df["Sales Amount"].sum() / 10000000
        unique_months = self.filtered_df["Month_Label"].nunique()
        if unique_months == 0:
            return "₹0.00 Cr"
        avg = total_sales / unique_months
        return f"₹{avg:,.2f} Cr"

    @rx.var
    def avg_monthly_b2c(self) -> str:
        if self.filtered_df.empty:
            return "₹0.00 Cr"
        b2c_df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        total_sales = b2c_df["Sales Amount"].sum() / 10000000
        unique_months = self.filtered_df["Month_Label"].nunique()
        if unique_months == 0:
            return "₹0.00 Cr"
        avg = total_sales / unique_months
        return f"₹{avg:,.2f} Cr"

    @rx.var
    def table_date_range_title(self) -> str:
        """Dynamic title suffix with date range."""
        if not self.start_date or not self.end_date:
            return ""
        try:
            s = pd.to_datetime(self.start_date).strftime("%B - %Y")
            e = pd.to_datetime(self.end_date).strftime("%B - %Y")
            return f"({s} To {e})"
        except:
            return ""

    @rx.var
    def monthly_summary_data(self) -> list[ChannelSummary]:
        """
        Data for Monthly Summary of Gross Sale Value (Channel wise) Table.
        """
        if self.filtered_df.empty:
            return []

        df = self.filtered_df.copy()
        
        # Ensure Month_Date is present
        if "Month_Date" not in df.columns:
            return []

        # Get all unique months sorted for columns
        months = sorted(df["Month_Date"].unique())
        # labels logic removed as it's not used inside the loops effectively, handled inside fmt/loops

        # Helper to format value
        def fmt(val):
            return f"₹{val/10000000:.2f} Cr"

        # 1. Group by Channel
        channels = df["Channel"].unique()
        summary_data = []
        
        # Pre-initialize grand total monthly sums
        gt_monthly_sums = {m: 0.0 for m in months}

        for channel in channels:
            # Filter for this channel
            ch_df = df[df["Channel"] == channel]
            ch_total = ch_df["Sales Amount"].sum()
            
            # Channel Monthly Totals
            ch_monthly_grp = ch_df.groupby("Month_Date")["Sales Amount"].sum()
            ch_monthly_values = []
            for i, m in enumerate(months):
                val = ch_monthly_grp.get(m, 0.0)
                is_shade_col = (i % 2 == 0) # Shade even indices (Apr, Jun, etc.)
                ch_monthly_values.append(
                    MonthlyValue(
                        month=pd.Timestamp(m).strftime('%b'), 
                        value=fmt(val),
                        is_shaded=is_shade_col
                    )
                )
                gt_monthly_sums[m] += val
                
            # 2. Process States for this Channel
            state_grp = ch_df.groupby("CUSTOMER STATE")["Sales Amount"].sum().sort_values(ascending=False)
            
            top_5_states = state_grp.head(5)
            other_states_val = state_grp.iloc[5:].sum() if len(state_grp) > 5 else 0
            
            children = []
            
            # Add Top 5
            for state_name, state_total in top_5_states.items():
                st_df = ch_df[ch_df["CUSTOMER STATE"] == state_name]
                st_monthly_grp = st_df.groupby("Month_Date")["Sales Amount"].sum()
                st_monthly_vals = []
                for i, m in enumerate(months):
                    val = st_monthly_grp.get(m, 0.0)
                    is_shade_col = (i % 2 == 0)
                    st_monthly_vals.append(
                        MonthlyValue(
                            month=pd.Timestamp(m).strftime('%b'), 
                            value=fmt(val),
                            is_shaded=is_shade_col
                        )
                    )
                
                children.append(
                    StateSummary(
                        state=str(state_name),
                        monthly_values=st_monthly_vals,
                        total_value=fmt(state_total)
                    )
                )
                
            # Add "Other States" if exists
            if other_states_val > 0:
                top_5_names = top_5_states.index.tolist()
                others_df = ch_df[~ch_df["CUSTOMER STATE"].isin(top_5_names)]
                
                oth_monthly_grp = others_df.groupby("Month_Date")["Sales Amount"].sum()
                oth_monthly_vals = []
                for i, m in enumerate(months):
                    val = oth_monthly_grp.get(m, 0.0)
                    is_shade_col = (i % 2 == 0)
                    oth_monthly_vals.append(
                        MonthlyValue(
                            month=pd.Timestamp(m).strftime('%b'), 
                            value=fmt(val),
                            is_shaded=is_shade_col
                        )
                    )

                children.append(
                    StateSummary(
                        state="Other States",
                        monthly_values=oth_monthly_vals,
                        total_value=fmt(other_states_val)
                    )
                )
            
            summary_data.append(
                ChannelSummary(
                    channel=str(channel),
                    monthly_values=ch_monthly_values,
                    total_value=fmt(ch_total),
                    children=children,
                    is_total=False
                )
            )

        # Finalize Grand Total Row
        gt_vals = []
        gt_total_all = 0
        for i, m in enumerate(months):
            val = gt_monthly_sums[m]
            is_shade_col = (i % 2 == 0)
            gt_vals.append(
                MonthlyValue(
                    month=pd.Timestamp(m).strftime('%b'), 
                    value=fmt(val),
                    is_shaded=is_shade_col
                )
            )
            gt_total_all += val
            
        summary_data.append(
             ChannelSummary(
                channel="Grand Total",
                monthly_values=gt_vals,
                total_value=fmt(gt_total_all),
                children=[],
                is_total=True
            )
        )
        
        return summary_data


        

    @rx.var
    def summary_table_columns(self) -> list[str]:
        """Dynamic columns for the monthly summary table."""
        if self.filtered_df.empty:
            return []
        months = sorted(self.filtered_df["Month_Date"].unique())
        return [pd.Timestamp(m).strftime('%b') for m in months]

    @rx.var
    def monthly_sales_return_data(self) -> list[ChannelSummary]:
        """
        Data for Monthly Sales Return (Channel wise) Table.
        Similar structure to monthly_summary_data but for 'Sales Return'.
        """
        if self.filtered_df.empty:
            return []

        df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] == "Sales Return"].copy()
        
        # Ensure Month_Date is present
        if "Month_Date" not in self.filtered_df.columns: 
             return []

        # Get all unique months from the main filtered_df to ensure we show all months
        months = sorted(self.filtered_df["Month_Date"].unique())
        
        # Helper to format value
        def fmt(val):
            # Format as absolute value with Indian numbering
            # val is negative for returns, so abs(val)
            s = str(int(abs(val)))
            if len(s) <= 3:
                res = s
            else:
                res = s[-3:]
                s = s[:-3]
                while len(s) > 2:
                    res = s[-2:] + "," + res
                    s = s[:-2]
                res = s + "," + res
            return f"₹{res}" 

        channels = df["Channel"].unique() if not df.empty else []
        
        summary_data = []
        gt_monthly_sums = {m: 0.0 for m in months}

        for channel in channels:
            ch_df = df[df["Channel"] == channel]
            ch_total = ch_df["Sales Amount"].sum()
            
            ch_monthly_grp = ch_df.groupby("Month_Date")["Sales Amount"].sum()
            ch_monthly_values = []
            
            for i, m in enumerate(months):
                val = ch_monthly_grp.get(m, 0.0)
                is_shade_col = (i % 2 == 0)
                ch_monthly_values.append(
                    MonthlyValue(
                        month=pd.Timestamp(m).strftime('%b'), 
                        value=fmt(val),
                        is_shaded=is_shade_col
                    )
                )
                gt_monthly_sums[m] += val
            
            summary_data.append(
                ChannelSummary(
                    channel=str(channel),
                    monthly_values=ch_monthly_values,
                    total_value=fmt(ch_total),
                    children=[],
                    is_total=False
                )
            )

        # Finalize Grand Total Row
        gt_vals = []
        gt_total_all = 0
        for i, m in enumerate(months):
            val = gt_monthly_sums[m]
            is_shade_col = (i % 2 == 0)
            gt_vals.append(
                MonthlyValue(
                    month=pd.Timestamp(m).strftime('%b'), 
                    value=fmt(val),
                    is_shaded=is_shade_col
                )
            )
            gt_total_all += val
            
        summary_data.append(
             ChannelSummary(
                channel="Total Returns", 
                monthly_values=gt_vals,
                total_value=fmt(gt_total_all),
                children=[],
                is_total=True
            )
        )
        
        return summary_data

    @rx.var
    def invoice_return_columns(self) -> list[str]:
        if self.filtered_df.empty:
            return []
        # Get unique channels + Grand Total
        channels = sorted(self.filtered_df["Channel"].unique().tolist())
        return channels

    @rx.var
    def invoice_vs_return_data(self) -> list[InvRetRow]:
        """
        Data for Invoice vs Sales Return Table.
        Row: Month
        Cols: Channel (Inv, Ret), ... Grand Total
        """
        if self.filtered_df.empty:
             return []

        df = self.filtered_df.copy()
        months = sorted(df["Month_Date"].unique())
        channels = sorted(df["Channel"].unique().tolist())
        
        # Prepare Data
        rows = []
        
        # Helper for totals
        col_totals_inv = {c: 0 for c in channels}
        col_totals_ret = {c: 0 for c in channels}
        grand_total_inv_sum = 0
        grand_total_ret_sum = 0

        for m in months:
            m_df = df[df["Month_Date"] == m]
            month_label = pd.Timestamp(m).strftime('%b')
            
            channel_data = []
            
            row_total_inv = 0
            row_total_ret = 0
            
            for ch in channels:
                ch_data = m_df[m_df["Channel"] == ch]
                
                inv_count = ch_data[ch_data["DOCUMENT DESCRIPTION"] != "Sales Return"]["BILLING DOCUMENT"].nunique()
                ret_count = ch_data[ch_data["DOCUMENT DESCRIPTION"] == "Sales Return"]["BILLING DOCUMENT"].nunique()
                
                # Update Column Totals
                col_totals_inv[ch] += inv_count
                col_totals_ret[ch] += ret_count
                
                # Update Row Totals
                row_total_inv += inv_count
                row_total_ret += ret_count
                
                ret_color = "red" if ret_count > 0 else "black"
                
                channel_data.append(
                    InvRetChannel(
                        channel=ch,
                        inv=str(inv_count) if inv_count > 0 else "-",
                        ret=str(ret_count) if ret_count > 0 else "-",
                        ret_color=ret_color
                    )
                )
            
            grand_total_inv_sum += row_total_inv
            grand_total_ret_sum += row_total_ret
            
            # Append Grand Total to channels list
            channel_data.append(
                InvRetChannel(
                    channel="Grand Total",
                    inv=str(row_total_inv),
                    ret=str(row_total_ret) if row_total_ret > 0 else "-",
                    ret_color="red" if row_total_ret > 0 else "black"
                )
            )
            
            rows.append(
                InvRetRow(
                    month=month_label,
                    channels=channel_data,
                    grand_total_inv=str(row_total_inv),
                    grand_total_ret=str(row_total_ret) if row_total_ret > 0 else "-"
                )
            )

        # Totals Row
        total_channels = []
        for ch in channels:
            total_channels.append(
                InvRetChannel(
                     channel=ch,
                     inv=str(col_totals_inv[ch]),
                     ret=str(col_totals_ret[ch]),
                     ret_color="red"
                )
            )
            
        # Append Grand Total for Totals Row
        total_channels.append(
            InvRetChannel(
                 channel="Grand Total",
                 inv=str(grand_total_inv_sum),
                 ret=str(grand_total_ret_sum),
                 ret_color="red"
            )
        )
        
        rows.append(
            InvRetRow(
                month="Total Count",
                channels=total_channels,
                grand_total_inv=str(grand_total_inv_sum),
                grand_total_ret=str(grand_total_ret_sum),
                is_total=True
            )
        )

        # Percentage Row
        pct_channels = []
        for ch in channels:
             inv = col_totals_inv[ch]
             ret = col_totals_ret[ch]
             pct = (ret / inv * 100) if inv > 0 else 0
             pct_channels.append(
                 InvRetChannel(
                      channel=ch,
                      val=f"{pct:.2f}%",
                      color="green"
                 )
             )
             
        gt_pct = (grand_total_ret_sum / grand_total_inv_sum * 100) if grand_total_inv_sum > 0 else 0
        pct_channels.append(
             InvRetChannel(
                  channel="Grand Total",
                  val=f"{gt_pct:.2f}%",
                  color=TEXT_COLOR # Changed from "green"
             )
        )
        
        rows.append(
            InvRetRow(
                month="Return % (Ret/Inv)",
                channels=pct_channels,
                grand_total_val=f"{gt_pct:.2f}%",
                is_pct=True
            )
        )
        
        return rows

    @rx.var
    def channel_sales_stats(self) -> list[dict]:
        """Data for the custom legend of Channel Wise Sale."""
        if self.filtered_df.empty:
            return []
        
        df = self.filtered_df.copy()
        grp = df.groupby("Channel")["Sales Amount"].sum().sort_values(ascending=False)
        total = grp.sum()
        
        stats = []
        # Colors matching the image roughly (Yellows, Greens, Blues, Purples)
        # We can use a palette or hardcoded list.
        # Let's use a nice palette.
        palette = [
            "#F6E05E", # Yellow
            "#48BB78", # Green
            "#4299E1", # Blue
            "#ECC94B", # Darker Yellow
            "#9F7AEA", # Purple
            "#ED64A6", # Pink
            "#F56565", # Red
            "#A0AEC0", # Gray
        ]
        
        for i, (channel, val) in enumerate(grp.items()):
            color = palette[i % len(palette)]
            pct = (val / total * 100) if total > 0 else 0
            stats.append({
                "channel": channel,
                "value": f"₹{val/10000000:.2f} Cr",
                "raw_value": val,
                "pct": f"({pct:.1f}%)",
                "color": color
            })
        return stats

    @rx.var
    def total_sales_formatted(self) -> str:
        if self.filtered_df.empty: return "₹0.00 Cr"
        val = self.filtered_df["Sales Amount"].sum()
        return f"₹{val/10000000:.2f} Cr"

    @rx.var
    def channel_sales_chart(self) -> go.Figure:
        """Donut chart for Channel Wise Sale."""
        if self.filtered_df.empty:
            return go.Figure()
            
        stats = self.channel_sales_stats
        labels = [item["channel"] for item in stats]
        values = [item["raw_value"] for item in stats]
        colors = [item["color"] for item in stats]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.6,
            marker=dict(colors=colors),
            textinfo='none', # Turn off labels on chart as we have legend
            hoverinfo='label+percent+value',
            sort=False # Already sorted in stats
        )])
        
        fig.update_layout(
            showlegend=False, # Custom legend outside
            margin=dict(t=0, b=0, l=0, r=0),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=580,
            annotations=[
                dict(text="Total Sales", x=0.5, y=0.55, font_size=12, showarrow=False, font_color="gray"),
                dict(text=self.total_sales_formatted, x=0.5, y=0.45, font_size=25, font_weight="bold", showarrow=False, font_color="white") # Increased font size
            ]
        )
        return fig


# Styling Constants - Dark Mode
# Styling Constants - Pitch Black Mode
# Luxury / High Contrast Dark Palette
CHART_COLORS = ["#3182CE", "#2F855A", "#D69E2E", "#C05621", "#805AD5", "#2C7A7B", "#B7791F", "#2B6CB0", "#276749", "#975A16"]

SIDEBAR_BG = "#000000" # Pitch Black sidebar
CONTENT_BG = "#000000" # Pitch Black content
CARD_BG = "#0A0A0A" # Deepest Gray/Black for cards
TEXT_COLOR = "#FFFFFF" # Pure White
ACCENT_COLOR = "#D4AF37" # Metallic Gold for Luxury Accent (was Light Blue)
BORDER_COLOR = "#333333" # Subtle dark borders

# --- UI Helpers ---

def table_container(title, subtitle, bg_color, content, footer=None):
    return rx.box(
        rx.flex(
            rx.box(
                rx.text(title, font_size="lg", font_weight="900", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                rx.text(subtitle, font_size="xs", font_weight="bold", color="gray.400", text_align="center", width="100%", letter_spacing="0.05em"),
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            border_bottom=f"1px solid {BORDER_COLOR}",
            bg="rgba(255, 255, 255, 0.02)"
        ),
        content,
        footer if footer is not None else rx.fragment(),
        bg=CARD_BG,
        border_radius="xl",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="0 4px 20px rgba(0, 0, 0, 0.5)", # Deeper shadow

        # overflow="hidden" # Removed to allow scrolling if needed
    )

def trend_badge(trend: str, text_color: str = None, font_size: str = "0.7em"):
    """Helper to render the trend badge."""
    if trend is None:
        trend = ""
    if text_color is None:
        trend_color = rx.cond(
            (trend.contains("-")) | (trend.contains("↓")), 
            "#D0312D", # Pitch Red
            "#00C851" # Good Green
        )
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

def kpi_card(title: str, value: str, trend: str, icon: str, color_scheme: str, bg_color: str = CARD_BG, align: str = "start", value_size: str = "6", title_size: str = "2", bottom_left: str = None, bottom_right: str = None, bottom_left_trend: str = None, bottom_right_trend: str = None, bottom_left_icon: str = None, bottom_right_icon: str = None, trend_inline: bool = False, subtitle: str = None):
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
    trend_color = rx.cond(
        (trend.contains("-")) | (trend.contains("↓")), 
        "#D0312D", # Pitch Red
        "#68D391" # Lighter green for dark mode
    )
    
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.vstack(
                    rx.heading(title, size=title_size, font_weight="900", color="gray.400", letter_spacing="0.05em", text_transform="uppercase"), # Uppercase title
                    rx.cond(
                         subtitle is not None,
                         rx.text(subtitle, font_size="xs", color="gray.500", font_weight="bold"),
                         rx.fragment()
                    ),
                    rx.heading(
                        value, 
                        rx.cond(
                            trend_inline,
                            rx.box(trend_badge(trend, font_size="0.5em"), display="inline-block", style={"verticalAlign": "middle", "marginTop": "-10px", "marginLeft": "8px"}),
                            rx.fragment()
                        ),
                        size=value_size, 
                        font_weight="900", 
                        color="white",
                        letter_spacing="-0.02em" # Tight spacing for numbers
                    ),
                    align_items=align,
                    spacing="1",
                    width="100%",
                ),
                rx.cond(
                    align == "start",
                    rx.box(
                         rx.spacer(),
                         rx.icon(icon, size=28, color=color_scheme, stroke_width=1.5), # Thinner stroke for elegance
                    ),
                    rx.fragment() 
                ),
                width="100%",
                align_items="center" if align == "center" else "start",
                justify_content="center" if align == "center" else "start",
            ),
            
            rx.cond(
                not trend_inline,
                rx.hstack(
                    rx.text(trend, color=trend_color, font_size="sm", font_weight="bold", text_align=align, width="100%"),
                    width="100%",
                    justify_content=align, 
                ),
                rx.fragment()
            ),
            
            # Bottom Corner Content (for Total Sales)
            rx.cond(
                bottom_left is not None,
                rx.flex(
                    rx.hstack(
                        rx.icon(bottom_left_icon, size=16, color="gray.400") if bottom_left_icon is not None else rx.fragment(),
                        rx.text(bottom_left, font_size="sm", color="white", font_weight="bold"),
                        trend_badge(bottom_left_trend, font_size="0.75em") if bottom_left_trend is not None else rx.fragment(),
                        align="center",
                        spacing="2"
                    ),
                    rx.spacer(),
                    rx.hstack(
                        rx.icon(bottom_right_icon, size=16, color="gray.400") if bottom_right_icon is not None else rx.fragment(),
                        rx.text(bottom_right, font_size="sm", color="white", font_weight="bold"),
                        trend_badge(bottom_right_trend, font_size="0.75em") if bottom_right_trend is not None else rx.fragment(),
                        align="center",
                        spacing="2"
                    ),
                    width="100%",
                    justify="between",
                    padding_top="4",
                    border_top=f"1px solid {BORDER_COLOR}",
                    margin_top="2"
                ),
                rx.fragment()
            ),
            
            spacing="3",
            align_items=align,
        ),
        padding="6", 
        bg=bg_color,
        border=f"1px solid {BORDER_COLOR}",
        border_radius="xl",
        width="100%",
        box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
        transition="all 0.2s",
        _hover={
            "transform": "translateY(-2px)",
            "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
            "border_color": color_scheme
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

def date_picker_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
             rx.flex(
                 # Left Panel (Header Display - Teal)
                 rx.center(
                     rx.vstack(
                         rx.text(State.picker_display_weekday, color="white", font_size="sm", opacity=0.8, text_align="center", width="100%"),
                         rx.text(State.picker_display_day, color="white", font_size="6xl", font_weight="bold", line_height="1", text_align="center", width="100%"), 
                         rx.text(State.picker_display_month, color="white", font_size="2xl", font_weight="bold", text_align="center", width="100%"),
                         rx.text(State.picker_display_year, color="white", font_size="2xl", opacity=0.7, text_align="center", width="100%"),
                         
                         spacing="1",
                         align="center",
                         justify="center",
                         height="100%",
                         width="100%"
                     ),
                     width="160px",
                     bg="#009688", # Teal
                     padding="4",
                     height="100%",
                 ),
                 
                 # Right Panel (Calendar - White)
                 rx.vstack(
                    # Header Month Year
                    rx.hstack(
                         rx.icon("chevron-left", on_click=State.picker_prev_month, cursor="pointer", color="black", size=18),
                         rx.text(State.picker_month_year_title, color="black", font_size="sm", font_weight="bold"), 
                         rx.icon("chevron-right", on_click=State.picker_next_month, cursor="pointer", color="black", size=18),
                        width="100%",
                        padding_x="4",
                        padding_top="4",
                        align="center",
                        justify="between"
                    ),
                    
                    # Weekday Headers
                    rx.grid(
                        *[rx.center(rx.text(day, color="#009688", font_size="xs", font_weight="bold")) for day in ["S", "M", "T", "W", "T", "F", "S"]],
                        columns="7",
                        width="100%",
                        padding_x="4",
                        margin_top="2"
                    ),
                    
                    # Days Grid
                    rx.grid(
                        rx.foreach(
                            State.picker_calendar_grid,
                            lambda item: rx.center(
                                    rx.text(
                                    item["day"], 
                                    font_size="sm",
                                    color=rx.cond(item["is_selected"], "white", rx.cond(item["is_current_month"], "black", "gray.300")),
                                    font_weight=rx.cond(item["is_selected"], "bold", "normal")
                                ),
                                bg=rx.cond(item["is_selected"], "#009688", "transparent"), # Teal selected
                                border_radius="full", 
                                width="30px",
                                height="30px",
                                cursor="pointer",
                                _hover={"bg": rx.cond(item["is_selected"], "#009688", "gray.100")},
                                on_click=lambda: State.picker_select_date(item["date_str"])
                            )
                        ),
                        columns="7",
                        width="100%",
                        padding_x="4",
                        row_gap="1"
                    ),
                    
                    rx.spacer(),
                    
                    # Footer
                    rx.hstack(
                        rx.text("Clear", color="#E53E3E", font_size="xs", font_weight="bold", cursor="pointer"),
                        rx.spacer(),
                        rx.text("CANCEL", on_click=State.close_picker, color="#009688", font_size="xs", font_weight="bold", cursor="pointer"),
                        rx.text("OK", on_click=State.picker_confirm, color="#009688", font_size="xs", font_weight="bold", cursor="pointer"),
                        width="100%",
                        justify="end",
                        padding="4",
                        spacing="4",
                        align="center"
                    ),
                    
                    bg="white", # White background for calendar
                    width="280px",
                    height="100%"
                 ),
                 
                 height="350px",
                 width="fit-content",
                 overflow="hidden",
                 border_radius="4px", # Slightly rounded
             ),
             bg="transparent", 
             padding="0",
             overflow="hidden",
             max_width="none",
             box_shadow="xl"
        ),
        open=State.show_picker,
    )

def sidebar_component() -> rx.Component:
    """The modern filter sidebar."""
    return rx.box(
        rx.vstack(
            # Sidebar Header (Centered Dashboard + Period)
            rx.box(
                rx.vstack(
                    rx.hstack(
                         rx.icon("layout-dashboard", size=20, color=ACCENT_COLOR),
                         rx.heading("DASHBOARD", size="3", color="white", font_weight="900", letter_spacing="0.1em"),
                         align="center",
                         spacing="3",
                         justify="center"
                     ),
                     rx.center(
                         rx.hstack(
                             rx.icon("calendar-days", size=16, color="white"),
                             rx.text("PERIOD", font_weight="900", color="white", font_size="xs", letter_spacing="0.1em"),
                             align="center", spacing="2", justify="center"
                         )
                     ),
                     spacing="2",
                     align="center",
                     justify="center",
                     width="100%"
                ),
                
                # Close Button (Absolute)
                rx.box(
                    rx.button(
                         rx.icon("x", size=18, color="white"),
                         variant="ghost",
                         size="1", 
                         on_click=State.toggle_sidebar,
                         color_scheme="gray"
                    ),
                    position="absolute",
                    top="0",
                    right="0"
                ),
                
                position="relative",
                width="100%",
                margin_bottom="6",
                padding_x="2"
            ),
            
            # Date Range Filter
            rx.vstack(
                # Vertical Layout
                rx.vstack(
                    rx.box(
                        rx.text("FROM", font_size="xs", color="white", font_weight="900", margin_bottom="2", text_align="center", width="100%"),
                        rx.box(
                            rx.hstack(
                                rx.text(rx.cond(State.start_date, State.start_date, "Select Date"), color="white", font_size="sm", font_weight="medium"),
                                rx.icon("chevron-down", size=14, color="gray.600"),
                                width="100%",
                                align="center",
                                justify="center",
                                spacing="2"
                            ),
                            bg="rgba(255,255,255,0.03)", 
                            border=f"1px solid {BORDER_COLOR}",
                            border_radius="md",
                            padding="3",
                            width="100%",
                            cursor="pointer",
                            on_click=lambda: State.open_picker("start"),
                            _hover={"border_color": ACCENT_COLOR, "bg": "rgba(255,255,255,0.05)"},
                            transition="all 0.2s"
                        ),
                        width="100%"
                    ),
                    rx.box(
                        rx.text("TO", font_size="xs", color="white", font_weight="900", margin_bottom="2", text_align="center", width="100%"),
                        rx.box(
                             rx.hstack(
                                rx.text(rx.cond(State.end_date, State.end_date, "Select Date"), color="white", font_size="sm", font_weight="medium"),
                                rx.icon("chevron-down", size=14, color="gray.600"),
                                width="100%",
                                align="center",
                                justify="center",
                                spacing="2"
                             ),
                            bg="rgba(255,255,255,0.03)",
                            border=f"1px solid {BORDER_COLOR}",
                            border_radius="md",
                            padding="3",
                            width="100%",
                            cursor="pointer",
                             on_click=lambda: State.open_picker("end"),
                             _hover={"border_color": ACCENT_COLOR, "bg": "rgba(255,255,255,0.05)"},
                             transition="all 0.2s"
                        ),
                        width="100%"
                    ),
                    width="100%",
                    spacing="4" 
                ),
                padding="0", 
                width="100%",
                margin_bottom="8" 
            ),
            
            rx.accordion.root(
                
                # State Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("map", size=16, color=ACCENT_COLOR),
                            rx.text("REGION", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_states, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.states,
                                    lambda state: rx.checkbox(
                                        state,
                                        checked=State.selected_states.contains(state),
                                        on_change=lambda checked: State.toggle_state(state, checked),
                                        color_scheme="gray", 
                                        size="1" 
                                    )
                                ),
                                spacing="2",
                                align_items="start"
                            ),
                            type="always",
                            scrollbars="vertical",
                            style={"height": 150},
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    style={"background": "transparent", "border": "none"}
                ),

                # Brand Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("tag", size=16, color=ACCENT_COLOR),
                            rx.text("BRAND", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_brands, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.brands,
                                    lambda brand: rx.checkbox(
                                        brand,
                                        checked=State.selected_brands.contains(brand),
                                        on_change=lambda checked: State.toggle_brand(brand, checked),
                                        color_scheme="gray",
                                        size="1"
                                    ),
                                ),
                                spacing="2",
                                align_items="start"
                            ),
                            type="always",
                            scrollbars="vertical",
                            style={"height": 150},
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    style={"background": "transparent", "border": "none"}
                ),
                
                # Channel Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("share-2", size=16, color=ACCENT_COLOR),
                            rx.text("CHANNEL", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_channels, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.channels,
                                    lambda channel: rx.checkbox(
                                        channel,
                                        checked=State.selected_channels.contains(channel),
                                        on_change=lambda checked: State.toggle_channel(channel, checked),
                                        color_scheme="gray",
                                        size="1"
                                    ),
                                ),
                                spacing="2",
                                align_items="start"
                            ),
                            type="always",
                            scrollbars="vertical",
                            style={"height": 150},
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    style={"background": "transparent", "border": "none"}
                ),

               # Supply Type Filter
                rx.accordion.item(
                    header=rx.center(
                        rx.hstack(
                            rx.icon("truck", size=16, color=ACCENT_COLOR),
                            rx.text("SUPPLY TYPE", font_weight="900", color="white", font_size="sm", letter_spacing="0.1em"),
                            align="center", spacing="2", justify="center"
                        ),
                        width="100%"
                    ),
                    content=rx.vstack(
                        rx.checkbox("Select All", on_change=State.toggle_all_supply, color_scheme="gray", size="1"),
                        rx.scroll_area(
                            rx.vstack(
                                rx.foreach(
                                    State.supply_types,
                                    lambda st: rx.checkbox(
                                        st,
                                        checked=State.selected_supply_types.contains(st),
                                        on_change=lambda checked: State.toggle_supply(st, checked),
                                        color_scheme="gray",
                                        size="1"
                                    ),
                                ),
                                spacing="2",
                                align_items="start"
                            ),
                            type="always",
                            scrollbars="vertical",
                            style={"height": 150},
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    style={"background": "transparent", "border": "none"}
                ),
                
                type="multiple",
                collapsible=True,
                width="100%",
                variant="outline", # Clean variant
                margin_top="16",
            ),
            
            width="100%",
            spacing="1",
            padding_top="500px", # Added spacing from top edge
        ),
        width="280px", # Slightly wider for elegance
        height="100vh", # Full height
        bg="#111111", # Darker background
        padding="6",
        border_right="1px solid #333333",
        display=rx.cond(State.is_sidebar_open, "block", "none"), 
        position="sticky",
        top="0",
        z_index="1000"
    )




def card_avg_monthly_sale():
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("AVG. MONTHLY SALE", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                rx.spacer(),
                rx.icon("chart-bar", color="#FF9966", size=20),
                width="100%",
                align="center",
            ),
            rx.hstack(
                rx.heading(State.average_monthly_sale, color="white", size="8", font_weight="900", letter_spacing="-0.02em"),
                rx.badge("↗ 14.9%", color_scheme="green", variant="surface", size="1"),
                align="baseline",
                spacing="3"
            ),
            rx.spacer(),
            rx.hstack(
                 rx.icon("briefcase", color="gray.500", size=14),
                 rx.text(State.avg_monthly_b2b, color="gray.300", font_size="xs", font_weight="bold"),
                 rx.spacer(),
                 rx.icon("shopping-cart", color="gray.500", size=14),
                 rx.text(State.avg_monthly_b2c, color="gray.300", font_size="xs", font_weight="bold"),
                 width="100%",
                 align="center",
                 padding_top="4",
                 border_top=f"1px solid {BORDER_COLOR}"
            ),
            height="100%",
            justify="between",
            align_items="start",
            spacing="1"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #FF9966", # Orange Accent
        border_radius="xl",
        padding="24px",
        width="100%",
        height="180px",
        box_shadow="lg"
    )

def card_daily_velocity():
    return rx.box(
         rx.vstack(
            rx.hstack(
                rx.text("DAILY SALES VELOCITY", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                rx.spacer(),
                rx.icon("zap", color="#63b3ed", size=20),
                width="100%",
                align="center",
            ),
            rx.heading(State.daily_sales_velocity_data["total"], color="white", size="8", font_weight="900", letter_spacing="-0.02em"),
            rx.spacer(),
            rx.hstack(
                 rx.icon("briefcase", color="gray.500", size=14),
                 rx.text(State.daily_sales_velocity_data["b2b"], color="gray.300", font_size="xs", font_weight="bold"),
                 rx.spacer(),
                 rx.icon("shopping-cart", color="gray.500", size=14),
                 rx.text(State.daily_sales_velocity_data["b2c"], color="gray.300", font_size="xs", font_weight="bold"),
                 width="100%",
                 align="center",
                 padding_top="4",
                 border_top=f"1px solid {BORDER_COLOR}"
            ),
            height="100%",
            justify="between",
            align_items="start",
            spacing="1"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #63b3ed", # Blue Accent
        border_radius="xl",
        padding="24px",
        width="100%",
        height="180px",
        box_shadow="lg"
    )

def card_returns_invoices():
    return rx.box(
        rx.vstack(
            rx.flex(
                # Left: Returns
                rx.box(
                    rx.vstack(
                        rx.hstack(rx.icon("rotate-ccw", color="red", size=14), rx.text("RETURNS", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.05em")),
                        rx.heading(State.return_metrics["count"], color="white", size="6", font_weight="900"),
                        rx.hstack(
                             rx.text(State.return_metrics["rate_pct"], color="red", font_size="xs", font_weight="bold"),
                             rx.text(State.return_metrics["val_cr"], color="gray.500", font_size="xs"),
                             spacing="2"
                        ),
                        align_items="start",
                        spacing="1",
                        width="100%"
                    ),
                    flex="1",
                ),
                # Vertical Separator
                rx.divider(orientation="vertical", height="auto", margin_x="4", border_color=BORDER_COLOR),
                 # Right: Invoices
                rx.box(
                    rx.vstack(
                        rx.hstack(rx.icon("file-text", color="gray.400", size=14), rx.text("INVOICES", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.05em")),
                        rx.heading(State.invoice_stats["count"], color="white", size="6", font_weight="900"),
                        rx.hstack(
                            rx.text("Avg", color="gray.500", font_size="xs"),
                            rx.text(State.invoice_stats["daily_avg"], color="white", font_size="xs", font_weight="bold"),
                            spacing="2"
                        ),
                        align_items="start",
                        spacing="1",
                        width="100%"
                    ),
                    flex="1.2", 
                ),
                width="100%",
                align_items="stretch" 
            ),
            rx.separator(color_scheme="gray", opacity=0.1),
            rx.text("B2C RETURN RATE", color="gray.500", font_weight="bold", font_size="10px", width="100%", letter_spacing="0.1em"),
            # Small Table for Channel Returns
            rx.vstack(
                rx.foreach(
                    State.return_breakdown,
                    lambda item: rx.hstack(
                        rx.text(item["channel"], color="gray.300", font_size="xs"),
                        rx.spacer(),
                        rx.badge(item["formatted_rate"], color_scheme="red", variant="surface", size="1"),
                        width="100%",
                        padding_y="1",
                        border_bottom=f"1px dashed {BORDER_COLOR}"
                    )
                ),
                width="100%",
                spacing="0"
            ),
            spacing="3",
            width="100%"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #e53935", # Red Accent
        border_radius="xl",
        padding="24px", # Explicit padding
        width="100%",
        box_shadow="lg"
    )

def card_pareto():
    return rx.box(
        rx.vstack(
                rx.center(
                     rx.vstack(
                        rx.text("PARETO (80% SALE)", color="gray.400", font_weight="bold", font_size="xs", letter_spacing="0.1em"),
                        rx.heading(
                            State.pareto_stats["count_80"], 
                            color="white", 
                            size="8", 
                            font_weight="900",
                            letter_spacing="-0.02em"
                        ),
                        spacing="1",
                        align_items="center",
                        width="100%"
                     ),
                     width="100%"
                ),
                 rx.box(
                    rx.vstack(
                        rx.foreach(
                            State.pareto_top_products,
                            lambda item: rx.hstack(
                                rx.badge(item["rank"], variant="solid", color_scheme="yellow", border_radius="full", size="1"),
                                rx.text(item["name"], color="gray.200", font_size="xs", no_of_lines=1, width="40%"), 
                                rx.spacer(),
                                rx.text(item["value_cr"], color="white", font_size="xs", font_weight="bold"),
                                rx.spacer(),
                                rx.text(item["pct"], color="gray.500", font_size="xs", font_weight="bold"),
                                width="100%",
                                padding_y="1",
                                border_bottom=f"1px solid {BORDER_COLOR}"
                            )
                        ),
                        width="100%",
                        spacing="1"
                    ),
                    width="100%",
                    bg="rgba(255,255,255,0.02)",
                    border_radius="md",
                    padding="4"
                ),
            rx.text(
                rx.text.span("Products driving 80% of sales ", font_weight="bold", color="gray.400"),
                rx.text.span(State.pareto_stats["pct_catalog"], font_weight="bold", color="white"),
                font_size="xs", 
                text_align="center",
                width="100%"
            ),
            spacing="3",
            width="100%"
        ),
        bg=CARD_BG,
        border=f"1px solid {BORDER_COLOR}",
        border_left="4px solid #8E2DE2", # Purple Accent
        border_radius="xl",
        padding="24px", 
        width="100%",
        box_shadow="lg"
    )


def courier_performance_card():
    return rx.box(
        rx.vstack(
            rx.center(
                rx.hstack(
                    rx.center(
                        rx.icon("truck", color="#3182CE", size=20),
                        bg="rgba(49, 130, 206, 0.1)", # Dark Blue tint
                        padding="2",
                        border_radius="md",
                        border="1px solid #3182CE"
                    ),
                    rx.text("Courier Performance(Only for Rajnigandha.com)", font_weight="900", color=TEXT_COLOR, font_size="md", letter_spacing="0.05em"),
                    align="center",
                    spacing="3",
                ),
                width="100%",
                margin_bottom="4"
            ),
            rx.grid(
                # Card 1: Avg Delivery Cost
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.icon("indian-rupee", size=14, color="gray"),
                            rx.text("AVG DELIVERY COST", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["avg_cost"], size="6", color="white", font_weight="900"),
                        rx.text("per shipment", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(255,255,255,0.02)", 
                    padding="4", 
                    border_radius="lg",
                    border=f"1px solid {BORDER_COLOR}",
                    width="100%"
                ),
                # Card 2: Avg Delivery Time
                rx.box(
                     rx.vstack(
                        rx.hstack(
                            rx.icon("clock", size=14, color="gray"),
                            rx.text("AVERAGE DELIVERY TIME", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["avg_time"], size="6", color="white", font_weight="900"),
                        rx.text("pickup to delivered", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(255,255,255,0.02)", 
                    padding="4", 
                    border_radius="lg",
                    border=f"1px solid {BORDER_COLOR}",
                     width="100%"
                ),
                # Card 3: Successful Delivery Rate (Green)
                rx.box(
                     rx.vstack(
                        rx.hstack(
                            rx.icon("circle_check", size=14, color="#48BB78"),
                            rx.text("SUCCESSFUL DELIVERY RATE", font_size="xs", font_weight="bold", color="#48BB78", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["success_rate"], size="6", color="white", font_weight="900"), 
                        rx.text("delivery rate", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(72, 187, 120, 0.05)", # Dark Green tint
                    padding="4", 
                    border_radius="lg",
                    border="1px solid #2F855A",
                     width="100%"
                ),
                # Card 4: Return Rate (Red)
                 rx.box(
                     rx.vstack(
                        rx.hstack(
                            rx.icon("rotate_cw", size=14, color="#F56565"),
                            rx.text("RETURN RATE", font_size="xs", font_weight="bold", color="#F56565", letter_spacing="0.1em"),
                            spacing="2",
                            align="center"
                        ),
                        rx.heading(State.courier_metrics["return_rate"], size="6", color="white", font_weight="900"), 
                        rx.text("of total orders", font_size="xs", color="gray.500"),
                        spacing="1",
                        align_items="center"
                    ),
                    bg="rgba(245, 101, 101, 0.05)", # Dark Red tint
                    padding="4", 
                    border_radius="lg",
                    border="1px solid #9B2C2C",
                     width="100%"
                ),
                columns={"initial": "1", "sm": "1", "lg": "2"},
                spacing="4",
                width="100%"
            ),
             width="100%"
        ),
        bg=CARD_BG,
        padding="24px", 
        border_radius="xl",
        box_shadow="lg",
        width="100%",
        border=f"1px solid {BORDER_COLOR}"
    )





def no_data_view() -> rx.Component:
    """The empty state view shown when no data is loaded."""
    return rx.center(
        rx.vstack(
            rx.heading("Upload Your Data", size="8", color="#1A202C", margin_bottom="8px"),
            rx.text(
                "Follow the steps to upload Sales and Courier data.",
                color="#718096",
                font_size="16px",
                margin_bottom="32px",
            ),
            
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("file-spreadsheet", size=24), 
                            rx.text("1. Sales Data", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="sales", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("truck", size=24), 
                            rx.text("2. Courier Data", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="courier", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    rx.tabs.trigger(
                        rx.hstack(
                            rx.icon("bar-chart-2", size=24), 
                            rx.text("3. Analyze", font_size="20px", weight="bold"),
                            spacing="3",
                            align="center",
                        ),
                        value="analyze", 
                        color="#1A202C",
                        padding_x="32px",
                        padding_y="16px",
                    ),
                    justify="center", # Center the tabs
                    spacing="8", # Substantial space between tabs
                    margin_bottom="32px",
                ),
                
                # TAB 1: SALES DATA
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("file-spreadsheet", size=32, color="#5B45FF"),
                                rx.text("Upload Sales Data Excel File", weight="bold", size="4", color="#1A202C"),
                                rx.text("Required for dashboard visualization", size="2", color="#718096"),
                                rx.cond(
                                    State.sales_data_uploaded,
                                    rx.badge("✅ File Uploaded Successfully", color_scheme="green", variant="solid", size="3"),
                                    rx.fragment()
                                ),
                                rx.upload(
                                     rx.button(
                                        "Select Sales File",
                                        size="3",
                                        variant="solid", # Solid for better visibility on white
                                        color_scheme="indigo",
                                        width="100%",
                                    ),
                                    id="sales_tab_upload",
                                    accept={
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], 
                                        "application/vnd.ms-excel": [".xls"]
                                    },
                                    max_files=1,
                                    on_drop=State.handle_sales_upload,
                                    border="1px dashed #CBD5E0",
                                    padding="32px",
                                    border_radius="lg",
                                    width="100%",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            padding="32px",
                            bg="#F7FAFC",
                            border_radius="xl",
                            width="100%",
                            border="1px solid #E2E8F0", # Add border for definition
                        ),
                    ),
                    value="sales",
                    padding="24px",
                ),
                
                # TAB 2: COURIER DATA
                rx.tabs.content(
                    rx.vstack(
                        rx.box(
                            rx.vstack(
                                rx.icon("truck", size=32, color="#3182CE"),
                                rx.text("Upload Courier Data Excel File", weight="bold", size="4", color="#1A202C"),
                                rx.text("Required for courier performance metrics", size="2", color="#718096"),
                                rx.cond(
                                    State.courier_data_uploaded,
                                    rx.badge("✅ File Uploaded Successfully", color_scheme="green", variant="solid", size="3"),
                                    rx.fragment()
                                ),
                                rx.upload(
                                     rx.button(
                                        "Select Courier File",
                                        size="3",
                                        variant="solid", # Solid
                                        color_scheme="blue",
                                        width="100%",
                                    ),
                                    id="courier_tab_upload",
                                    accept={
                                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"], 
                                        "application/vnd.ms-excel": [".xls"]
                                    },
                                    max_files=1,
                                    on_drop=State.handle_courier_upload,
                                    border="1px dashed #CBD5E0",
                                    padding="32px",
                                    border_radius="lg",
                                    width="100%",
                                ),
                                spacing="4",
                                align="center",
                            ),
                            padding="32px",
                            bg="#F7FAFC",
                            border_radius="xl",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                    ),
                    value="courier",
                    padding="24px",
                ),

                # TAB 3: ANALYZE
                rx.tabs.content(
                     rx.vstack(
                        rx.heading("Ready to Analyze?", size="6", color="#1A202C"),
                        rx.box(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("Sales Data Status:", weight="bold", color="#1A202C"),
                                    rx.cond(
                                        State.sales_data_uploaded,
                                        rx.badge("Ready", color_scheme="green", variant="solid"),
                                        rx.badge("Missing", color_scheme="red", variant="solid"),
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                rx.hstack(
                                    rx.text("Courier Data Status:", weight="bold", color="#1A202C"),
                                    rx.cond(
                                        State.courier_data_uploaded,
                                        rx.badge("Ready", color_scheme="green", variant="solid"),
                                        rx.badge("Optional", color_scheme="gray", variant="solid"),
                                    ),
                                    justify="between",
                                    width="100%",
                                ),
                                width="100%",
                                spacing="4",
                            ),
                            padding="24px",
                            bg="#F7FAFC",
                            border_radius="lg",
                            width="100%",
                            border="1px solid #E2E8F0",
                        ),
                        rx.button(
                            "Launch Dashboard 🚀", 
                            on_click=State.start_analysis,
                            size="4",
                            width="100%",
                            # disabled=~State.sales_data_uploaded, # Removed disabling to ensure visibility
                            color_scheme="purple",
                            variant="solid",
                            opacity=rx.cond(State.sales_data_uploaded, "1", "0.5"), # Visual cue instead via opacity but completely visible
                            cursor=rx.cond(State.sales_data_uploaded, "pointer", "not-allowed"),
                        ),
                        spacing="6",
                        align="center",
                        width="100%",
                    ),
                    value="analyze",
                    padding="24px",
                ),
                
                defaultValue="sales",
                width="100%",
            ),

            # Error message
            rx.cond(
                State.deployment_status != "",
                rx.center( # Wrap in center
                    rx.callout.root(
                        rx.callout.text(State.deployment_status),
                        color_scheme="red",
                        role="alert",
                        margin_top="16px",
                    ),
                    width="100%", # Center needs width
                ),
            ),
            align="center",
            width="100%",
            max_width="1000px", # Increased from 600px to accommodate large tabs
        ),
        width="100%",
        height="100vh",
        background_color="white", # Explicit white background, so we force dark text everywhere above
    )






def monthly_summary_table():
    return rx.box(
        # Custom Header for this specific table to match the colorful request
        rx.flex(
            rx.box(
                rx.text("Monthly Summary of Gross Sale Value (Channel wise)", font_size="md", font_weight="bold", color="white", text_align="center", width="100%"),
                rx.text("Breakdown by Channel and Top 5 States", font_size="10px", color="gray.200", text_align="center", width="100%"),
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            bg="linear-gradient(90deg, #2D3748 0%, #4A5568 100%)", # Colorful gradient header
            border_top_left_radius="xl",
            border_top_right_radius="xl",
            border_bottom="1px solid #4A5568",
        ),
        
        rx.box(
            # HEADER
            rx.flex(
                rx.box(rx.text("Channel / State", font_weight="bold", color="#63B3ED", font_size="sm"), width="300px", padding_left="4"), # Light Blue
                rx.foreach(
                    State.summary_table_columns,
                    lambda col: rx.box(rx.text(col, font_weight="bold", color="#63B3ED", font_size="sm", text_align="right"), flex="1", padding_right="4") # Light Blue
                ),
                rx.box(rx.text("Grand Total", font_weight="bold", color="#ECC94B", font_size="sm", text_align="right"), width="150px", padding_right="4"), # Yellow
                bg="#1A202C", 
                padding_y="4", 
                border_bottom="1px solid #4A5568",
                width="100%",
                align="center"
            ),
            
            # BODY
            rx.vstack(
                rx.foreach(
                    State.monthly_summary_data,
                    lambda row: rx.box(
                        # Conditional: Grand Total Row vs Channel Row
                        rx.cond(
                            row["is_total"],
                            # Grand Total Row Style (Fixed Footer-like)
                             rx.flex(
                                rx.box(rx.text(row["channel"], font_weight="bold", color="#ECC94B", font_size="md"), width="300px", padding_left="4"),
                                rx.foreach(
                                    row["monthly_values"],
                                    lambda m: rx.box(rx.text(m.value, font_weight="bold", color="#ECC94B", font_size="md", text_align="right"), flex="1", padding_right="4")
                                ),
                                rx.box(rx.text(row["total_value"], font_weight="bold", color="#ECC94B", font_size="md", text_align="right"), width="150px", padding_right="4"),
                                bg="rgba(255, 255, 255, 0.08)",
                                padding_y="4",
                                border_top="2px solid #ECC94B",
                                width="100%",
                                align="center"
                            ),
                            # Normal Channel Row (Accordion)
                            rx.accordion.root(
                                rx.accordion.item(
                                    header=rx.flex(
                                        rx.box(
                                            rx.hstack(
                                                rx.icon("chevron-down", size=16),
                                                rx.text(row["channel"], font_weight="bold", color="white", font_size="sm"),
                                                spacing="2",
                                                align="center"
                                            ),
                                            width="300px", 
                                            padding_left="2"
                                        ), 
                                        rx.foreach(
                                            row["monthly_values"],
                                            lambda m: rx.box(rx.text(m.value, color="white", font_size="sm", text_align="right"), flex="1", padding_right="4")
                                        ),
                                        rx.box(rx.text(row["total_value"], font_weight="bold", color="white", font_size="sm", text_align="right"), width="150px", padding_right="4"),
                                        width="100%",
                                        align="center",
                                        padding_y="2", # Added padding for regular rows
                                        _hover={"bg": "rgba(255,255,255,0.02)"}
                                    ),
                                    content=rx.vstack(
                                        rx.foreach(
                                            row["children"],
                                            lambda child: rx.flex(
                                                rx.box(
                                                     rx.hstack(
                                                        rx.text("•", color="gray.500", font_size="lg", margin_right="1"),
                                                        rx.text(child["state"], color="gray.300", font_style="italic", font_size="xs"),
                                                        padding_left="10", # Indent
                                                        align="center"
                                                     ),
                                                     width="300px"
                                                ),
                                                rx.foreach(
                                                    child["monthly_values"],
                                                    lambda m: rx.box(rx.text(m.value, color="gray.400", font_size="xs", text_align="right"), flex="1", padding_right="4")
                                                ),
                                                rx.box(rx.text(child["total_value"], color="gray.300", font_size="xs", text_align="right"), width="150px", padding_right="4"),
                                                width="100%",
                                                padding_y="2",
                                                border_bottom="1px dashed rgba(255,255,255,0.05)",
                                                _hover={"bg": "rgba(255,255,255,0.02)"},
                                                align="center"
                                            )
                                        ),
                                        width="100%",
                                        bg="rgba(0,0,0,0.2)"
                                    ),
                                    value="ch",
                                    border_width="0",
                                    padding="0",
                                ),
                                type="multiple",
                                collapsible=True,
                                width="100%",
                                variant="ghost",
                            )
                        ),
                        width="100%",
                        border_bottom="1px solid rgba(255,255,255,0.05)"
                    )
                ),
                width="100%",
                spacing="0"
            ),
            width="100%",
            overflow="auto", # Enable horizontal scroll if columns crowd
        ),
        bg=CARD_BG,
        border_radius="xl",
        border="1px solid #4A5568",
        box_shadow="lg",
    )

def index() -> rx.Component:
    return rx.cond(
        # CONDITIONAL: Show No Data View if dashboard is not started
        ~State.show_dashboard,
        no_data_view(),
        # ELSE: Show Main Dashboard
        rx.flex(
            date_picker_modal(),
            # Sidebar
            sidebar_component(),
            
            # Main Content
            rx.box(
                rx.box(
                    rx.vstack(
                        rx.hstack(
                            rx.button(
                                "☰ Filters", 
                                on_click=State.toggle_sidebar, 
                                color_scheme="gray", 
                                variant="outline",
                                size="2"
                            ),
                            rx.heading(State.dashboard_title, size="6", color=TEXT_COLOR),
                            rx.spacer(),
                            # Removed persistent upload buttons as per user request
                            width="100%",
                        ),
                        # Status feedback for uploads is now shown in the no_data_view or a toast, 
                        # but we can keep a subtle indicator if needed. For now, just removing the buttons.
                        # AI Chat Interface      ),
                        rx.fragment(),

                    
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
                            # bg_color="#48BB78", # REMOVED for dark theme consistency
                            align="center",
                            value_size="9", 
                            title_size="8", 
                            bottom_left=State.total_b2b_sales,
                            bottom_right=State.total_b2c_sales,
                            bottom_left_trend=State.b2b_trend,
                            bottom_right_trend=State.b2c_trend,
                            bottom_left_icon="briefcase", 
                            bottom_right_icon="shopping-cart", 
                            trend_inline=True, 
                        ),
                        rx.grid(
                            card_avg_monthly_sale(),
                            card_daily_velocity(),
                            card_returns_invoices(),
                            card_pareto(),
                            columns={"initial": "1", "sm": "1", "lg": "2", "xl": "2"}, # 2x2 Layout
                            spacing="4",
                            width="100%"
                        ),
                        
                        # Courier Performance Card
                        courier_performance_card(),

                        spacing="4",
                        width="100%",
                    ),
                    
                    rx.box(height="10px"),

                    # Monthly Summary Table
                    rx.box(
                        monthly_summary_table_v2(),
                        width="100%"
                    ),
                    
                    rx.box(height="20px"),

                    # Monthly Sales Return Table
                    rx.box(
                        monthly_sales_return_table(),
                        width="100%"
                    ),

                    rx.box(height="20px"),

                    # Invoice vs Returns Table
                    rx.box(
                        invoice_vs_return_table(),
                        width="100%"
                    ),
                    
                    rx.separator(margin_y="6", color_scheme="gray"),
                    
                    # Charts Row 1
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.heading("Monthly Sales Trend (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                                rx.plotly(data=State.monthly_sales_chart, height="400px"),
                                width="100%",
                                align="center",
                            ),
                            bg="#000000",
                            box_shadow="lg",
                            border="1px solid #4A5568",
                            border_radius="xl",
                            padding="4"
                        ),
                        
                        # Added Channel Wise Sale (Donut Chart)
                        channel_sales_card(),
                        
                        rx.box(
                            rx.vstack(
                                rx.heading("Sales by State Top -10 Distribution (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                                rx.plotly(data=State.state_sales_chart, height="580px"),
                                width="100%",
                                align="center",
                            ),
                            bg="#000000",
                            box_shadow="lg",
                            border="1px solid #4A5568",
                            border_radius="xl",
                            padding="4"
                        ),
                        columns="1",
                        spacing="4",
                        width="100%",
                    ),
                    
                    # Charts Row 2
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.heading("Sales by Product - Top 5 (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),

                                rx.plotly(data=State.product_sales_chart, height="580px"),
                                width="100%",
                                align="center",
                            ),
                            bg="#000000",
                            box_shadow="lg",
                            border="1px solid #4A5568",
                            border_radius="xl",
                            padding="4"
                        ),
                         rx.box(
                            rx.vstack(
                                rx.heading("Sales by Supply Type (Value in Crore)", size="4", color=TEXT_COLOR, width="100%", text_align="center"),
                                rx.plotly(data=State.supply_sales_chart, height="580px"),
                                width="100%",
                                align="center",
                            ),
                            bg="#000000",
                            box_shadow="lg",
                            border="1px solid #4A5568",
                            border_radius="xl",
                            padding="4"
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
                                        rx.table.column_header_cell("Rank", text_align="center", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("Product Name", text_align="center", color="white", font_weight="bold"), # Center align
                                        rx.table.column_header_cell("Sales", text_align="center", color="white", font_weight="bold"), # shortened for space
                                        rx.table.column_header_cell("Contribution (in %)", text_align="center", color="white", font_weight="bold"), # Renamed
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
                                            rx.table.cell(rx.text(row["label"], font_size="xs", weight="medium", color="white", text_shadow="0px 1px 2px black"), text_align="center"), # Center align
                                            rx.table.cell(rx.text(row["formatted_value"], font_family="mono", color="white", font_size="xs", font_weight="bold", text_shadow="0px 1px 2px black"), text_align="center"),
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
                                        rx.table.column_header_cell("Channel", text_align="center", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("Sales", text_align="center", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("Orders", text_align="center", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("AOV", text_align="center", color="white", font_weight="bold"),
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
                                            rx.table.cell(rx.text(row["formatted_sales"], font_family="mono", font_size="xs", color="white"), text_align="center"),
                                            rx.table.cell(rx.text(row["orders"], font_family="mono", font_size="xs", color="white"), text_align="center"),
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
                                        rx.table.column_header_cell("State", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("Top Product", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("Sales", text_align="right", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("% contribution to Sales in the State", text_align="center", color="white", font_weight="bold"),
                                        rx.table.column_header_cell("Total Sale in the State", text_align="center", color="white", font_weight="bold"),
                                    ),
                                    bg="rgba(255,255,255,0.05)"
                                ),
                                rx.table.body(
                                    rx.foreach(
                                        State.state_data,
                                        lambda row: rx.table.row(
                                            rx.table.cell(rx.text(row["state"], font_weight="bold", font_size="xs", color="white")),
                                            rx.table.cell(rx.text(row["product"], font_size="xs", color="white")),
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







                    rx.box(height="40px"), # Bottom padding
                    ), 
                    padding="6",
                    width="100%", # Occupy full width
                    max_width="1300px", # EXACT match for table content (1290px + margins)
                    margin_x="auto", # Center horizontally
                ), 
                bg=CONTENT_BG,
                flex="1",
                height="100vh",
                overflow="auto",
                align_items="center", # Ensure children center
            ),
            spacing="0",
            flex_direction=["column", "row"],
            height="100vh",
            width="100vw",
            on_mount=State.load_data,
        )
    )




app = rx.App(
    theme=rx.theme(
        appearance="dark", 
        has_background=True, 
        radius="large", 
        accent_color="amber", # Gold/Amber accent
        gray_color="slate",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap",
    ],
    style={
        "font_family": "Inter, sans-serif",
        "background_color": "#000000",
    }
)
app.add_page(index, title="Sales Dashboard")
def monthly_summary_table_v2() -> rx.Component:
    MONTH_COL_WIDTH = "110px"

    return rx.box(
        # 1. Main Title Bar
        rx.flex(
            rx.box(
                rx.text(f"Monthly Summary of Gross Sale Value (Channel wise) {State.table_date_range_title}", font_size="md", font_weight="900", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                rx.box(height="12px"), # Gap between title and subtitle
                rx.text("Breakdown by Channel and Top 5 States", font_size="xs", font_weight="bold", color="gray.400", letter_spacing="0.05em", text_align="center", width="100%"),
                rx.box(height="12px"), # Extra spacing
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            bg=CARD_BG,
            border_bottom=f"1px solid {BORDER_COLOR}",
            border_top_left_radius="xl",
            border_top_right_radius="xl",
        ),
        
        # 2. Table Container
        rx.box(
            # HEADER ROW
            rx.flex(
                rx.box(rx.text("CHANNEL / REGION", font_weight="bold", color="gray.400", font_size="9px", letter_spacing="0.1em"), width="240px", min_width="240px", max_width="240px", padding_left="4", padding_y="3", border_right=f"1px solid {BORDER_COLOR}"),
                rx.foreach(
                    State.summary_table_columns,
                    lambda col: rx.flex(
                        rx.text(col, font_weight="bold", color="gray.400", font_size="9px", text_align="center", width="100%", letter_spacing="0.1em"),
                        width=MONTH_COL_WIDTH,
                        min_width=MONTH_COL_WIDTH,
                        max_width=MONTH_COL_WIDTH,
                        flex="none", 
                        padding_y="3", 
                        border_right=f"1px solid {BORDER_COLOR}", 
                        justify="center", 
                        align="center",
                        overflow="hidden"
                    )
                ),
                rx.box(rx.text("TOTAL", font_weight="bold", color="white", font_size="9px", text_align="center", letter_spacing="0.1em"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg="#064E3B"),
                bg="#064E3B",
                width="100%",
                align="center",
                border_bottom=f"1px solid {BORDER_COLOR}",
            ),
            
            # BODY ROWS
            rx.vstack(
                rx.foreach(
                    State.monthly_summary_data,
                    lambda row: rx.box(
                        # Condition: Grand Total Footer vs Data Rows
                        rx.cond(
                            row.is_total,
                             # FOOTER ROW (Grand Total)
                             rx.flex(
                                 rx.box(rx.text(row.channel, font_weight="900", color="white", font_size="sm", letter_spacing="0.05em", text_transform="capitalize"), width="240px", min_width="240px", max_width="240px", padding_left="4", padding_y="3", border_right=f"1px solid {BORDER_COLOR}", overflow="hidden"),
                                rx.foreach(
                                    row.monthly_values,
                                    lambda m, i: rx.flex(
                                        rx.text(m.value, color="white", font_size="9px", font_weight="medium", text_align="center", width="100%"),  
                                        width=MONTH_COL_WIDTH,
                                        min_width=MONTH_COL_WIDTH,
                                        max_width=MONTH_COL_WIDTH,
                                        flex="none", 
                                        padding_y="3", 
                                        border_right=f"1px solid {BORDER_COLOR}", 
                                        bg=rx.cond(i % 2 == 0, "rgba(255,255,255,0.03)", "rgba(255,255,255,0.01)"),
                                        justify="center",
                                        align="center",
                                        overflow="hidden"
                                    )
                                ),
                                    rx.box(rx.text(row.total_value, font_weight="900", color="#22c55e", font_size="sm", text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg="#000000"), # Black for total column
                                bg="#064E3B", # Dark Green for Total ROW
                                width="100%",
                                align="center",
                                border_top=f"1px solid {BORDER_COLOR}",
                            ),
                            # DATA ROW (Channel + Accordion)
                            rx.accordion.root(
                                rx.accordion.item(
                                    rx.accordion.trigger(
                                        rx.flex(
                                            rx.box(
                                                rx.hstack(
                                                    rx.icon("chevron-down", size=16, color="white"),
                                                    rx.text(row.channel, font_weight="bold", color="white", font_size="9px", white_space="nowrap", text_overflow="ellipsis", overflow="hidden", text_transform="capitalize"),
                                                    spacing="2",
                                                    align="center"
                                                ),
                                                width="240px", 
                                                min_width="240px",
                                                max_width="240px",
                                                padding_left="2",
                                                padding_y="3",
                                                border_right=f"1px solid {BORDER_COLOR}",
                                                overflow="hidden"
                                            ), 
                                            rx.foreach(
                                                row.monthly_values,
                                                lambda m, i: rx.flex(
                                                    rx.text(m.value, color="white", font_size="9px", text_align="center", width="100%", white_space="nowrap", text_overflow="ellipsis", overflow="hidden"),  
                                                    width=MONTH_COL_WIDTH,
                                                    min_width=MONTH_COL_WIDTH,
                                                    max_width=MONTH_COL_WIDTH,
                                                    flex="none",
                                                    padding_y="3", 
                                                    border_right=f"1px solid {BORDER_COLOR}", 
                                                    bg=rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.02)"),
                                                    justify="center",
                                                    align="center",
                                                    overflow="hidden"
                                                )
                                            ),
                                                rx.box(rx.text(row.total_value, font_weight="bold", color="white", font_size="9px", text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg="#000000"), 
                                            width="100%",
                                            align="center",
                                            bg="transparent",
                                            _hover={"bg": "rgba(255,255,255,0.03)"}
                                        ),
                                        padding="0",
                                        _hover={"bg": "transparent"},
                                    ),
                                    rx.accordion.content(
                                        rx.vstack(
                                            rx.foreach(
                                                row.children,
                                                lambda child: rx.flex(
                                                    rx.box(
                                                        rx.text(child.state, color="gray.400", font_size="9px", padding_left="8"),  
                                                        width="240px", 
                                                        min_width="240px",
                                                        max_width="240px",
                                                        padding_y="2", 
                                                        border_right=f"1px solid {BORDER_COLOR}",
                                                        overflow="hidden"
                                                    ),
                                                    rx.foreach(
                                                        child.monthly_values,
                                                        lambda m, i: rx.flex(
                                                            rx.text(m.value, color="gray.400", font_size="9px", text_align="center", width="100%", white_space="nowrap", text_overflow="ellipsis", overflow="hidden"),  
                                                            width=MONTH_COL_WIDTH,
                                                            min_width=MONTH_COL_WIDTH,
                                                            max_width=MONTH_COL_WIDTH,
                                                            flex="none", 
                                                            padding_y="2", 
                                                            border_right=f"1px solid {BORDER_COLOR}", 
                                                            bg=rx.cond(i % 2 == 0, "rgba(0,0,0,0.2)", "rgba(0,0,0,0.3)"), 
                                                            justify="center",
                                                            align="center",
                                                            overflow="hidden"
                                                        )
                                                    ),
                                                    rx.box(rx.text(child.total_value, color="gray.400", font_size="9px", text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="2", overflow="hidden", bg="#000000"),
                                                    bg="rgba(0,0,0,0.4)",
                                                    width="100%",
                                                    align="center",
                                                    border_top=f"1px dotted {BORDER_COLOR}",
                                                )
                                            ),
                                            width="100%",
                                            spacing="0",
                                        ),
                                        padding="0",
                                    ),
                                    border_width="0",
                                    padding="0",
                                ),
                                type="multiple",
                                collapsible=True,
                                width="100%",
                                variant="ghost",
                            )
                        ),
                        width="100%",
                        border_bottom=f"1px solid {BORDER_COLOR}",
                        bg="transparent"
                    )
                ),
                width="100%",
                spacing="0"
            ),
            width="100%",
            overflow="auto", 
        ),
        bg="transparent",
        width="100%",
        min_width="1230px", # Corrected width for 240+140+cols
        box_shadow="lg",
    )

def monthly_sales_return_table() -> rx.Component:
    MONTH_COL_WIDTH = "110px"

    return rx.box(
        # 1. Main Title Bar
        rx.flex(
            rx.box(
                rx.text(f"Monthly Sales Return (Channel wise) {State.table_date_range_title}", font_size="md", font_weight="900", color="white", letter_spacing="0.05em", text_align="center", width="100%"),
                width="100%",
            ),
            align="center",
            justify="center",
            padding="4",
            bg=CARD_BG,
            border_bottom=f"1px solid {BORDER_COLOR}",
            border_top_left_radius="xl",
            border_top_right_radius="xl",
        ),
        
        rx.box(
            # HEADER ROW
            rx.flex(
                rx.box(rx.text("CHANNEL", font_weight="bold", color="gray.400", font_size="9px", letter_spacing="0.1em"), width="240px", min_width="240px", max_width="240px", padding_left="4", padding_y="3", border_right="1px solid rgba(255,255,255,0.05)"),
                rx.foreach(
                    State.summary_table_columns,
                    lambda col, i: rx.flex(
                        rx.text(col, font_weight="bold", color="gray.400", font_size="9px", text_align="center", width="100%", letter_spacing="0.1em"),
                        width=MONTH_COL_WIDTH,
                        min_width=MONTH_COL_WIDTH,
                        max_width=MONTH_COL_WIDTH,
                        flex="none", 
                        padding_y="3", 
                        border_right="1px solid rgba(255,255,255,0.05)", 
                        bg=rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.03)"),
                        justify="center", 
                        align="center",
                        overflow="hidden"
                    )
                ),

                rx.box(rx.text("TOTAL", font_weight="bold", color="white", font_size="9px", text_align="center", letter_spacing="0.1em"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg="#064E3B"),
                bg="#064E3B",
                width="100%",
                align="center",
                border_bottom=f"1px solid {BORDER_COLOR}",
            ),
            
            # BODY ROWS
            rx.vstack(
                rx.foreach(
                    State.monthly_sales_return_data,
                    lambda row: rx.box(
                         rx.flex(
                            rx.box(rx.text(row.channel, font_weight="bold", color=rx.cond(row.is_total, "white", "gray.300"), font_size="9px", text_transform="capitalize"), width="240px", min_width="240px", max_width="240px", padding_left="4", padding_y="3", border_right=f"1px solid {BORDER_COLOR}", overflow="hidden"),
                            rx.foreach(
                                row.monthly_values,
                                lambda m, i: rx.flex(
                                    rx.text(m.value, color=rx.cond(row.is_total, "white", "gray.400"), font_size="9px", text_align="center", width="100%", white_space="nowrap", text_overflow="ellipsis", overflow="hidden"),  
                                    width=MONTH_COL_WIDTH,
                                    min_width=MONTH_COL_WIDTH,
                                    max_width=MONTH_COL_WIDTH,
                                    flex="none", 
                                    padding_y="3", 
                                    border_right=f"1px solid {BORDER_COLOR}", 
                                    bg=rx.cond(
                                        row.is_total,
                                        rx.cond(i % 2 == 0, "rgba(255,255,255,0.05)", "rgba(255,255,255,0.02)"),
                                        rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                                    ), 
                                    justify="center",
                                    align="center",
                                    overflow="hidden"
                                )
                            ),
                                rx.box(rx.text(row.total_value, font_weight="bold", color=rx.cond(row.is_total, "#22c55e", "white"), font_size=rx.cond(row.is_total, "sm", "9px"), text_align="center"), width="140px", min_width="140px", max_width="140px", padding_y="3", overflow="hidden", bg=rx.cond(row.is_total, "#000000", "#000000")),
                            bg=rx.cond(row.is_total, "#064E3B", "transparent"),
                            width="100%",
                            align="center",
                            border_top=rx.cond(row.is_total, f"1px solid {BORDER_COLOR}", "none"),
                            border_bottom=f"1px solid {BORDER_COLOR}"
                        )
                    )
                ),
                width="100%",
                spacing="0"
            ),
            width="100%",
            overflow="auto", 
        ),
        bg="#000000",
        width="100%",
        min_width="1230px", # Corrected Width
        border_radius="xl",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="lg",
    )

def invoice_vs_return_table() -> rx.Component:
    COL_WIDTH = "68px" # Smaller cols for Inv/Ret
    MONTH_COL_WIDTH = "150px" 

    return rx.box(
        # 1. Main Title Bar
        rx.flex(
             rx.box(
                rx.hstack(
                     rx.icon("file-text", size=20, color="white"),
                    rx.text(f"Invoice vs Sales Return {State.table_date_range_title}", font_size="md", font_weight="900", color="white", letter_spacing="0.05em", text_align="center"),
                    justify="center",
                    align="center", 
                    spacing="2"
                ),
                width="100%",
             ),
            align="center",
            justify="center",
            padding="4",
            bg=CARD_BG,
            border_bottom=f"1px solid {BORDER_COLOR}",
            border_top_left_radius="xl",
            border_top_right_radius="xl",
        ),
        
        rx.box(
             # COMPLEX HEADER
             rx.flex(
                 # Column 1: Month (Merged Vertically)
                 rx.box(
                     rx.center(
                         rx.text("MONTH", font_weight="bold", color="gray.400", font_size="9px", letter_spacing="0.1em"),
                         height="100%",
                         width="100%"
                     ),
                     width=MONTH_COL_WIDTH, 
                     min_width=MONTH_COL_WIDTH, 
                     border_right=f"1px solid {BORDER_COLOR}", 
                     height="auto", # Fill height of parent flex
                     flex_shrink=0
                 ),
                 
                 # Column Block: Channels + Subheaders
                 rx.vstack(
                     # Row A: Channels 
                     rx.flex(
                         rx.foreach(
                             State.invoice_return_columns,
                             lambda col, i: rx.flex(
                                 rx.text(col, font_weight="bold", color="gray.400", font_size="9px", text_align="center", width="100%", letter_spacing="0.1em", text_transform="capitalize"),
                                 width="136px", 
                                 min_width="136px",
                                 flex="none", 
                                 padding_y="3", 
                                 border_right=f"1px solid {BORDER_COLOR}", 
                                 justify="center", 
                                 align="center",
                                 overflow="hidden"
                             )
                         ),
                         width="fit-content",
                         spacing="0",
                         flex="1"
                     ),
                     
                     # Row B: Inv / Ret Sub-headers
                     rx.flex(
                         rx.foreach(
                             State.invoice_return_columns,
                             lambda col, i: rx.flex(
                                 rx.box(rx.text("Inv", color="gray.400", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                                 rx.box(rx.text("Ret", color="#FA5252", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                                 width="136px",
                                 min_width="136px",
                                 flex="none",
                                 justify="center",
                                 align="center",
                                 overflow="hidden",
                                 spacing="0"
                             )
                         ),
                         width="fit-content",
                         border_top=f"1px solid {BORDER_COLOR}",
                         spacing="0"
                     ),
                     spacing="0",
                     width="fit-content"
                ),
                # Grand Total Column Header
                rx.vstack(
                    rx.flex(
                        rx.text("Grand Total", font_weight="bold", color="gray.400", font_size="9px", text_align="center", width="100%", letter_spacing="0.1em"),
                        width="136px", 
                        min_width="136px",
                        padding_y="3", 
                        border_right=f"1px solid {BORDER_COLOR}", 
                        justify="center", 
                        align="center",
                        overflow="hidden",
                        flex="1"
                    ),
                    rx.flex(
                        rx.box(rx.text("Inv", color="gray.400", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                        rx.box(rx.text("Ret", color="#FA5252", font_size="9px", font_weight="bold", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                        width="136px",
                        min_width="136px",
                        flex="none",
                        justify="center",
                        align="center",
                        overflow="hidden",
                        spacing="0",
                        border_top=f"1px solid {BORDER_COLOR}"
                    ),
                    bg="transparent",
                    width="fit-content",
                    spacing="0"
                ), 
                bg="#064E3B",
                width="fit-content",
                align="stretch"
            ),


             # BODY
            rx.vstack(
                rx.foreach(
                    State.invoice_vs_return_data,
                    lambda row: rx.flex(
                        rx.box(rx.text(row.month, font_weight="bold", color="white", font_size="9px"), width=MONTH_COL_WIDTH, min_width=MONTH_COL_WIDTH, padding_left="4", padding_y="3", border_right=f"1px solid {BORDER_COLOR}", overflow="hidden"),
                        
                        # Check if it has 'channels' list (Normal Rows)
                        rx.cond(
                           row.is_pct,
                            # PCT ROW
                            rx.foreach(
                                row.channels, 
                                lambda chan, i: rx.flex(
                                   rx.text(chan.val, color=chan.color, font_size="9px", font_weight="bold", text_align="center", width="100%"),
                                   width="136px",
                                   min_width="136px",
                                   flex="none",
                                   padding_y="2",
                                   bg=rx.cond(
                                       row.is_total,
                                       rx.cond(i % 2 == 0, "rgba(255,255,255,0.05)", "rgba(255,255,255,0.02)"),
                                       rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                                   ), 
                                   border_right=f"1px solid {BORDER_COLOR}",
                                   justify="center",
                                   align="center"
                               )
                            ),
                            # DATA ROW
                            rx.foreach(
                                row.channels,
                                lambda chan, i: rx.flex(
                                    rx.box(rx.text(chan.inv, color=rx.cond(chan.channel=="Grand Total", "#22c55e", "white"), font_size="9px", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                                    rx.box(rx.text(chan.ret, color="#FA5252", font_size="9px", text_align="center"), width=COL_WIDTH, border_right=f"1px solid {BORDER_COLOR}", padding_y="2"),
                                    width="136px",
                                    min_width="136px",
                                    flex="none",
                                    justify="center",
                                    align="center",
                                    overflow="hidden",
                                    spacing="0",
                                    bg=rx.cond(
                                       row.is_total,
                                       rx.cond(i % 2 == 0, "rgba(255,255,255,0.05)", "rgba(255,255,255,0.02)"),
                                       rx.cond(i % 2 == 0, "transparent", "rgba(255,255,255,0.04)")
                                   )
                                )
                            )
                        ),
                        bg=rx.cond(row.is_total, "#064E3B", "transparent"), # Greenish for total row
                        width="fit-content",
                        border_bottom=f"1px solid {BORDER_COLOR}",
                        align="center"
                    )
                 ),
                 width="fit-content",
                 spacing="0"
             ),
             width="100%",
             overflow="auto", 
        ),
        bg="#000000",
        width="100%",
        min_width="1230px",
        border_radius="xl",
        border=f"1px solid {BORDER_COLOR}",
        box_shadow="lg",
    )

# Channel Sales Card
def channel_sales_card() -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.heading("Channel Wise Sale", size="4", color=TEXT_COLOR, width="100%", text_align="center", margin_bottom="4"), 
            
            rx.flex(
                # Chart
                rx.box(
                    rx.plotly(data=State.channel_sales_chart, height="580px", config={"displayModeBar": False}),
                    width="55%", # Slightly increased width allocation
                    min_width="300px",
                    display="flex",
                    justify_content="center",
                    align_items="center"
                ),
                
                # Custom Legend
                rx.vstack(
                    rx.foreach(
                        State.channel_sales_stats,
                        lambda item: rx.hstack(
                             rx.box(width="10px", height="10px", border_radius="50%", bg=item["color"]),
                             rx.text(item["channel"], color="gray.300", font_size="sm", font_weight="medium"),
                             rx.spacer(),
                             rx.text(item["value"], color="white", font_size="sm", font_weight="bold"),
                             rx.text(item["pct"], color="gray.500", font_size="xs", font_weight="medium"),
                             width="100%",
                             padding_y="1",
                             border_bottom="1px dashed #4A5568",
                             align="center"
                        )
                    ),
                    width="50%",
                    min_width="250px",
                    padding_left="4",
                    spacing="0"
                ),
                
                width="100%",
                flex_wrap="wrap",
                align="center",
                justify="center"
            ),
            width="100%",
        ),
        bg=CARD_BG,
        border_radius="xl",
        box_shadow="lg",
        border="1px solid #4A5568",
        padding="6",
        width="100%",
        height="100%"
    )