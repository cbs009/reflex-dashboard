import reflex as rx
import pandas as pd
import io
from typing import List
from .filters import FilterState
from .store import DataStore

class DataState(FilterState):
    # Load data
    async def handle_sales_upload(self, files: List[rx.UploadFile]):
        """Handle sales data upload."""
        if not files:
            return

        for file in files:
            try:
                upload_data = await file.read()
                
                # Save to a temporary file or read directly if pandas supports bytes (it does for read_excel with engine openpyxl usually, or BytesIO)
                # For simplicity and robustness with read_excel, let's wrap in BytesIO
                df = pd.read_excel(io.BytesIO(upload_data))
                
                if self.process_sales_data(df):
                    self.sales_data_uploaded = True
                    
                    if self.courier_data_uploaded:
                        self.deployment_status = "All Files Uploaded Successfully"
                    else:
                        self.deployment_status = "Sales Data Uploaded Successfully"
                    
            except Exception as e:
                print(f"Error processing sales upload: {e}")
                self.deployment_status = f"Error: {str(e)}"

    async def handle_courier_upload(self, files: List[rx.UploadFile]):
        """Handle courier data upload."""
        if not files:
             return

        for file in files:
            try:
                upload_data = await file.read()
                df = pd.read_excel(io.BytesIO(upload_data))
                if self.process_courier_data(df):
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
            # 1. Check if it's actually a Courier file (contains 'waybill_num')
            if "waybill_num" in temp_df.columns.str.lower():
                 print("Warning: Courier file detected in Sales upload.")
                 self.deployment_status = "⚠️ Warning: You uploaded the Courier file to the Sales slot. Please upload the Sales file."
                 return False

            # 2. We expect at least TOTAL VALUE or Sales Amount
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
                    
                    # Convert to category to reduce serialization size
                    temp_df[col] = temp_df[col].astype("category")

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
            temp_df["Month_Label"] = temp_df["Month_Date"].dt.strftime('%B-%Y').astype("category")
            
            # Populate Filter Options
            # NOTE: We assume self.months etc are available via mixin inheritance in the final State class
            self.months = sorted([m for m in temp_df['Month_Label'].unique().tolist() if m is not None], key=lambda x: pd.to_datetime(x, format='%B-%Y', errors='coerce'))
            self.states = sorted(temp_df['CUSTOMER STATE'].unique().tolist())
            self.brands = sorted(temp_df['Brand'].unique().tolist())
            self.channels = sorted(temp_df['Channel'].unique().tolist())
            if 'TYPE OF SUPPLY' in temp_df.columns:
                self.supply_types = sorted(temp_df['TYPE OF SUPPLY'].unique().tolist())
            
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
                 self.min_date = self.start_date
                 self.max_date = self.end_date
            else:
                 self.start_date = ""
                 self.end_date = ""
                 self.min_date = ""
                 self.max_date = ""

            # ATOMIC UPDATE using DataStore
            try:
                # Use router.session.session_id to get the unique session ID
                token = self.router.session.session_id
                DataStore.set_sales_data(token, temp_df)
                print(f"Data successfully stored for session: {token}")
            except Exception as e:
                print(f"DEBUG: Failed to store data (missing token?): {e}")
                print(f"DEBUG: Failed to store data (missing token?): {e}")
                # If we can't store the data, we can't really proceed with the dashboard
                return False
            
            return True
            
        except Exception as e:
            print(f"Error processing sales data: {e}")
            self.deployment_status += f" [Data Processing Error: {str(e)}] "
            return False

    def process_courier_data(self, df: pd.DataFrame):
        try:
            temp_df = df.copy()
            # Normalize columns to lowercase to ensure 'gross_amount' etc match
            temp_df.columns = temp_df.columns.str.lower().str.strip()
            
            print(f"DEBUG: Original Courier Columns: {temp_df.columns.tolist()}")

            # --- COLUMN MAPPING LOGIC ---
            # Map various possible column names to our standard internal names
            column_map = {
                # Standard Target : [Possible Variations]
                "gross_amount": ["total amount", "cod amount", "bill value", "invoice value", "declared value"],
                "waybill_num": ["waybill no", "awb", "awb no", "docket no", "tracking number"],
                "status": ["current status", "delivery status", "shipment status"],
                "pickup_date": ["pickup date", "manifest date", "booking date"],
                "fpd": ["edd", "promised delivery date", "expected date"],
                "brand": ["client", "client name", "sender", "shipper"]
            }

            rename_dict = {}
            for standard, variations in column_map.items():
                # If standard name already exists, skip
                if standard in temp_df.columns:
                    continue
                # Check variations
                for var in variations:
                    if var in temp_df.columns:
                        rename_dict[var] = standard
                        break # Found a match, stop looking for this standard col
            
            if rename_dict:
                print(f"DEBUG: Renaming columns: {rename_dict}")
                temp_df = temp_df.rename(columns=rename_dict)

            # VALIDATION: Check for expected courier columns
            
            # 1. Check if it's actually a Sales file
            if "TOTAL VALUE" in [c.upper() for c in temp_df.columns] or "SALES AMOUNT" in [c.upper() for c in temp_df.columns]:
                 print("Warning: Sales file detected in Courier upload.")
                 self.deployment_status = "⚠️ Warning: You uploaded the Sales file to the Courier slot. Please upload the Courier file."
                 return False

            # Based on courier_metrics usage: gross_amount, waybill_num, fpd, pickup_date, status
            # We relax the strictness slightly but warn
            required_cols = ["gross_amount", "waybill_num", "status"]
            missing = [col for col in required_cols if col not in temp_df.columns]
            
            if missing:
                 print(f"ERROR: Missing Courier Columns: {missing}")
                 # Try to provide a more helpful error
                 raise ValueError(f"Invalid Courier File. Missing columns: {missing}. Found: {temp_df.columns.tolist()}")
            
            # If brand/client column exists, filter for Rajnigandha.com if requested
            # The user asked for "Coureir Performance(Only for Rajnigandha.com)"
            # We check if there's a column that might indicate this.
            if "brand" in temp_df.columns:
                # normalize content
                counts_before = len(temp_df)
                temp_df["brand"] = temp_df["brand"].astype(str).str.lower()
                # flexible matching
                mask = temp_df["brand"].str.contains("rajnigandha", na=False)
                if mask.any():
                    temp_df = temp_df[mask]
                    print(f"DEBUG: Filtered for Rajnigandha. Rows {counts_before} -> {len(temp_df)}")
                else:
                    print("DEBUG: Brand column found but 'rajnigandha' not found. using all data.")
            
            # Ensure numeric types
            if "gross_amount" in temp_df.columns:
                temp_df["gross_amount"] = pd.to_numeric(temp_df["gross_amount"], errors='coerce').fillna(0)

            try:
                # Use router.session.session_id
                token = self.router.session.session_id
                DataStore.set_courier_data(token, temp_df)
                print(f"Courier Data successfully stored for session: {token}. Columns: {temp_df.columns.tolist()}")
            except Exception as e:
                print(f"DEBUG: Failed to store courier data (missing token?): {e}")
                return False
            print(f"DEBUG: Courier Data Processed. Shape: {temp_df.shape}")
            return True
        except Exception as e:
            print(f"DEBUG: Error processing courier data: {str(e)}")
            self.deployment_status = f"Error: {str(e)}"
            return False

    # --- New Tabbed Workflow State ---
    show_dashboard: bool = False
    
    def start_analysis(self):
        """Switch to dashboard view."""
        if not self.sales_data_uploaded:
             self.deployment_status = "Please upload Sales Data before launching."
             return
        self.show_dashboard = True

    # Intro Page State
    show_intro: bool = True

    def dismiss_intro(self):
        """Dismiss the intro page and show the main dashboard."""
        self.show_intro = False

    @property
    def filtered_df(self) -> pd.DataFrame:
        try:
            token = self.get_token()
            df_source = DataStore.get_sales_data(token)
        except AttributeError:
            # During initial compilation/static analysis, get_token might not be available
            return pd.DataFrame()
        
        if df_source is None or df_source.empty:
            return pd.DataFrame()
        
        # Apply Filters
        # Ensure Billing_Date is datetime for comparison
        # We rely on Billing_Date being correctly set in process_sales_data
        
        mask = (
            (df_source['CUSTOMER STATE'].isin(self.selected_states)) &
            (df_source['Brand'].isin(self.selected_brands)) &
            (df_source['Channel'].isin(self.selected_channels))
        )
        
        if self.start_date and self.end_date:
             mask = mask & (df_source['Billing_Date'] >= self.start_date) & (df_source['Billing_Date'] <= self.end_date)
             
        df = df_source[mask]
        
        if self.selected_supply_types and 'TYPE OF SUPPLY' in df.columns:
             df = df[df['TYPE OF SUPPLY'].isin(self.selected_supply_types)]
             
        return df

    @property
    def courier_df(self) -> pd.DataFrame:
        try:
            token = self.get_token()
            df = DataStore.get_courier_data(token)
            if df is None: return pd.DataFrame()
            return df
        except AttributeError:
            return pd.DataFrame()

    def load_data(self):
        """Check if data exists in memory on load, otherwise reset state to force re-upload."""
        token = self.get_token()
        dfs = DataStore.get_sales_data(token)
        
        if dfs is None or dfs.empty:
            if self.sales_data_uploaded:
                print(f"DEBUG: Data missing for session {token} but State thinks uploaded. Resetting.")
                self.sales_data_uploaded = False
                self.courier_data_uploaded = False
                self.show_dashboard = False
                self.deployment_status = "Session expired or server restarted. Please re-upload data."
