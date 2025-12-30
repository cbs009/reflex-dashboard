import reflex as rx
import pandas as pd
import io
from .base import BaseState

class DataState(BaseState):
    """Handles data uploads and processing."""
    
    async def handle_sales_upload(self, files: list[rx.UploadFile]):
        """Handle sales data upload."""
        if not files:
            return

        for file in files:
            try:
                upload_data = await file.read()
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
            temp_df = df.copy()
            temp_df.columns = temp_df.columns.str.upper().str.strip()
            
            column_mapping = {
                "BILLING DATE": "Billing_Date",
                "TOTAL VALUE": "Sales Amount",
                "BRAND DESCRIPTION": "Brand",
                "SKU QTY": "Quantity",
                "CHANNEL": "Channel",
                "PRODUCT": "Product",
                "CUSTOMER STATE": "CUSTOMER STATE",
                "TYPE OF SUPPLY": "TYPE OF SUPPLY",
                "DOCUMENT DESCRIPTION": "DOCUMENT DESCRIPTION",
                "BILLING DOCUMENT": "BILLING DOCUMENT",
            }
            
            if "TOTAL VALUE" not in temp_df.columns and "Sales Amount" not in temp_df.columns:
                 raise ValueError("Invalid Sales File. Missing 'TOTAL VALUE' column.")

            temp_df = temp_df.rename(columns=column_mapping)
            temp_df = temp_df.loc[:, ~temp_df.columns.duplicated()]

            for col in ["Brand", "Channel", "CUSTOMER STATE", "TYPE OF SUPPLY", "Product"]:
                if col in temp_df.columns:
                    temp_df[col] = temp_df[col].astype(str).fillna("").str.strip()
                    if col == "TYPE OF SUPPLY":
                        temp_df[col] = temp_df[col].str.upper().replace({
                            "BUSINESS TO BUSINESS": "B2B",
                            "BUSINESS TO CONSUMER": "B2C",
                            "DIRECT": "B2C",
                            "DEALER": "B2B",
                        })
                    if col == "Channel":
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

            if temp_df["Sales Amount"].dtype == "object":
                temp_df["Sales Amount"] = temp_df["Sales Amount"].astype(str).str.replace(",", "", regex=False)
            temp_df["Sales Amount"] = pd.to_numeric(temp_df["Sales Amount"], errors="coerce").fillna(0)
            
            if temp_df["Quantity"].dtype == "object":
                temp_df["Quantity"] = temp_df["Quantity"].astype(str).str.replace(",", "", regex=False)
            temp_df["Quantity"] = pd.to_numeric(temp_df["Quantity"], errors="coerce").fillna(0)

            if "DISCOUNT AMOUNT" in temp_df.columns:
                if temp_df["DISCOUNT AMOUNT"].dtype == "object":
                    temp_df["DISCOUNT AMOUNT"] = temp_df["DISCOUNT AMOUNT"].astype(str).str.replace(",", "", regex=False)
                temp_df["DISCOUNT AMOUNT"] = pd.to_numeric(temp_df["DISCOUNT AMOUNT"], errors="coerce").fillna(0)

            temp_df["Billing_Date"] = pd.to_datetime(temp_df["Billing_Date"], format="%d-%m-%Y", errors="coerce")
            temp_df["Month_Date"] = temp_df["Billing_Date"].dt.to_period("M").dt.to_timestamp()
            temp_df["Month_Label"] = temp_df["Month_Date"].dt.strftime('%B-%Y')
            
            self.months = sorted([m for m in temp_df['Month_Label'].unique().tolist() if m is not None], key=lambda x: pd.to_datetime(x, format='%B-%Y', errors='coerce'))
            self.states = sorted(temp_df['CUSTOMER STATE'].unique().tolist())
            self.brands = sorted(temp_df['Brand'].unique().tolist())
            self.channels = sorted(temp_df['Channel'].unique().tolist())
            if 'TYPE OF SUPPLY' in temp_df.columns:
                self.supply_types = sorted(temp_df['TYPE OF SUPPLY'].unique().tolist())
            
            self.selected_months = self.months
            self.selected_states = self.states
            self.selected_brands = self.brands
            self.selected_channels = self.channels
            self.selected_supply_types = self.supply_types
            
            if not temp_df["Billing_Date"].isnull().all():
                 min_d = temp_df["Billing_Date"].min()
                 max_d = temp_df["Billing_Date"].max()
                 self.start_date = min_d.strftime("%Y-%m-%d")
                 self.end_date = max_d.strftime("%Y-%m-%d")
            else:
                 self.start_date = ""
                 self.end_date = ""

            # Ensure all expected columns exist to avoid KeyError in computed vars
            expected_cols = [
                "Billing_Date", "Sales Amount", "Brand", "Quantity", "Channel", 
                "Product", "CUSTOMER STATE", "TYPE OF SUPPLY", "DOCUMENT DESCRIPTION", 
                "BILLING DOCUMENT", "Month_Date", "Month_Label"
            ]
            for col in expected_cols:
                if col not in temp_df.columns:
                    if col in ["Sales Amount", "Quantity"]:
                        temp_df[col] = 0.0
                    elif col == "Billing_Date":
                        temp_df[col] = pd.NaT
                    else:
                        temp_df[col] = ""

            self._df = temp_df
            
        except Exception as e:
            print(f"Error processing sales data: {e}")
            self.deployment_status += f" [Data Processing Error: {str(e)}] "

    def process_courier_data(self, df: pd.DataFrame):
        try:
            temp_df = df.copy()
            temp_df.columns = temp_df.columns.str.lower().str.strip()
            required_cols = ["gross_amount", "waybill_num", "status"]
            missing = [col for col in required_cols if col not in temp_df.columns]
            if missing:
                 raise ValueError(f"Invalid Courier File. Missing columns: {missing}")
            self._courier_df = temp_df
        except Exception as e:
            self.deployment_status = f"Error: {str(e)}"

    def close_upload_modal(self):
        self.is_upload_modal_open = False

    def start_analysis(self):
        """Switch to dashboard view."""
        self.is_upload_modal_open = False
        
    def load_data(self):
        """Internal cleanup."""
        pass
