# Task List

- [x] Refactor Filters (`components/filters.py`)
    - [x] Create `horizontal_filter_bar` component
    - [x] Convert direct lists to Popovers/Dropdowns for horizontal space efficiency
    - [x] Style Date Date picker for horizontal layout
- [x] Refactor Layout (`components/layouts.py`)
    - [x] Extract current dashboard content into `overview_tab_content` function
    - [x] Create placeholder content functions for new tabs
    - [x] Implement Main Header "Enterprise Intelligence Suite"
    - [x] Implement `rx.tabs` structure
    - [x] Integrate `horizontal_filter_bar`
    - [x] Position AI Assistant
- [x] Verify
    - [x] Check Tab switching
    - [x] Check Filter functionality in new layout
    - [x] Verify Mobile responsiveness (basic check)

# Phase 3: Advanced Intelligence Modules (New Requirements)

- [ ] Predictive Engine (Forecasting & Replenishment)
    - [ ] SKU-level revenue forecasting (ARIMA/Prophet/ML)
    - [ ] Demand forecasting for reorder planning
    - [ ] Seasonality & promo uplift measurement
    - [ ] Out-of-stock risk alerts

- [ ] Operations Lab (Inventory & Logistics)
    - [ ] Inventory & Stock Efficiency Analytics (Safety stock, Ageing, Dead stock)
    - [ ] Packaging + Weight + Fraud Control (ERP vs Courier weight, Overcharging detection)

- [ ] Strategy Lab (Geo & Market)
    - [ ] Pincode, Zone & Geo Intelligence (Heatmaps, Route optimization, Zone pricing)

- [ ] Customer Science (Advanced Analytics)
    - [ ] Customer Analytics (CLV, Segmentation, Repeat behavior)
    - [ ] Basket Analysis (Apriori/Association rules)
    - [ ] Churn Forecasting & RTO Risk Prediction
    - [ ] Clustering Models (Customer K-Means, SKU Clustering, Regional Clusters)
