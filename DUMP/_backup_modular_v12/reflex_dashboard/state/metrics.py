import reflex as rx
import pandas as pd
import datetime
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Any
from .data import DataState
from ..constants import CHART_COLORS, TEXT_COLOR, BORDER_COLOR, CARD_BG, ACCENT_BLUE
from ..models import MonthlyValue, StateSummary, ChannelSummary, InvRetChannel, InvRetRow

class MetricsState(DataState):
    """Analytics computed vars (KPIs, table data, charts)."""
    current_tab: str = "business-summary"

    def set_tab(self, tab: str):
        self.current_tab = tab


    @rx.var
    def show_dashboard(self) -> bool:
        return not self._df.empty

    @rx.var
    def dashboard_title(self) -> str:
        base_title = "📊 Interactive Sales Dashboard"
        if self._df.empty:
            return base_title
        try:
             df = self._df.copy()
             if not pd.api.types.is_datetime64_any_dtype(df["Billing_Date"]):
                 df["Billing_Date"] = pd.to_datetime(df["Billing_Date"], errors="coerce")
             min_date = df["Billing_Date"].min()
             max_date = df["Billing_Date"].max()
             if pd.isnull(min_date) or pd.isnull(max_date):
                 return base_title
             return f"{base_title} ({min_date.strftime('%B\'%y')} - {max_date.strftime('%B\'%y')})"
        except:
            return base_title

    @rx.var
    def courier_metrics(self) -> dict:
        if self._courier_df.empty:
            return {"avg_cost": "₹0.0", "avg_time": "0.0 days", "success_rate": "0.0%", "return_rate": "0.0%"}
        df = self._courier_df.copy()
        total_gross = df["gross_amount"].sum()
        total_waybills = df["waybill_num"].nunique()
        avg_cost = total_gross / total_waybills if total_waybills > 0 else 0
        time_df = df.dropna(subset=["fpd", "pickup_date"]).copy()
        avg_time = 0
        if not time_df.empty:
            time_df["pickup_date"] = pd.to_datetime(time_df["pickup_date"])
            time_df["fpd"] = pd.to_datetime(time_df["fpd"])
            avg_time = ((time_df["fpd"] - time_df["pickup_date"]).dt.total_seconds() / (24 * 3600)).mean()
        success_rate = (len(df[df["status"] == "Delivered"]) / len(df) * 100) if len(df) > 0 else 0
        return_rate = (len(df[df["status"] == "RTO"]) / len(df) * 100) if len(df) > 0 else 0
        return {
            "avg_cost": f"₹{avg_cost:.1f}", "avg_time": f"{avg_time:.1f} days",
            "success_rate": f"{success_rate:.1f}%", "return_rate": f"{return_rate:.1f}%"
        }

    @rx.var
    def filtered_df(self) -> pd.DataFrame:
        expected_cols = [
            "Billing_Date", "Sales Amount", "Brand", "Quantity", "Channel", 
            "Product", "CUSTOMER STATE", "TYPE OF SUPPLY", "DOCUMENT DESCRIPTION", 
            "BILLING DOCUMENT", "Month_Date", "Month_Label"
        ]
        if self._df.empty: 
            return pd.DataFrame(columns=expected_cols)
            
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
             
        # Guard against case where mask or supply filter leaves it empty but missing columns
        for col in expected_cols:
            if col not in df.columns:
                df[col] = pd.Series(dtype='object')
                
        return df

    @rx.var
    def total_sales(self) -> str:
        if self.filtered_df.empty: return "₹0.00 Cr"
        return f"₹{self.filtered_df['Sales Amount'].sum() / 10000000:,.2f} Cr"

    @rx.var
    def total_invoices(self) -> str:
        if self.filtered_df.empty: return "0"
        return f"{self.filtered_df['BILLING DOCUMENT'].nunique():,}"

    @rx.var
    def total_sales_return(self) -> str:
        if self.filtered_df.empty: return "₹0.00 Cr"
        ret_df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]
        return f"₹{abs(ret_df['Sales Amount'].sum()) / 10000000:,.2f} Cr"

    @rx.var
    def average_monthly_sale(self) -> str:
        if self.filtered_df.empty: return "₹0.00 Cr"
        unique_months = self.filtered_df["Month_Label"].nunique()
        if unique_months == 0: return "₹0.00 Cr"
        return f"₹{(self.filtered_df['Sales Amount'].sum() / 10000000) / unique_months:,.2f} Cr"

    def calculate_mom(self, df, col="Sales Amount") -> str:
        if df.empty or "Month_Date" not in df.columns: return ""
        monthly_data = df.groupby("Month_Date")[col].sum().sort_index()
        if len(monthly_data) < 2: return ""
        curr, prev = monthly_data.iloc[-1], monthly_data.iloc[-2]
        if prev == 0: return "↑ 100% MoM"
        growth = ((curr - prev) / prev) * 100
        return f"{'↑' if growth >= 0 else '↓'} {abs(growth):.1f}% MoM"

    @rx.var
    def total_sales_trend(self) -> str: return self.calculate_mom(self.filtered_df)

    @rx.var
    def b2b_trend(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return ""
        return self.calculate_mom(self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"])

    @rx.var
    def b2c_trend(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return ""
        return self.calculate_mom(self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"])

    @rx.var
    def average_monthly_sale_trend(self) -> str: return self.total_sales_trend

    @rx.var
    def total_invoices_trend(self) -> str:
        if self.filtered_df.empty: return ""
        monthly_inv = self.filtered_df.groupby("Month_Date")["BILLING DOCUMENT"].nunique().sort_index()
        if len(monthly_inv) < 2: return ""
        curr, prev = monthly_inv.iloc[-1], monthly_inv.iloc[-2]
        if prev == 0: return "↑ 100% MoM"
        growth = ((curr - prev) / prev) * 100
        return f"{'↑' if growth >= 0 else '↓'} {abs(growth):.1f}% MoM"

    @rx.var
    def total_sales_return_trend(self) -> str:
        ret_df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]
        return self.calculate_mom(ret_df)

    @rx.var
    def total_b2b_sales(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return "B2B: ₹0.00 Cr"
        val = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]["Sales Amount"].sum() / 10000000
        return f"B2B: ₹{val:,.2f} Cr"

    @rx.var
    def total_b2c_sales(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return "B2C: ₹0.00 Cr"
        val = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]["Sales Amount"].sum() / 10000000
        return f"B2C: ₹{val:,.2f} Cr"

    @rx.var
    def avg_monthly_b2b(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return "₹0.00 Cr"
        b2b_df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]
        unique_months = b2b_df["Month_Label"].nunique()
        if unique_months == 0: return "₹0.00 Cr"
        return f"₹{(b2b_df['Sales Amount'].sum() / 10000000) / unique_months:,.2f} Cr"

    @rx.var
    def avg_monthly_b2c(self) -> str:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns: return "₹0.00 Cr"
        b2c_df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        unique_months = b2c_df["Month_Label"].nunique()
        if unique_months == 0: return "₹0.00 Cr"
        return f"₹{(b2c_df['Sales Amount'].sum() / 10000000) / unique_months:,.2f} Cr"

    @rx.var
    def product_data(self) -> list[dict]:
        if self.filtered_df.empty: return []
        df = self.filtered_df.copy()
        if "Product" not in df.columns: return []
        total_rev = df["Sales Amount"].sum()
        grp = df.groupby("Product")["Sales Amount"].sum().reset_index().sort_values("Sales Amount", ascending=False)
        top_10 = grp.head(10).to_dict("records")
        results = []
        for i, r in enumerate(top_10):
            val = r["Sales Amount"]
            pct = (val / total_rev * 100) if total_rev else 0
            results.append({
                "rank": str(i+1), "label": str(r["Product"]), "formatted_value": f"₹{val / 10000000:.2f} Cr",
                "formatted_pct": f"{pct:.1f}%", "rank_bg": CHART_COLORS[i % len(CHART_COLORS)],
                "row_bg": "rgba(255,255,255,0.03)" if i % 2 == 0 else "transparent",
            })
        others_val = grp.iloc[10:]["Sales Amount"].sum() if len(grp) > 10 else 0
        if others_val > 0:
            results.append({"rank": "-", "label": "Other Products", "formatted_value": f"₹{others_val / 10000000:.2f} Cr",
                            "formatted_pct": f"{(others_val / total_rev * 100) if total_rev else 0:.1f}%", "rank_bg": "#718096", "row_bg": "transparent"})
        return results

    @rx.var
    def b2c_data(self) -> list[dict]:
        if self.filtered_df.empty: return []
        df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        if df.empty: return []
        stats = df.groupby("Channel").agg(sales=("Sales Amount", "sum"), orders=("BILLING DOCUMENT", "nunique")).reset_index()
        stats["aov"] = stats.apply(lambda x: x["sales"] / x["orders"] if x["orders"] > 0 else 0, axis=1)
        stats = stats.sort_values("aov", ascending=False)
        return [{"channel": str(r["Channel"]), "formatted_sales": f"₹{r['sales'] / 10000000:.2f} Cr", "orders": f"{r['orders']:,.0f}", "formatted_aov": f"₹{r['aov']:,.0f}", "channel_color": CHART_COLORS[i % len(CHART_COLORS)]} for i, r in enumerate(stats.to_dict("records"))]

    @rx.var
    def state_data(self) -> list[dict]:
        if self.filtered_df.empty: return []
        df = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]
        if df.empty: return []
        state_prod = df.groupby(["CUSTOMER STATE", "Product"])["Sales Amount"].sum().reset_index()
        top_per_state = state_prod.sort_values("Sales Amount", ascending=False).drop_duplicates(["CUSTOMER STATE"])
        state_totals = df.groupby("CUSTOMER STATE")["Sales Amount"].sum().to_dict()
        return [{"state": str(r["CUSTOMER STATE"]), "product": str(r["Product"]), "formatted_sales": f"₹{r['Sales Amount'] / 100000:.2f} L", "formatted_pct": f"{(r['Sales Amount'] / state_totals.get(r['CUSTOMER STATE'], 1) * 100):.1f}%", "formatted_total_sales": f"₹{state_totals.get(r['CUSTOMER STATE'], 0) / 100000:.2f} L"} for r in top_per_state.to_dict("records")]

    @rx.var
    def daily_sales_velocity_data(self) -> Dict[str, str]:
        if self.filtered_df.empty: return {"total": "₹0 L", "b2b": "₹0 L", "b2c": "₹0 L"}
        total = self.filtered_df["Sales Amount"].sum()
        days = self.filtered_df["Billing_Date"].nunique()
        if days == 0: return {"total": "₹0 L", "b2b": "₹0 L", "b2c": "₹0 L"}
        b2b = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2B"]["Sales Amount"].sum() if "TYPE OF SUPPLY" in self.filtered_df.columns else 0
        b2c = self.filtered_df[self.filtered_df["TYPE OF SUPPLY"] == "B2C"]["Sales Amount"].sum() if "TYPE OF SUPPLY" in self.filtered_df.columns else 0
        return {"total": f"₹{total/days/100000:,.2f} L", "b2b": f"₹{b2b/days/100000:,.2f} L", "b2c": f"₹{b2c/days/100000:,.2f} L"}

    @rx.var
    def daily_velocity(self) -> str:
        return self.daily_sales_velocity_data["total"]

    @rx.var
    def invoice_stats(self) -> dict:
        if self.filtered_df.empty: return {"count": "0", "daily_avg": "0", "b2b_inv": "0", "b2c_inv": "0", "b2b_val": "₹0.00 Cr", "b2c_val": "₹0.00 Cr"}
        df = self.filtered_df
        total_inv = df["BILLING DOCUMENT"].nunique()
        days = df["Billing_Date"].nunique()
        b2b = df[df["TYPE OF SUPPLY"] == "B2B"]
        b2c = df[df["TYPE OF SUPPLY"] == "B2C"]
        return {
            "count": f"{total_inv:,}",
            "daily_avg": f"{total_inv/days:,.1f}" if days > 0 else "0",
            "b2b_inv": f"{b2b['BILLING DOCUMENT'].nunique():,}",
            "b2c_inv": f"{b2c['BILLING DOCUMENT'].nunique():,}",
            "b2b_val": f"₹{b2b['Sales Amount'].sum()/10000000:,.2f} Cr",
            "b2c_val": f"₹{b2c['Sales Amount'].sum()/10000000:,.2f} Cr"
        }

    @rx.var
    def return_metrics(self) -> dict:
        if self.filtered_df.empty: return {"count": "0", "rate_pct": "0.0%", "val_cr": "₹0.00 Cr"}
        df = self.filtered_df
        ret_df = df[df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]
        total_ret = ret_df["BILLING DOCUMENT"].nunique()
        total_inv = df["BILLING DOCUMENT"].nunique()
        rate = (total_ret / total_inv * 100) if total_inv > 0 else 0
        val = abs(ret_df["Sales Amount"].sum()) / 10000000
        return {"count": str(total_ret), "rate_pct": f"{rate:.1f}%", "val_cr": f"₹{val:,.2f} Cr"}

    @rx.var
    def return_breakdown(self) -> list[dict]:
        if self.filtered_df.empty: return []
        df = self.filtered_df
        results = []
        for channel in df["Channel"].unique():
            ch_df = df[df["Channel"] == channel]
            total_inv = ch_df["BILLING DOCUMENT"].nunique()
            ret_inv = ch_df[ch_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
            rate = (ret_inv / total_inv * 100) if total_inv > 0 else 0
            results.append({"channel": str(channel), "formatted_rate": f"{rate:.1f}%"})
        return results

    @rx.var
    def pareto_stats(self) -> Dict[str, Any]:
        if self.filtered_df.empty: return {"count_80": 0, "pct_catalog": "0.0%"}
        sales_df = self.filtered_df[self.filtered_df["Sales Amount"] > 0]
        grp = sales_df.groupby("Product")["Sales Amount"].sum().sort_values(ascending=False).reset_index()
        total = grp["Sales Amount"].sum()
        if total <= 0: return {"count_80": 0, "pct_catalog": "0.0%"}
        grp["cumulative_pct"] = grp["Sales Amount"].cumsum() / total
        count_80 = (grp["cumulative_pct"] <= 0.80).sum() + 1
        return {"count_80": str(count_80), "pct_catalog": f"({(count_80 / len(grp) * 100):.1f}% of catalog)"}

    @rx.var
    def pareto_top_products(self) -> list[dict]:
        if self.filtered_df.empty: return []
        sales_df = self.filtered_df[self.filtered_df["Sales Amount"] > 0]
        grp = sales_df.groupby("Product")["Sales Amount"].sum().sort_values(ascending=False).reset_index()
        total = grp["Sales Amount"].sum()
        if total <= 0: return []
        results = []
        for i, r in enumerate(grp.head(5).to_dict("records")):
            val = r["Sales Amount"]
            results.append({
                "rank": str(i+1), "name": str(r["Product"]), "value_cr": f"₹{val/10000000:,.2f} Cr", "pct": f"{(val/total*100):.1f}%"
            })
        return results

    @rx.var
    def summary_table_columns(self) -> list[str]:
        if self.filtered_df.empty: return []
        months = sorted(self.filtered_df["Month_Date"].unique())
        return [pd.Timestamp(m).strftime('%b') for m in months]

    @rx.var
    def monthly_summary_data(self) -> list[ChannelSummary]:
        if self.filtered_df.empty: return []
        df = self.filtered_df.copy()
        months = sorted(df["Month_Date"].unique())
        def fmt(val): return f"₹{val/10000000:.2f} Cr"
        res = []
        gt_sums = {m: 0.0 for m in months}
        for channel in df["Channel"].unique():
            ch_df = df[df["Channel"] == channel]
            ch_grp = ch_df.groupby("Month_Date")["Sales Amount"].sum()
            ch_vals = [MonthlyValue(month=pd.Timestamp(m).strftime('%b'), value=fmt(ch_grp.get(m, 0.0)), is_shaded=(i % 2 == 0)) for i, m in enumerate(months)]
            for m in months: gt_sums[m] += ch_grp.get(m, 0.0)
            st_grp = ch_df.groupby("CUSTOMER STATE")["Sales Amount"].sum().sort_values(ascending=False)
            children = [StateSummary(state=str(s), total_value=fmt(v), monthly_values=[MonthlyValue(month=pd.Timestamp(m).strftime('%b'), value=fmt(ch_df[ch_df["CUSTOMER STATE"] == s].groupby("Month_Date")["Sales Amount"].sum().get(m, 0.0)), is_shaded=(i % 2 == 0)) for i, m in enumerate(months)]) for s, v in st_grp.head(5).items()]
            res.append(ChannelSummary(channel=str(channel), monthly_values=ch_vals, total_value=fmt(ch_df["Sales Amount"].sum()), children=children))
        res.append(ChannelSummary(channel="Grand Total", monthly_values=[MonthlyValue(month=pd.Timestamp(m).strftime('%b'), value=fmt(gt_sums[m]), is_shaded=(i % 2 == 0)) for i, m in enumerate(months)], total_value=fmt(sum(gt_sums.values())), is_total=True))
        return res

    @rx.var
    def monthly_sales_return_data(self) -> list[ChannelSummary]:
        if self.filtered_df.empty: return []
        df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)].copy()
        if df.empty: return []
        months = sorted(self.filtered_df["Month_Date"].unique())
        def fmt(val): return f"₹{abs(val)/10000000:.2f} Cr"
        res = []
        gt_sums = {m: 0.0 for m in months}
        for channel in self.filtered_df["Channel"].unique():
            ch_df = df[df["Channel"] == channel]
            ch_grp = ch_df.groupby("Month_Date")["Sales Amount"].sum()
            ch_vals = [MonthlyValue(month=pd.Timestamp(m).strftime('%b'), value=fmt(ch_grp.get(m, 0.0)), is_shaded=(i % 2 == 0)) for i, m in enumerate(months)]
            for m in months: gt_sums[m] += ch_grp.get(m, 0.0)
            res.append(ChannelSummary(channel=str(channel), monthly_values=ch_vals, total_value=fmt(ch_df["Sales Amount"].sum())))
        res.append(ChannelSummary(channel="Grand Total", monthly_values=[MonthlyValue(month=pd.Timestamp(m).strftime('%b'), value=fmt(gt_sums[m]), is_shaded=(i % 2 == 0)) for i, m in enumerate(months)], total_value=fmt(sum(gt_sums.values())), is_total=True))
        return res

    @rx.var
    def invoice_return_columns(self) -> list[str]:
        if self.filtered_df.empty: return []
        return sorted(self.filtered_df["Channel"].unique())

    @rx.var
    def invoice_vs_return_data(self) -> list[InvRetRow]:
        if self.filtered_df.empty: return []
        df = self.filtered_df.copy()
        months = sorted(df["Month_Date"].unique())
        channels = self.invoice_return_columns
        res = []
        for i, m in enumerate(months):
            m_df = df[df["Month_Date"] == m]
            row_chans = []
            for ch in channels:
                c_df = m_df[m_df["Channel"] == ch]
                inv = c_df[~c_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
                ret = c_df[c_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
                row_chans.append(InvRetChannel(channel=ch, inv=str(inv), ret=str(ret), ret_color="#D0312D" if ret > 0 else "gray.500"))
            res.append(InvRetRow(month=pd.Timestamp(m).strftime('%b-%y'), channels=row_chans, grand_total_inv=str(m_df["BILLING DOCUMENT"].nunique())))
            
        # Add Grand Total Row
        total_chans = []
        for ch in channels:
            c_df = df[df["Channel"] == ch]
            inv = c_df[~c_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
            ret = c_df[c_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
            total_chans.append(InvRetChannel(channel=ch, inv=str(inv), ret=str(ret), ret_color="#D0312D" if ret > 0 else "gray.500"))
        res.append(InvRetRow(month="Total", channels=total_chans, grand_total_inv=str(df["BILLING DOCUMENT"].nunique()), is_total=True))
        
        # Add Pct Row
        pct_chans = []
        for ch in channels:
            c_df = df[df["Channel"] == ch]
            inv = c_df[~c_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
            ret = c_df[c_df["DOCUMENT DESCRIPTION"].str.contains("Sales Return", case=False, na=False)]["BILLING DOCUMENT"].nunique()
            rate = (ret / inv * 100) if inv > 0 else 0
            pct_chans.append(InvRetChannel(channel=ch, val=f"{rate:.1f}%", color="#D0312D" if rate > 5 else "gray.400"))
        res.append(InvRetRow(month="Return %", channels=pct_chans, is_pct=True, is_total=True))
        
        return res

    @rx.var
    def channel_sales_stats(self) -> list[dict]:
        if self.filtered_df.empty: return []
        df = self.filtered_df.groupby("Channel")["Sales Amount"].sum().reset_index().sort_values("Sales Amount", ascending=False)
        total = df["Sales Amount"].sum()
        return [{"channel": str(r["Channel"]), "value": f"₹{r['Sales Amount']/10000000:.2f} Cr", "pct": f"{(r['Sales Amount']/total*100):.1f}%", "color": CHART_COLORS[i % len(CHART_COLORS)]} for i, r in enumerate(df.to_dict("records"))]

    @rx.var
    def table_date_range_title(self) -> str:
        if self._df.empty: return ""
        try:
             df = self._df.copy()
             if not pd.api.types.is_datetime64_any_dtype(df["Billing_Date"]):
                 df["Billing_Date"] = pd.to_datetime(df["Billing_Date"], errors="coerce")
             min_date = df["Billing_Date"].min()
             max_date = df["Billing_Date"].max()
             if pd.isnull(min_date) or pd.isnull(max_date):
                 return ""
             return f"({min_date.strftime('%B\'%y')} - {max_date.strftime('%B\'%y')})"
        except:
            return ""

    @rx.var
    def monthly_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        data = self.filtered_df.groupby("Month_Date")["Sales Amount"].sum().reset_index()
        data["Month"] = data["Month_Date"].dt.strftime('%b-%Y')
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        fig = go.Figure(go.Scatter(x=data["Month"], y=data["Sales Amount"], mode='lines', fill='tozeroy', line=dict(color="#3b82f6", width=4, shape='spline'), fillcolor='rgba(59, 130, 246, 0.1)', hoverinfo='x+y'))
        fig.update_layout(template="plotly_white", height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR, margin=dict(l=0, r=0, t=0, b=0), hovermode="x unified", xaxis=dict(showgrid=False, linecolor="rgba(0,0,0,0)", tickfont=dict(size=10, weight='bold', color='#94a3b8')), yaxis=dict(showgrid=False, showticklabels=False))
        return fig

    @rx.var
    def channel_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        df = self.filtered_df.groupby("Channel")["Sales Amount"].sum().reset_index()
        fig = px.pie(df, values="Sales Amount", names="Channel", hole=0.7, color_discrete_sequence=CHART_COLORS)
        fig.update_layout(template="plotly_white", height=300, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR, margin=dict(l=0, r=0, t=0, b=0))
        fig.update_traces(textinfo='none', hoverinfo='label+percent')
        return fig

    @rx.var
    def state_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        df = self.filtered_df.groupby("CUSTOMER STATE")["Sales Amount"].sum().reset_index().sort_values("Sales Amount", ascending=False).head(10)
        df["Sales Amount"] = (df["Sales Amount"] / 10000000).round(2)
        fig = px.bar(df, x="Sales Amount", y="CUSTOMER STATE", orientation='h', color="CUSTOMER STATE", color_discrete_sequence=CHART_COLORS, text="Sales Amount")
        fig.update_layout(template="plotly_white", height=580, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR, margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=True, gridcolor=BORDER_COLOR), yaxis=dict(showgrid=False))
        fig.update_traces(textposition='outside')
        return fig

    @rx.var
    def product_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        df = self.filtered_df.groupby("Product")["Sales Amount"].sum().reset_index().sort_values("Sales Amount", ascending=False).head(5)
        df["Sales Amount"] = (df["Sales Amount"] / 10000000).round(2)
        fig = px.bar(df, x="Product", y="Sales Amount", color="Product", color_discrete_sequence=CHART_COLORS, text="Sales Amount")
        fig.update_layout(template="plotly_white", height=580, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(showgrid=True, gridcolor=BORDER_COLOR), xaxis=dict(showgrid=False))
        fig.update_traces(textposition='outside')
        return fig

    @rx.var
    def supply_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        df = self.filtered_df.groupby("TYPE OF SUPPLY")["Sales Amount"].sum().reset_index()
        df["Sales Amount"] = (df["Sales Amount"] / 10000000).round(2)
        fig = px.bar(df, x="TYPE OF SUPPLY", y="Sales Amount", color="TYPE OF SUPPLY", color_discrete_sequence=CHART_COLORS, text="Sales Amount")
        fig.update_layout(template="plotly_white", height=580, showlegend=False, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR, margin=dict(l=20, r=20, t=20, b=20), yaxis=dict(showgrid=True, gridcolor=BORDER_COLOR), xaxis=dict(showgrid=False))
        fig.update_traces(textposition='outside')
        return fig

    @rx.var
    def loyalty_radar_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        # Synthetic loyalty metrics for radar visualization
        categories = ['Retention', 'Frequency', 'Monetary', 'Diversity', 'Stability']
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=[90, 85, 95, 70, 88], theta=categories, fill='toself', name='VIP Segment', line_color=ACCENT_BLUE))
        fig.add_trace(go.Scatterpolar(r=[60, 50, 40, 80, 55], theta=categories, fill='toself', name='Casual Segment', line_color="#10b981"))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100], gridcolor=BORDER_COLOR), angularaxis=dict(gridcolor=BORDER_COLOR)), template="plotly_white", height=400, showlegend=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR)
        return fig

    @rx.var
    def bcg_bubble_chart(self) -> go.Figure:
        if self.filtered_df.empty: return go.Figure()
        df = self.filtered_df.groupby("Product").agg(sales=("Sales Amount", "sum"), count=("Quantity", "sum")).reset_index().head(15)
        df["growth"] = [15, 2, -5, 20, 10, -8, 4, 30, 12, 5, -2, 18, 0, 7, -10][:len(df)] # Synthetic growth placeholder
        fig = px.scatter(df, x="sales", y="growth", size="count", color="Product", hover_name="Product", size_max=60, color_discrete_sequence=CHART_COLORS)
        fig.update_layout(template="plotly_white", height=500, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=TEXT_COLOR, margin=dict(l=20, r=20, t=20, b=20), xaxis=dict(showgrid=True, gridcolor=BORDER_COLOR, title="Cumulative Revenue"), yaxis=dict(showgrid=True, gridcolor=BORDER_COLOR, title="MoM Growth %"))
        # Add quadrant lines
        fig.add_hline(y=10, line_dash="dash", line_color="#94a3b8", opacity=0.3)
        fig.add_vline(x=df["sales"].mean(), line_dash="dash", line_color="#94a3b8", opacity=0.3)
        return fig

    def toggle_all_months(self, select: bool): self.selected_months = self.months if select else []
    def toggle_all_states(self, select: bool): self.selected_states = self.states if select else []
    def toggle_all_brands(self, select: bool): self.selected_brands = self.brands if select else []
    def toggle_all_channels(self, select: bool): self.selected_channels = self.channels if select else []
    def toggle_all_supply(self, select: bool): self.selected_supply_types = self.supply_types if select else []

    def toggle_month(self, month: str, checked: bool): self.selected_months = self.selected_months + [month] if checked else [m for m in self.selected_months if m != month]
    def toggle_state(self, state: str, checked: bool): self.selected_states = self.selected_states + [state] if checked else [s for s in self.selected_states if s != state]
    def toggle_brand(self, brand: str, checked: bool): self.selected_brands = self.selected_brands + [brand] if checked else [b for b in self.selected_brands if b != brand]
    def toggle_channel(self, channel: str, checked: bool): self.selected_channels = self.selected_channels + [channel] if checked else [c for c in self.selected_channels if c != channel]
    def toggle_supply(self, supply: str, checked: bool): self.selected_supply_types = self.selected_supply_types + [supply] if checked else [s for s in self.selected_supply_types if s != supply]
