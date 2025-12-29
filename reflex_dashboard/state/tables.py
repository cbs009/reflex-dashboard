import reflex as rx
import pandas as pd
from typing import List, Dict
from .charts import ChartState
from ..colors import CHART_COLORS, TEXT_COLOR
from ..models import MonthlyValue, ChannelSummary, StateSummary, InvRetChannel, InvRetRow

class TableState(ChartState):
    
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
    def summary_table_columns(self) -> list[str]:
        """Dynamic columns for the monthly summary table."""
        if self.filtered_df.empty:
            return []
        months = sorted(self.filtered_df["Month_Date"].unique())
        return [pd.Timestamp(m).strftime('%b') for m in months]

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
    def monthly_sales_return_data(self) -> list[ChannelSummary]:
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
