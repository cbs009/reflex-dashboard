
import pandas as pd
import os
import sys

# Mocking State class structure
class MockState:
    def __init__(self):
        self._df = pd.DataFrame()
        self.deployment_status = ""
        self.months = []
        self.states = []
        self.brands = []
        self.channels = []
        self.supply_types = []
        self.selected_months = []
        
    def process_sales_data(self, df: pd.DataFrame):
        print("Starting process_sales_data...")
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
                            if "RCLUB" in v_upper: return "rclub.in"
                            if "BUSINESS CLUB" in v_upper: return "Rajnigandha Business Club" 
                            if "RAJNIGANDHA" in v_upper: return "rajnigandha.com"
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
            
            # --- DEBUGGING DATE ---
            print("Billing Date Sample:")
            print(temp_df["Billing_Date"].head())
            
            temp_df["Month_Date"] = temp_df["Billing_Date"].dt.to_period("M").dt.to_timestamp()
            temp_df["Month_Label"] = temp_df["Month_Date"].dt.strftime('%B-%Y')
            
            print("Month Label Sample:")
            print(temp_df["Month_Label"].head())

            # Populate Filter Options
            self.months = sorted([m for m in temp_df['Month_Label'].unique().tolist() if m is not None], key=lambda x: pd.to_datetime(x, format='%B-%Y', errors='coerce'))
            self.states = sorted(temp_df['CUSTOMER STATE'].unique().tolist())
            self.brands = sorted(temp_df['Brand'].unique().tolist())
            self.channels = sorted(temp_df['Channel'].unique().tolist())
            if 'TYPE OF SUPPLY' in temp_df.columns:
                self.supply_types = sorted(temp_df['TYPE OF SUPPLY'].unique().tolist())
            
            # Default Selections (All)
            self.selected_months = self.months
            
            print("Finished processing. Selected months:", self.selected_months)

            # ATOMIC UPDATE
            self._df = temp_df
            print("Self df updated. Shape:", self._df.shape)
            
        except Exception as e:
            print(f"Error processing sales data: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    file_path = "assets/Uoload_ecom_sale.xlsx"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    print(f"Reading {file_path}")
    df = pd.read_excel(file_path)
    
    state = MockState()
    state.process_sales_data(df)
