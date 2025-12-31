import pandas as pd
import os

# Dummy Sales Data
sales_data = {
    "BILLING DATE": ["01-04-2025", "15-04-2025", "01-05-2025", "20-05-2025"],
    "TOTAL VALUE": [1000, 2000, 1500, 3000],
    "BRAND DESCRIPTION": ["BrandA", "BrandB", "BrandA", "BrandC"],
    "SKU QTY": [10, 20, 15, 30],
    "CHANNEL": ["Amazon", "Flipkart", "B2B", "Direct"],
    "PRODUCT": ["Prod1", "Prod2", "Prod1", "Prod3"],
    "CUSTOMER STATE": ["Delhi", "Mumbai", "Delhi", "Bangalore"],
    "TYPE OF SUPPLY": ["B2C", "B2C", "B2B", "B2C"],
    "DOCUMENT DESCRIPTION": ["Inv1", "Inv2", "Inv3", "Inv4"],
    "BILLING DOCUMENT": ["Doc1", "Doc2", "Doc3", "Doc4"]
}
df_sales = pd.DataFrame(sales_data)
df_sales.to_excel("dummy_sales.xlsx", index=False)

# Dummy Courier Data
courier_data = {
    "gross_amount": [100, 200, 150, 300],
    "waybill_num": ["WB1", "WB2", "WB3", "WB4"],
    "status": ["Delivered", "In Transit", "Delivered", "RTO"],
    "fpd": ["Yes", "No", "Yes", "No"],
    "pickup_date": ["2025-04-02", "2025-04-16", "2025-05-02", "2025-05-21"]
}
df_courier = pd.DataFrame(courier_data)
df_courier.to_excel("dummy_courier.xlsx", index=False)

print("Dummy data created: dummy_sales.xlsx, dummy_courier.xlsx")
