import reflex as rx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from .kpi import KPIState
from ..colors import CHART_COLORS, ACCENT_COLOR, TEXT_COLOR, BORDER_COLOR, CARD_BG

class ChartState(KPIState):
    
    @rx.var
    def monthly_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
        
        data = self.filtered_df.groupby("Month_Date")["Sales Amount"].sum().reset_index()
        data["Month"] = data["Month_Date"].dt.strftime('%b-%Y')
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        
        # Create colors for each point
        marker_colors = [CHART_COLORS[i % len(CHART_COLORS)] for i in range(len(data))]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=data["Month"],
            y=data["Sales Amount"],
            mode='lines+markers+text',
            text=data["Sales Amount"],
            textposition='middle center',
            textfont=dict(
                size=10, 
                color='white', 
                weight='bold'
            ),
            marker=dict(
                size=35,
                color=marker_colors,
                symbol='circle',
                line=dict(width=2, color='white'),
                opacity=1
            ),
            line=dict(
                color=ACCENT_COLOR,
                width=3
            ),
            hoverinfo='x+y',
        ))

        fig.update_layout(
        template="plotly_dark",
        height=400, # Explicit height override
        paper_bgcolor="rgba(0,0,0,0)", # Transparent to let card bg show
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=TEXT_COLOR,
        margin=dict(l=20, r=20, t=20, b=20),
        hovermode="x unified",
        xaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor=BORDER_COLOR,
            showline=False
        ),
        yaxis=dict(
            showgrid=True, 
            gridwidth=1, 
            gridcolor=BORDER_COLOR,
            showline=False,
            showticklabels=False # Hide y-axis labels as values are in bubbles
        )
    )
        return fig

    @rx.var
    def state_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
            
        data = self.filtered_df.groupby("CUSTOMER STATE")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        if len(data) > 10:
            top_10 = data.head(10)
            others_val = data.iloc[10:]["Sales Amount"].sum()
            others = pd.DataFrame([{'CUSTOMER STATE': 'Other states', 'Sales Amount': others_val}])
            data = pd.concat([top_10, others], ignore_index=True)
            
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        # Sort for display
        data = data.sort_values("Sales Amount", ascending=True) 
        
        fig = px.treemap(
            data,
            path=["CUSTOMER STATE"],
            values="Sales Amount",
            color="CUSTOMER STATE",
            hover_data=['Sales Amount'],
            color_discrete_sequence=CHART_COLORS,
            color_discrete_map={"Other states": "#2D3748"}, # Dark Gray for "Other states"
            template="plotly_dark",
        )
        
        fig.update_traces(
            textinfo="label+value+percent entry",
            textfont=dict(size=14, color="white"),
            marker=dict(line=dict(width=1, color='white')),
            textposition="middle center"
        )
        
        fig.update_layout(
            height=580, # Explicit height override
            paper_bgcolor=CARD_BG,
            plot_bgcolor=CARD_BG,
            font_color=TEXT_COLOR,
            margin=dict(l=0, r=0, t=0, b=0), # Edge to Edge
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor="#4A5568")
        return fig

    @rx.var
    def product_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
            
        data = self.filtered_df.groupby("Product")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        if len(data) > 5:
            top_5 = data.head(5)
            others_val = data.iloc[5:]["Sales Amount"].sum()
            others = pd.DataFrame([{'Product': 'Other', 'Sales Amount': others_val}])
            data = pd.concat([top_5, others], ignore_index=True)
            
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        
        # Calculate Total for Center Text
        total_sales_val = data["Sales Amount"].sum()
        
        fig = px.pie(
            data,
            names="Product",
            values="Sales Amount",
            template="plotly_dark",
            hole=0.5 # Increased hole size for text
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            sort=True, 
            direction='clockwise'
        )
        fig.update_layout(
            height=580, # Explicit height override
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            annotations=[dict(text=f"Total Sales<br>{total_sales_val:.2f} Cr", x=0.5, y=0.5, font_size=16, showarrow=False, font_weight="bold", font_color="white")]
        )
        return fig

    @rx.var
    def supply_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty or "TYPE OF SUPPLY" not in self.filtered_df.columns:
            return go.Figure()
            
        data = self.filtered_df.groupby("TYPE OF SUPPLY")["Sales Amount"].sum().reset_index()
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        
        # Calculate Total for Center Text
        total_sales_val = data["Sales Amount"].sum()
        
        fig = px.pie(
            data,
            names="TYPE OF SUPPLY",
            values="Sales Amount",
            template="plotly_dark",
            hole=0.5 # Match Product chart
        )
        fig.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            texttemplate='%{percent}<br>(%{value:.2f} Cr)',
            sort=True
        )
        fig.update_layout(
            height=580, # Explicit height override
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font_color=TEXT_COLOR,
            margin=dict(l=20, r=20, t=20, b=20),
            showlegend=True,
            annotations=[dict(text=f"Total Sales<br>{total_sales_val:.2f} Cr", x=0.5, y=0.5, font_size=16, showarrow=False, font_weight="bold", font_color="white")]
        )
        return fig

    # --- Channel Chart Logic (moved from component/chart snippet if existed, 
    # but seems it was using state var `channel_sales_chart` which was missing in original file view?
    # I saw `State.channel_sales_chart` in `channel_sales_card` text.
    # I'll implement it here assuming it follows similar pattern.
    
    @rx.var
    def channel_sales_chart(self) -> go.Figure:
        if self.filtered_df.empty:
            return go.Figure()
            
        data = self.filtered_df.groupby("Channel")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        
        data["Sales Amount"] = (data["Sales Amount"] / 10000000).round(2)
        total_val = data["Sales Amount"].sum()
        
        fig = px.pie(
            data,
            names="Channel",
            values="Sales Amount",
            template="plotly_dark",
            hole=0.7,
            color_discrete_sequence=CHART_COLORS
        )
        
        fig.update_traces(
            textinfo='none', # Hide labels on chart, use legend
            hoverinfo='label+value+percent'
        )
        
        fig.update_layout(
            height=580,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color=TEXT_COLOR,
            margin=dict(l=0, r=0, t=0, b=0),
            showlegend=False, # Custom legend used
             annotations=[dict(text=f"Total Sales<br>{total_val:.2f} Cr", x=0.5, y=0.5, font_size=20, showarrow=False, font_weight="bold", font_color="white")]
        )
        return fig
        
    @rx.var
    def channel_sales_stats(self) -> list[dict]:
        if self.filtered_df.empty:
            return []
            
        data = self.filtered_df.groupby("Channel")["Sales Amount"].sum().reset_index()
        data = data.sort_values("Sales Amount", ascending=False)
        total = data["Sales Amount"].sum()
        
        results = []
        for i, row in enumerate(data.to_dict('records')):
            val = row["Sales Amount"]
            pct = val / total * 100 if total > 0 else 0
            results.append({
                "channel": row["Channel"],
                "value": f"₹{val/10000000:.2f} Cr",
                "pct": f"{pct:.1f}%",
                "color": CHART_COLORS[i % len(CHART_COLORS)]
            })
        return results
