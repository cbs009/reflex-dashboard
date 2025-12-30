import reflex as rx
import pandas as pd
from typing import Dict, List, Any
from .data import DataState

class KPIState(DataState):
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

    # New KPI Calculations
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
    def return_breakdown(self) -> List[Dict[str, str]]:
        if self.filtered_df.empty:
            return []
            
        # Group by Channel
        # Calculate Return Rate per Channel: (Unique Sales Return / Unique Invoices) * 100
        
        breakdown = []
        channels = self.filtered_df["Channel"].unique()
        
        for ch in channels:
            ch_df = self.filtered_df[self.filtered_df["Channel"] == ch]
            
            # Returns
            returns_df = ch_df[ch_df["DOCUMENT DESCRIPTION"] == "Sales Return"]
            unique_returns = returns_df["BILLING DOCUMENT"].nunique()
            
            # Invoices
            invoices_df = ch_df[ch_df["DOCUMENT DESCRIPTION"] != "Sales Return"]
            total_invoices_count = invoices_df["BILLING DOCUMENT"].nunique()
            
            rate = (unique_returns / total_invoices_count * 100) if total_invoices_count > 0 else 0.0
            
            breakdown.append({
                "channel": ch,
                "formatted_rate": f"{rate:.1f}%",
                "rate": rate
            })
            
        # Sort by rate desc
        breakdown.sort(key=lambda x: x["rate"], reverse=True)
        
        return breakdown

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
    def pareto_top_products(self) -> List[Dict[str, str]]:
        if self.filtered_df.empty:
            return []
            
        sales_df = self.filtered_df[self.filtered_df["Sales Amount"] > 0]
        product_sales = sales_df.groupby("Product")["Sales Amount"].sum().sort_values(ascending=False).reset_index()
        total_sales = product_sales["Sales Amount"].sum()
        
        if total_sales <= 0:
            return []
            
        product_sales["pct"] = product_sales["Sales Amount"] / total_sales * 100
        
        # Take top 5 for display
        top_5 = product_sales.head(5)
        
        result = []
        for i, row in top_5.iterrows():
            val_cr = row["Sales Amount"] / 10000000
            result.append({
                "rank": str(i + 1),
                "name": row["Product"],
                "value_cr": f"₹{val_cr:.2f} Cr",
                "pct": f"{row['pct']:.1f}%"
            })
            
        return result
