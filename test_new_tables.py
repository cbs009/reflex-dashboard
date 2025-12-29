
import pandas as pd
import os
import sys

# Mock classes to match Reflex classes
class MockMonthlyValue:
    def __init__(self, month, value, is_shaded):
        self.month = month
        self.value = value
        self.is_shaded = is_shaded
    def __repr__(self):
        return f"MV({self.month}, {self.value})"

class MockChannelSummary:
    def __init__(self, channel, monthly_values, total_value, children, is_total):
        self.channel = channel
        self.monthly_values = monthly_values
        self.total_value = total_value
        self.children = children
        self.is_total = is_total
    def __repr__(self):
        return f"CS({self.channel}, Total: {self.total_value})"

# Global for Mock State
class State:
    filtered_df = pd.DataFrame()
    
    # Inject Property Decorator Mock
    class rx_var_mock:
        def __init__(self, func):
            self.func = func
        def __get__(self, obj, objtype=None):
            return self.func(obj)

    # Re-implement properties using the logic from reflex_dashboard.py
    # NOTE: I am copying the logic here because I cannot import from reflex_dashboard.py 
    # easily without the whole Reflex app context which might fail in a simple script.
    # Ideally I should import, but let's see if I can just verify the logic by running the *actual* logic
    # if I can mock rx.Base.
    
    # Actually, let's try to import the State class from reflex_dashboard if possible,
    # but that requires 'reflex'. If 'reflex' is installed in the env, I can try.
    # If not, I'll copy the logic. The user has reflex running, so it should be installed.
    pass

# Strategy: Create a script that imports 'reflex' and the State class if possible,
# OR just copy the logic to test it in isolation.
# Given the user environment, 'reflex' is likely available. 
# However, importing 'reflex_dashboard' might trigger app init code.
# The safest way to verify the *logic* (which is what I care about here) is to copy it 
# into the test script or assume the 'reflex_dashboard.py' edits are correct and just 
# try to run a script that reuses the logic.
# Let's simple copy the logic I just wrote to verify it works with pandas.

def monthly_sales_return_data(self):
    if self.filtered_df.empty:
        return []

    df = self.filtered_df[self.filtered_df["DOCUMENT DESCRIPTION"] == "Sales Return"].copy()
    
    # Ensure Month_Date is present
    if "Month_Date" not in self.filtered_df.columns: 
            return []

    months = sorted(self.filtered_df["Month_Date"].unique())
    
    def fmt(val):
        return f"₹{val:,.0f}" 

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
                MockMonthlyValue(
                    month=pd.Timestamp(m).strftime('%b -%Y'), 
                    value=fmt(val),
                    is_shaded=is_shade_col
                )
            )
            gt_monthly_sums[m] += val
            
        summary_data.append(
            MockChannelSummary(
                channel=str(channel),
                monthly_values=ch_monthly_values,
                total_value=fmt(ch_total),
                children=[],
                is_total=False
            )
        )

    gt_vals = []
    gt_total_all = 0
    for i, m in enumerate(months):
        val = gt_monthly_sums[m]
        is_shade_col = (i % 2 == 0)
        gt_vals.append(
            MockMonthlyValue(
                month=pd.Timestamp(m).strftime('%b -%Y'), 
                value=fmt(val),
                is_shaded=is_shade_col
            )
        )
        gt_total_all += val
        
    summary_data.append(
            MockChannelSummary(
            channel="Total Returns", 
            monthly_values=gt_vals,
            total_value=fmt(gt_total_all),
            children=[],
            is_total=True
        )
    )
    
    return summary_data

