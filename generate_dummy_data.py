import pandas as pd
import numpy as np
from datetime import datetime
from prophet import Prophet
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.ensemble import IsolationForest, RandomForestClassifier
# from xgboost import XGBClassifier # Removed due to missing libomp
from lifelines import KaplanMeierFitter
import warnings
warnings.filterwarnings('ignore')

def generate_data():
    print("Generating synthetic historical data and training models...")
    file_path = "assets/predictive_analytics_data.xlsx"
    
    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        
        # 1. Revenue Forecast (Prophet)
        print("Training Prophet for Revenue Forecasting...")
        dates = pd.date_range(start='2023-01-01', periods=24, freq='ME')
        # Simulate historical data with seasonality and trend
        base_sales = np.linspace(100, 200, 24)
        seasonality = np.sin(np.linspace(0, 4*np.pi, 24)) * 20
        noise = np.random.normal(0, 5, 24)
        history_sales = base_sales + seasonality + noise
        
        df_prophet = pd.DataFrame({'ds': dates, 'y': history_sales})
        m = Prophet(yearly_seasonality=True, weekly_seasonality=False, daily_seasonality=False)
        m.fit(df_prophet)
        
        future = m.make_future_dataframe(periods=6, freq='ME')
        forecast = m.predict(future)
        
        # Format for Export
        df_rev_export = forecast[['ds', 'yhat']].tail(12).copy()
        df_rev_export.columns = ['Month', 'Forecast (AI)']
        # Add actuals for simpler plotting alignment (simulated)
        df_rev_export['Realized Sales'] = np.append(history_sales[-6:], [np.nan]*6)
        df_rev_export['Forecast (AI)'] = df_rev_export['Forecast (AI)'].round(2)
        df_rev_export.to_excel(writer, sheet_name='RevenueGrowth', index=False)


        # 2. Regression (Price Elasticity - SKLearn)
        print("Training Regression Model...")
        discounts = np.random.uniform(0, 30, 100)
        # Sales impact = 2.5 * discount + noise
        impact = 2.5 * discounts + np.random.normal(0, 5, 100)
        
        reg = LinearRegression()
        reg.fit(discounts.reshape(-1, 1), impact)
        
        df_reg = pd.DataFrame({'Discount': discounts, 'Sales Impact': impact})
        df_reg.to_excel(writer, sheet_name='Regression', index=False)


        # 3. Survival Analysis (Lifelines)
        print("Fitting Kaplan-Meier Survival Curve...")
        T = np.random.exponential(5, size=100) # Time to churn
        E = np.random.binomial(1, 0.7, size=100) # Event observed
        
        kmf = KaplanMeierFitter()
        kmf.fit(T, event_observed=E)
        
        df_surv = kmf.survival_function_.reset_index()
        df_surv.columns = ['Time', 'Survival Probability']
        df_surv = df_surv[df_surv['Time'] <= 6] # Limit to 6 months view
        df_surv.to_excel(writer, sheet_name='Survival', index=False)


        # 4. Propensity Scoring (Random Forest - replacing XGBoost due to missing libomp)
        print("Training Random Forest for Propensity...")
        # Synthetic features: [Recency, Frequency, Monetary]
        X = np.random.rand(100, 3)
        # Synthetic target (1 = likely to buy)
        y = (X[:, 0] * 0.3 + X[:, 1] * 0.5 + X[:, 2] * 0.2 > 0.5).astype(int)
        
        # Use RandomForest instead of XGBoost
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X, y)
        scores = rf.predict_proba(X)[:, 1]
        
        categories = ['High Value', 'Loyal', 'At Risk', 'Lost']
        # Assign categories based on score bins
        df_prop = pd.DataFrame({'Score': scores})
        df_prop['Category'] = pd.cut(df_prop['Score'], bins=4, labels=categories[::-1])
        # Aggregated for chart
        df_prop_agg = df_prop.groupby('Category')['Score'].mean().reset_index()
        df_prop_agg.to_excel(writer, sheet_name='Propensity', index=False)


        # 5. BCG Matrix (KMeans Cluster)
        print("Clustering for BCG Matrix...")
        entities = ['Zepto', 'Blinkit', 'Amazon', 'Flipkart'] + [f'Comp-{i}' for i in range(20)]
        market_share = np.random.uniform(0.1, 0.9, len(entities))
        growth_rate = np.random.uniform(-0.1, 0.5, len(entities))
        
        X_bcg = np.column_stack((market_share, growth_rate))
        kmeans = KMeans(n_clusters=4, random_state=42)
        kmeans.fit(X_bcg)
        
        df_bcg = pd.DataFrame({
            'Entity': entities,
            'Market Share': market_share,
            'Growth Rate': growth_rate,
            'Size': np.random.uniform(10, 50, len(entities))
        })
        df_bcg.to_excel(writer, sheet_name='BCG', index=False)


        # 6. Toxic SKU (Isolation Forest)
        print("Detecting Toxic SKUs with Isolation Forest...")
        n_skus = 50
        margin = np.random.normal(20, 5, n_skus)
        returns = np.random.normal(5, 2, n_skus)
        # Inject outliers
        margin[-5:] = np.random.normal(5, 1, 5) # Low margin
        returns[-5:] = np.random.normal(15, 2, 5) # High return
        
        X_toxic = np.column_stack((margin, returns))
        clf = IsolationForest(contamination=0.1, random_state=42)
        preds = clf.fit_predict(X_toxic)
        
        df_toxic = pd.DataFrame({
            'SKU_ID': [f'SKU-{i}' for i in range(100, 100+n_skus)],
            'Metric_X': margin,
            'Metric_Y': returns,
            'Is_Toxic': preds
        })
        # Filter mostly toxic or all for scatter
        df_toxic.to_excel(writer, sheet_name='ToxicSKU', index=False)

        # --- Phase 3: Advanced Intelligence Modules ---

        # 7. SKU Forecast (Prophet again for specific SKU)
        dates_sku = pd.date_range(start='2024-01-01', periods=12, freq='ME')
        # SKU History
        sku_hist = np.linspace(500, 800, 12) + np.random.normal(0, 20, 12)
        df_sku_p = pd.DataFrame({'ds': dates_sku, 'y': sku_hist})
        m_sku = Prophet()
        m_sku.fit(df_sku_p)
        future_sku = m_sku.make_future_dataframe(periods=3, freq='ME')
        forecast_sku = m_sku.predict(future_sku)
        
        df_sku_export = forecast_sku[['ds', 'yhat']].copy()
        df_sku_export.columns = ['Date', 'AI Forecast']
        df_sku_export['SKU'] = 'SKU-101'
        df_sku_export['Actual Demand'] = np.append(sku_hist, [np.nan]*3)
        df_sku_export.to_excel(writer, sheet_name='SKUForecast', index=False)

        # 8, 9, 10 pass through simulated logic as they rely on business rules more than ML
        # just regenerating them for consistency
        demand_data = {
            'SKU_ID': ['SKU-101', 'SKU-102', 'SKU-205', 'SKU-310', 'SKU-404', 'SKU-520'],
            'Category': ['Electronics', 'Electronics', 'Home', 'Fashion', 'Kitchen', 'Home'],
            'Current Stock': [120, 50, 800, 15, 60, 200],
            'Forecasted Demand (M+1)': [150, 200, 750, 100, 50, 250],
            'Reorder Qty': [30, 150, 0, 85, 0, 50],
            'Status': ['Partial Stock', 'Critical Low', 'Overstock', 'Critical Low', 'Healthy', 'Reorder Soon']
        }
        pd.DataFrame(demand_data).to_excel(writer, sheet_name='DemandPlanning', index=False)

        seasonality_data = {
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            'Baseline Sales': [100, 110, 120, 115, 125, 130, 120, 140, 150, 180, 200, 220],
            'Promo Uplift':   [10,  5,   15,  10,  20,  25,  10,  30,  40,  60,  80,  90] 
        }
        pd.DataFrame(seasonality_data).to_excel(writer, sheet_name='Seasonality', index=False)

        risk_data = {
            'SKU_ID': ['SKU-310', 'SKU-102', 'SKU-520', 'SKU-777', 'SKU-888'],
            'Risk Level': ['Critical', 'High', 'Medium', 'Low', 'Safe'],
            'Days Cover': [2, 5, 12, 25, 45],
            'Alert Message': ['Only 2 days stock left.', 'Stock below safety.', 'Approaching reorder.', 'Healthy.', 'Excess inventory.']
        }
        pd.DataFrame(risk_data).to_excel(writer, sheet_name='StockRisk', index=False)

    print(f"Successfully generated Real ML Analytics Data at {file_path}")

if __name__ == "__main__":
    generate_data()
