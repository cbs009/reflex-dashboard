
import reflex as rx
from .ai import AIState
from .predictive import PredictiveState
from ..utils.ppt_generator import create_presentation

class State(PredictiveState):
    """The main app state that aggregates all other states."""
    
    def export_ppt(self):
        """Generates and downloads the dashboard as a PowerPoint."""
        
        # 1. GATHER KPIS (Expanded list)
        
        # Business Summary KPIs
        kpi_list = [
            {"label": "Total Sales", "value": self.total_sales, "trend": self.total_sales_trend},
            {"label": "Avg Monthly Sale", "value": self.average_monthly_sale, "trend": self.total_sales_trend},
            {"label": "Total Invoices", "value": self.total_invoices, "trend": self.total_invoices_trend},
            {"label": "Active Customers (B2B)", "value": self.total_b2b_sales.split(":")[-1].strip(), "trend": self.b2b_trend},
            {"label": "Daily Sales Velocity", "value": self.daily_sales_velocity_data.get("total", "0"), "trend": ""},
            {"label": "Sales Returns", "value": self.total_sales_return, "trend": f"{self.return_metrics.get('rate_pct', '0%')} Rate"},
        ]
        
        # Pareto KPI (if valid)
        pareto = self.pareto_stats
        kpi_list.append({
            "label": "Top 80% Contribution",
             "value": f"{pareto.get('count_80', '0')} Products",
             "trend": pareto.get("pct_catalog", "")
        })
        
        # Courier KPIs (if data exists)
        cm = self.courier_metrics
        kpi_list.extend([
            {"label": "Courier Avg Cost", "value": cm.get("avg_cost", "0"), "trend": ""},
            {"label": "Courier Avg Time", "value": cm.get("avg_time", "0"), "trend": ""},
            {"label": "Delivery Success Rate", "value": cm.get("success_rate", "0%"), "trend": ""},
            {"label": "Return Rate (RTO)", "value": cm.get("return_rate", "0%"), "trend": ""},
        ])
        
        # 2. GATHER CHARTS (Expanded list)
        charts = {}
        
        # Standard Charts (Overview Tab)
        if self.monthly_sales_chart: charts["Monthly Sales Trend"] = self.monthly_sales_chart
        if self.channel_sales_chart: charts["Channel Sales Distribution"] = self.channel_sales_chart
        if self.product_sales_chart: charts["Product Sales Distribution"] = self.product_sales_chart
        if self.state_sales_chart: charts["Sales by State"] = self.state_sales_chart
        if self.supply_sales_chart: charts["Sales by Supply Type"] = self.supply_sales_chart
        
        # Predictive Charts (Predictive Tab)
        try:
             # Check if data exists for these charts to avoid empty charts
            if self.revenue_growth_chart and getattr(self.revenue_growth_chart, 'data', None):
                charts["AI Revenue Forecast"] = self.revenue_growth_chart
            
            if self.regression_chart and getattr(self.regression_chart, 'data', None):
                charts["Price Elasticity (Regression)"] = self.regression_chart
                
            if self.survival_chart and getattr(self.survival_chart, 'data', None):
                charts["Customer Retention (Survival)"] = self.survival_chart
                
            if self.propensity_chart and getattr(self.propensity_chart, 'data', None):
                 charts["Propensity Scoring"] = self.propensity_chart
                 
            if self.bcg_matrix_chart and getattr(self.bcg_matrix_chart, 'data', None):
                 charts["BCG Matrix (Market Share)"] = self.bcg_matrix_chart
                 
            if self.toxic_sku_chart and getattr(self.toxic_sku_chart, 'data', None):
                 charts["Toxic SKU Analysis"] = self.toxic_sku_chart
                 
            if self.sku_forecast_chart and getattr(self.sku_forecast_chart, 'data', None):
                 charts["SKU Level Forecast"] = self.sku_forecast_chart
                 
            if self.seasonality_chart and getattr(self.seasonality_chart, 'data', None):
                 charts["Seasonality Analysis"] = self.seasonality_chart
                 
        except Exception as e:
            print(f"Error gathering predictive charts: {e}")

        # 3. GATHER TABLES (New)
        tables = {}
        
        # Monthly Summary Table
        # Convert `ChannelSummary` objects to 2D list
        # Columns: Month, Channel 1, Channel 2, ..., Grand Total
        summ_data = self.monthly_summary_data
        if summ_data:
            cols = ["Channel"] + self.summary_table_columns + ["Total"]
            rows = []
            for row_obj in summ_data:
                # Row format: [Channel Name, Val1, Val2 ..., TotalVal]
                r = [row_obj.channel]
                for mv in row_obj.monthly_values:
                    r.append(mv.value)
                r.append(row_obj.total_value)
                rows.append(r)
            tables["Monthly Summary of Gross Sale Value"] = {"columns": cols, "rows": rows}
            
        # Invoice vs Returns Table
        inv_ret_data = self.invoice_vs_return_data
        if inv_ret_data:
            # Dynamic Columns based on channels
            # Row object structure: month, channels list, grand_total_inv/ret
            # This is complex to flatten. Let's simplify for PPT.
            # Table: Month | Channel 1 (Inv/Ret) | ... | Total Inv | Total Ret
            
            # Let's extract channel names from first row
            first_row = inv_ret_data[0]
            channel_names = [c.channel for c in first_row.channels if c.channel != "Grand Total"]
            
            cols = ["Month"]
            for c in channel_names:
                cols.append(f"{c} (Inv/Ret)")
            cols.append("Grand Total Inv")
            cols.append("Grand Total Ret")
            
            rows = []
            for item in inv_ret_data:
                r = [item.month]
                # Map channel data
                ch_map = {c.channel: f"{c.inv}/{c.ret}" for c in item.channels}
                for c_name in channel_names:
                    r.append(ch_map.get(c_name, "-/-"))
                
                # Grand totals exist as properties or in channel list
                # Logic in `tables.py` puts GT in channels list too, but also has explicit fields
                r.append(item.grand_total_inv if hasattr(item, 'grand_total_inv') else "")
                r.append(item.grand_total_ret if hasattr(item, 'grand_total_ret') else "")
                rows.append(r)
                
            tables["Invoice vs Sales Return"] = {"columns": cols, "rows": rows}
            
        # Pareto Top Products Table
        pareto_prods = self.pareto_top_products
        if pareto_prods:
            cols = ["Rank", "Product Name", "Sales (Cr)", "Contribution %"]
            rows = []
            for p in pareto_prods:
                rows.append([p["rank"], p["name"], p["value_cr"], p["pct"]])
            tables["Pareto Top Products"] = {"columns": cols, "rows": rows}

        # 4. Generate PPT
        ppt_io = create_presentation(kpi_data=kpi_list, chart_figures=charts, table_data=tables)
        
        # 5. Return Download Event
        return rx.download(
            data=ppt_io.read(), 
            filename="Enterprise_Intelligence_Report_Full.pptx"
        )