def invoice_vs_return_data(self):
    if self.filtered_df.empty:
            return []

    df = self.filtered_df.copy()
    months = sorted(df["Month_Date"].unique())
    channels = sorted(df["Channel"].unique().tolist())
    
    rows = []
    
    col_totals_inv = {c: 0 for c in channels}
    col_totals_ret = {c: 0 for c in channels}
    grand_total_inv_sum = 0
    grand_total_ret_sum = 0

    for m in months:
        m_df = df[df["Month_Date"] == m]
        month_label = pd.Timestamp(m).strftime('%b -%Y')
        
        row_data = {
            "month": month_label,
            "channels": [],
            "is_pct": False,
            "is_total": False
        }
        
        row_total_inv = 0
        row_total_ret = 0
        
        for ch in channels:
            ch_data = m_df[m_df["Channel"] == ch]
            
            inv_count = ch_data[ch_data["DOCUMENT DESCRIPTION"] != "Sales Return"]["BILLING DOCUMENT"].nunique()
            ret_count = ch_data[ch_data["DOCUMENT DESCRIPTION"] == "Sales Return"]["BILLING DOCUMENT"].nunique()
            
            col_totals_inv[ch] += inv_count
            col_totals_ret[ch] += ret_count
            
            row_total_inv += inv_count
            row_total_ret += ret_count
            
            ret_color = "red" if ret_count > 0 else "black"
            
            row_data["channels"].append({
                "channel": ch,
                "inv": str(inv_count) if inv_count > 0 else "-",
                "ret": str(ret_count) if ret_count > 0 else "-",
                "ret_color": ret_color
            })
        
        grand_total_inv_sum += row_total_inv
        grand_total_ret_sum += row_total_ret
        
        row_data["grand_total"] = {
            "inv": str(row_total_inv),
            "ret": str(row_total_ret) if row_total_ret > 0 else "-"
        }
        
        rows.append(row_data)

    total_row = {
        "month": "Total Count",
        "channels": [],
        "is_total": True,
        "is_pct": False
    }
    for ch in channels:
        total_row["channels"].append({
                "channel": ch,
                "inv": str(col_totals_inv[ch]),
                "ret": str(col_totals_ret[ch]),
                "ret_color": "red"
        })
    total_row["grand_total"] = {
            "inv": str(grand_total_inv_sum),
            "ret": str(grand_total_ret_sum)
    }
    rows.append(total_row)

    pct_row = {
            "month": "Return % (Ret/Inv)",
            "channels": [],
            "is_pct": True,
            "is_total": False
    }
    
    for ch in channels:
            inv = col_totals_inv[ch]
            ret = col_totals_ret[ch]
            pct = (ret / inv * 100) if inv > 0 else 0
            pct_row["channels"].append({
                "channel": ch,
                "val": f"{pct:.2f}%",
                "color": "green"
            })
            
    gt_pct = (grand_total_ret_sum / grand_total_inv_sum * 100) if grand_total_inv_sum > 0 else 0
    pct_row["grand_total"] = f"{gt_pct:.2f}%"
    
    rows.append(pct_row)
    
    return rows

if __name__ == "__main__":
    # Prepare Data
    file_path = "uploaded_files/Uoload_ecom_sale.xlsx"
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        sys.exit(1)
        
    print(f"Reading {file_path}")
    df = pd.read_excel(file_path)
    
    # Preprocessing (Simplified from reflex_dashboard.py)
    df.columns = df.columns.str.upper().str.strip()
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
    df = df.rename(columns=column_mapping)
    df = df.loc[:, ~df.columns.duplicated()]
    
    # Standardize Channel
    def map_channel(val):
        val = str(val).strip()
        v_upper = val.upper()
        if "AMAZON" in v_upper: return "Amazon"
        if "FLIPKART" in v_upper: return "Flipkart"
        if "RCLUB" in v_upper: return "rclub.in"
        if "BUSINESS CLUB" in v_upper: return "Rajnigandha Business Club" 
        if "RAJNIGANDHA" in v_upper: return "rajnigandha.com"
        if "B2B" in v_upper or "DEALER" in v_upper: return "B2B" 
        return val 
    df["Channel"] = df["Channel"].apply(map_channel)
    
    df["Sales Amount"] = pd.to_numeric(df["Sales Amount"].astype(str).str.replace(",", ""), errors="coerce").fillna(0)
    df["Billing_Date"] = pd.to_datetime(df["Billing_Date"], format="%d-%m-%Y", errors="coerce")
    df["Month_Date"] = df["Billing_Date"].dt.to_period("M").dt.to_timestamp()
    
    mock_state = State()
    mock_state.filtered_df = df
    
    print("\n--- Testing Monthly Sales Return Data ---")
    ret_data = monthly_sales_return_data(mock_state)
    print(f"Found {len(ret_data)} rows (Expected Channels + Total)")
    for r in ret_data:
        print(r)
        
    print("\n--- Testing Invoice vs Return Data ---")
    inv_data = invoice_vs_return_data(mock_state)
    print(f"Found {len(inv_data)} rows")
    for r in inv_data:
        print(f"Month: {r['month']}, GrandTotal: {r.get('grand_total')}")