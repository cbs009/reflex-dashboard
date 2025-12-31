import reflex as rx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from .ai import AIState
from ..colors import CHART_COLORS, TEXT_COLOR, CARD_BG

class PredictiveState(AIState):
    """State for Predictive Engine."""
    
    revenue_data: list[dict] = []
    regression_data: list[dict] = []
    survival_data: list[dict] = []
    propensity_data: list[dict] = []
    bcg_data: list[dict] = []
    toxic_data: list[dict] = []
    
    # Phase 3 Data
    sku_forecast_data: list[dict] = []
    demand_data: list[dict] = []
    seasonality_data: list[dict] = []
    risk_data: list[dict] = []

    def load_predictive_data(self):
        """Load data from Excel file."""
        try:
            file_path = "assets/predictive_analytics_data.xlsx"
            
            # Load Revenue Growth
            df_rev = pd.read_excel(file_path, sheet_name='RevenueGrowth')
            self.revenue_data = df_rev.to_dict('records')
            
            # Load Regression
            df_reg = pd.read_excel(file_path, sheet_name='Regression')
            self.regression_data = df_reg.to_dict('records')
            
            # Load Survival
            df_surv = pd.read_excel(file_path, sheet_name='Survival')
            self.survival_data = df_surv.to_dict('records')
            
            # Load Propensity
            df_prop = pd.read_excel(file_path, sheet_name='Propensity')
            self.propensity_data = df_prop.to_dict('records')
            
            # Load BCG
            df_bcg = pd.read_excel(file_path, sheet_name='BCG')
            self.bcg_data = df_bcg.to_dict('records')
            
            # Load Toxic SKU
            df_toxic = pd.read_excel(file_path, sheet_name='ToxicSKU')
            self.toxic_data = df_toxic.to_dict('records')

            # --- Phase 3 Loading ---
            # SKU Forecast
            df_sku = pd.read_excel(file_path, sheet_name='SKUForecast')
            self.sku_forecast_data = df_sku.to_dict('records')
            
            # Demand Planning
            df_demand = pd.read_excel(file_path, sheet_name='DemandPlanning')
            self.demand_data = df_demand.to_dict('records')
            
            # Seasonality
            df_seas = pd.read_excel(file_path, sheet_name='Seasonality')
            self.seasonality_data = df_seas.to_dict('records')
            
            # Risk Alerts
            df_risk = pd.read_excel(file_path, sheet_name='StockRisk')
            self.risk_data = df_risk.to_dict('records')
            
        except Exception as e:
            print(f"Error loading predictive data: {e}")

    @rx.var
    def revenue_growth_chart(self) -> go.Figure:
        if not self.revenue_data:
            return go.Figure()
            
        df = pd.DataFrame(self.revenue_data)
        
        fig = go.Figure()
        
        # Realized Sales Line
        fig.add_trace(go.Scatter(
            x=df['Month'], 
            y=df['Realized Sales'],
            mode='lines+markers',
            name='Realized Sales',
            line=dict(color='#3B82F6', width=4), # Blue
            marker=dict(size=8)
        ))
        
        # Forecast Line
        fig.add_trace(go.Scatter(
            x=df['Month'], 
            y=df['Forecast (AI)'],
            mode='lines+markers',
            name='Forecast (AI)',
            line=dict(color='#8B5CF6', width=4, dash='dot'), # Purple Dotted
            marker=dict(size=8, symbol='circle-open')
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        return fig

    @rx.var
    def regression_chart(self) -> go.Figure:
        if not self.regression_data:
            return go.Figure()
            
        df = pd.DataFrame(self.regression_data)
        
        # Sort values by Discount for clean line plotting
        df = df.sort_values(by="Discount")
        
        fig = go.Figure()
        
        # Scatter points (Actual Data)
        fig.add_trace(go.Scatter(
            x=df['Discount'],
            y=df['Sales Impact'],
            mode='markers',
            name='Actual Data',
            marker=dict(size=8, color='rgba(59, 130, 246, 0.6)', line=dict(width=1, color='#3B82F6'))
        ))
        
        # Trendline (Linear Regression Fit)
        # Using numpy polyfit for a cleaner trendline than connecting raw dots
        x = df['Discount']
        y = df['Sales Impact']
        slope, intercept = np.polyfit(x, y, 1)
        trend_line = slope * x + intercept
        
        fig.add_trace(go.Scatter(
            x=x,
            y=trend_line,
            mode='lines',
            name='Trend (Linear Fit)',
            line=dict(color='#F59E0B', width=3) # Amber for visibility
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False, title='Discount (%)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', title='Sales Impact ($)')
        )
        return fig
    
    @rx.var
    def survival_chart(self) -> go.Figure:
        if not self.survival_data:
            return go.Figure()
        
        df = pd.DataFrame(self.survival_data)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['Time'],
            y=df['Survival Probability'],
            mode='lines+markers',
            name='Survival %',
            line=dict(color='#8B5CF6', width=3),
            marker=dict(size=8, color='#C4B5FD', line=dict(width=2, color='#8B5CF6'))
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', range=[0.6, 1.05]),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    @rx.var
    def propensity_chart(self) -> go.Figure:
        if not self.propensity_data:
            return go.Figure()
            
        df = pd.DataFrame(self.propensity_data)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df['Category'],
            y=df['Score'],
            name='Score',
            marker_color='#3B82F6'
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    @rx.var
    def bcg_matrix_chart(self) -> go.Figure:
        if not self.bcg_data:
            return go.Figure()
        
        df = pd.DataFrame(self.bcg_data)
        
        # Define specific colors for each entity
        color_map = {
            'Zepto': '#8B5CF6',   # Violet
            'Blinkit': '#FACC15', # Yellow
            'Amazon': '#F97316',  # Orange
            'Flipkart': '#3B82F6' # Blue
        }
        
        fig = px.scatter(
            df, 
            x="Market Share", 
            y="Growth Rate",
            size="Size", 
            color="Entity",
            hover_name="Entity",
            size_max=50, # Slightly larger bubbles
            template="plotly_dark",
            color_discrete_map=color_map
        )
        
        fig.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", # Fully transparent
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(title='Share', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(title='Growth', showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig

    @rx.var
    def toxic_sku_chart(self) -> go.Figure:
        if not self.toxic_data:
            return go.Figure()
            
        df = pd.DataFrame(self.toxic_data)
        
        fig = px.scatter(
            df, 
            x="Metric_X", 
            y="Metric_Y",
            hover_name="SKU_ID",
            template="plotly_dark",
             color_discrete_sequence=['#EF4444'] # Red
        )
        
        fig.update_traces(marker=dict(size=8))
        
        fig.update_layout(
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)", # Fully transparent
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
             xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)'),
             showlegend=True,
             legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig
    
    # --- Phase 3 Logic ---

    @rx.var
    def sku_forecast_chart(self) -> go.Figure:
        if not self.sku_forecast_data:
            return go.Figure()
            
        df = pd.DataFrame(self.sku_forecast_data)
        
        fig = go.Figure()
        
        # Actual Demand
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['Actual Demand'],
            mode='lines+markers',
            name='Actual Demand',
            line=dict(color='#10B981', width=3), # Emerald Green
            marker=dict(size=6)
        ))
        
        # AI Forecast
        fig.add_trace(go.Scatter(
            x=df['Date'], 
            y=df['AI Forecast'],
            mode='lines+markers',
            name='AI Forecast',
            line=dict(color='#3B82F6', width=3, dash='dot'), # Blue Dotted
            marker=dict(size=6, symbol='diamond')
        ))
        
        fig.update_layout(
            template="plotly_dark",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        return fig

    @rx.var
    def seasonality_chart(self) -> go.Figure:
        if not self.seasonality_data:
            return go.Figure()
            
        df = pd.DataFrame(self.seasonality_data)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Month'],
            y=df['Baseline Sales'],
            name='Baseline',
            marker_color='#64748B' # Slate
        ))
        
        fig.add_trace(go.Bar(
            x=df['Month'],
            y=df['Promo Uplift'],
            name='Promo Uplift',
            marker_color='#F59E0B' # Amber
        ))
        
        fig.update_layout(
            barmode='stack',
            template="plotly_dark",
            height=300,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)')
        )
        return fig
    
    @rx.var
    def demand_planning_display(self) -> list[dict]:
        if not self.demand_data:
            return []
        
        data = self.demand_data
        enhanced_data = []
        for row in data:
            status_color = "gray"
            if row['Status'] == 'Critical Low': status_color = "red"
            elif row['Status'] == 'Reorder Soon': status_color = "yellow"
            elif row['Status'] == 'Overstock': status_color = "orange"
            elif row['Status'] == 'Healthy': status_color = "green"
            
            row['status_color'] = status_color
            enhanced_data.append(row)
            
        return enhanced_data

    @rx.var
    def risk_alerts(self) -> list[dict]:
        if not self.risk_data:
            return []
        return self.risk_data
