import reflex as rx
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from .base import BaseState
from ..colors import CHART_COLORS, TEXT_COLOR, CARD_BG, BORDER_COLOR

class CustomerState(BaseState):
    """State for the Customer Science tab."""
    
    @rx.var
    def rfm_radar_chart(self) -> go.Figure:
        """Mock data for RFM Behavioral Radar."""
        categories = ['Recency', 'Frequency', 'Monetary', 'Consistency', 'Bundling']
        values = [80, 65, 40, 70, 55] # Example shape
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]], # Close the loop
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(0, 255, 255, 0.2)', # Neon Cyan tint
            line=dict(color='#00FFFF', width=3),
            marker=dict(size=5, color='#00FFFF'),
            name='Activity'
        ))
        
        # Add a secondary "benchmark" or "avg" shape for visual complexity (reddish)
        values_2 = [50, 50, 50, 50, 50]
        fig.add_trace(go.Scatterpolar(
            r=values_2 + [values_2[0]],
            theta=categories + [categories[0]],
            fill='toself',
            fillcolor='rgba(255, 0, 255, 0.1)', # Neon Pink tint
            line=dict(color='#FF00FF', width=2, dash='dot'),
            marker=dict(size=0),
            name='Benchmark'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100],
                    showticklabels=False, # Clean look
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=16, color='gray', family="Inter", weight="bold"),
                    gridcolor='rgba(255,255,255,0.1)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=40, r=40, t=80, b=20), # Increased top margin for Recency label
            showlegend=False,
            height=660,
            hoverlabel=dict(bgcolor="white", font_size=16, font_family="Inter", font_color="black"),
            font=dict(size=14),
        )
        return fig

    @rx.var
    def market_basket_data(self) -> list[dict]:
        """Mock data for Market Basket Associations."""
        return [
            {"pairs": "RG 100g + Pan", "lift": 4.2, "confidence": 82, "support": 15},
            {"pairs": "RG 117g + RG 4g", "lift": 3.8, "confidence": 75, "support": 12},
            {"pairs": "Elaichi + Twin", "lift": 2.5, "confidence": 45, "support": 8},
            {"pairs": "Saffron + 100g", "lift": 2.1, "confidence": 38, "support": 5},
            {"pairs": "Dates + Silver", "lift": 1.9, "confidence": 32, "support": 4},
            {"pairs": "Supari + Mix", "lift": 1.5, "confidence": 28, "support": 3},
        ]

    @rx.var
    def revenue_trends_chart(self) -> go.Figure:
        """Mock data for New vs Returning Revenue."""
        months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]
        new_rev = [15, 14, 13, 17, 18, 20, 24, 23, 20, 18, 19] # Smoothed random
        ret_rev = [20, 22, 28, 30, 35, 38, 48, 55, 35, 38, 40] 
        
        # Area chart needs stacked values usually, or just direct values with fill
        
        fig = go.Figure()
        
        # New Revenue (Bottom)
        fig.add_trace(go.Scatter(
            x=months, y=new_rev,
            mode='lines',
            line=dict(width=3, color='#00BFFF'), # Neon Blue
            stackgroup='one',
            fillcolor='rgba(0, 191, 255, 0.4)',
            name='New Revenue'
        ))
        
        # Returning Revenue (Top)
        fig.add_trace(go.Scatter(
            x=months, y=ret_rev,
            mode='lines',
            line=dict(width=3, color='#9D00FF'), # Neon Purple
            stackgroup='one',
            fillcolor='rgba(157, 0, 255, 0.2)',
            name='Returning Revenue'
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=TEXT_COLOR,
            margin=dict(l=10, r=10, t=20, b=20),
            height=660,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="white")),
            hovermode="x unified",
            xaxis=dict(showgrid=False, showline=False, tickfont=dict(size=10, color='gray')),
            yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.1)', gridwidth=1, showline=False, zeroline=False, tickfont=dict(size=10, color='gray')),
            clickmode="event+select", # Trying to avoid interactions blocking view
            hoverlabel=dict(bgcolor="white", font_size=16, font_family="Inter", font_color="black"),
            font=dict(size=14),
        )
        return fig

    @rx.var
    def wallet_share_chart(self) -> go.Figure:
        """Mock data for Customer Wallet Share."""
        dates = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb"]
        share = [18, 17.5, 17.5, 18, 19, 18.5, 19.5, 20, 20.5, 21, 21.5] # Slow growth
        
        fig = go.Figure()
        
        # Step line equivalent
        fig.add_trace(go.Scatter(
            x=dates, y=share,
            mode='lines',
            line=dict(color='#39FF14', width=4, shape='hv'), # Neon Lime
            name='Wallet Share'
        ))
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=TEXT_COLOR,
            margin=dict(l=10, r=10, t=20, b=20),
            height=660,
            showlegend=False,
            xaxis=dict(showgrid=False, showline=True, linecolor='gray', tickfont=dict(size=10, color='gray')),
            yaxis=dict(
                showgrid=True, gridcolor='rgba(255,255,255,0.1)', gridwidth=1, 
                showline=False, 
                zeroline=False, 
                tickfont=dict(size=10, color='gray'),
                range=[0, 24]
            ),
            hoverlabel=dict(bgcolor="white", font_size=16, font_family="Inter", font_color="black"),
            font=dict(size=14),
        )
        return fig

    @rx.var
    def ltv_segments_chart(self) -> go.Figure:
        """Mock data for Predictive LTV Segments (Donut)."""
        labels = ['Champions', 'Loyal', 'Potential', 'Churning']
        values = [55, 25, 15, 5]
        colors = ['#2C3E50', '#4A5568', '#718096', '#F56565'] # Dark Blue/Grays + Red for Churn
        # Adjust colors to match screenshot: Dark blue dominant, some gray, some red
        colors = ['#39FF14', '#A0AEC0', '#718096', '#FF0000'] # Very Green, Gray, Gray, Very Red

        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=0.6,
            marker=dict(colors=colors, line=dict(color='#000000', width=2)),
            sort=False
        )])
        
        fig.update_traces(
            textinfo='none',
            hoverinfo='label+percent'
        )
        
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=TEXT_COLOR,
            margin=dict(l=10, r=10, t=10, b=10),
            height=660,
            showlegend=False, # Custom legend in UI
            hoverlabel=dict(bgcolor="white", font_size=16, font_family="Inter", font_color="black"),
            font=dict(size=14),
        )
        return fig

