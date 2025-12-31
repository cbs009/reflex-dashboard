
import pandas as pd
import os
import sys

try:
    print("Checking dependencies...")
    import openpyxl
    print("openpyxl is installed.")
except ImportError:
    print("❌ openpyxl is NOT installed. This is likely the cause if read_excel fails.")

path = "/Users/chandrabhushansingh/AI/data/Courier_details.xlsx"
print(f"Checking file at: {path}")

if not os.path.exists(path):
    print("❌ File does not exist!")
    sys.exit(1)

try:
    print("Reading Excel file...")
    # Attempt to read without engine spec first, then with openpyxl
    df = pd.read_excel(path) 
    print(f"✅ Data Loaded. Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    
    # Run the metrics logic
    avg_cost = df["total_amount"].mean() if not df.empty else 0
    print(f"Avg Cost: {avg_cost}")
    
    delivered = df[df["status"] == "Delivered"]
    print(f"Delivered count: {len(delivered)}")
    
    rto = df[df["status"] == "RTO"]
    print(f"RTO count: {len(rto)}")
    
except Exception as e:
    print(f"❌ Error reading/processing file: {e}")