class CustomerBehaviorState(BaseState):
    """State for the Behavioral Metrics & AI section."""
    
    # --- Interactive AOV Calculator ---
    aov_revenue: float = 0.0
    aov_orders: int = 0
    calculated_aov: float = 0.0

    def calculate_aov(self):
        if self.aov_orders > 0:
            self.calculated_aov = round(self.aov_revenue / self.aov_orders, 2)
        else:
            self.calculated_aov = 0.0

    def set_aov_revenue(self, val):
        try:
            self.aov_revenue = float(val)
        except ValueError:
            self.aov_revenue = 0.0
    
    def set_aov_orders(self, val):
        try:
            self.aov_orders = int(val)
        except ValueError:
            self.aov_orders = 0

    # --- Feature Importance Chart ---
    @rx.var
    def feature_importance_chart(self) -> go.Figure:
        try:
            df = pd.read_csv("data/feature_importance.csv")
            df = df.sort_values(by="Importance", ascending=True) # Ascending for horizontal bar
        except Exception:
            # Fallback if file not found
            data = {'Feature': ['Recency', 'Frequency', 'Monetary'], 'Importance': [0.5, 0.3, 0.2]}
            df = pd.DataFrame(data)

        fig = go.Figure(go.Bar(
            x=df['Importance'],
            y=df['Feature'],
            orientation='h',
            marker=dict(
                color=df['Importance'],
                colorscale=[[0, '#00BFFF'], [1, '#48BB78']], # Blue to Green
                line=dict(width=0)
            ),
            text=df['Importance'],
            textposition='auto',
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=10, b=10),
            height=300,
            xaxis=dict(visible=False),
            yaxis=dict(tickfont=dict(size=12, color='white')),
            bargap=0.2
        )
        return fig

    # --- Cohort Retention Heatmap ---
    @rx.var
    def cohort_heatmap_chart(self) -> go.Figure:
        try:
            df = pd.read_csv("data/cohort_retention.csv")
            cohorts = df['Cohort'].tolist()
            # Extract only the M columns for z-values
            z_values = df[['M0', 'M1', 'M2', 'M3', 'M4']].values.tolist()
            x_labels = ['M0', 'M1', 'M2', 'M3', 'M4']
        except Exception:
             cohorts = ['Jan', 'Feb']
             z_values = [[100, 50], [100, 60]]
             x_labels = ['M0', 'M1']

        fig = go.Figure(data=go.Heatmap(
            z=z_values,
            x=x_labels,
            y=cohorts,
            colorscale=[[0, '#0E1117'], [1, '#48BB78']], # Dark to Green
            text=z_values,
            texttemplate="%{text}%",
            showscale=False
        ))

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color=TEXT_COLOR,
            margin=dict(l=40, r=20, t=20, b=20),
            height=350,
            xaxis=dict(side="top", tickfont=dict(color='gray')),
            yaxis=dict(autorange="reversed", tickfont=dict(color='white'))
        )
        return fig
