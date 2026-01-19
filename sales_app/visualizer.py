import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

class Visualizer:
    """Creates all required graphs using Plotly."""
    
    @staticmethod
    def create_historical_daily_trend(historical_dfs):
        """
        Graph 1: Historical Daily Sales Trend
        Line chart - combined daily totals across ALL historical months
        
        Returns:
            str: JSON representation of Plotly figure
        """
        try:
            fig = go.Figure()
            
            if not historical_dfs:
                fig.add_trace(go.Scatter(x=[], y=[], mode='lines'))
                fig.update_layout(title="Daily Sales Trend – Historical Analysis")
                return fig.to_json()
            
            # Combine all historical data
            all_daily_totals = {}
            
            for filename, df in historical_dfs.items():
                if df is None or df.empty:
                    continue
                
                day_columns = list(df.columns[1:])
                
                for day_idx, col in enumerate(day_columns):
                    day_num = day_idx + 1
                    total = float(df[col].sum())
                    
                    if day_num not in all_daily_totals:
                        all_daily_totals[day_num] = []
                    all_daily_totals[day_num].append(total)
            
            # Calculate average for each day across all months
            days = sorted(all_daily_totals.keys())
            avg_sales = [sum(all_daily_totals[day]) / len(all_daily_totals[day]) 
                        for day in days]
            
            fig.add_trace(go.Scatter(
                x=days,
                y=avg_sales,
                mode='lines+markers',
                name='Daily Sales',
                line=dict(color='#2E7D32', width=2),
                marker=dict(size=6)
            ))
            
            fig.update_layout(
                title="Daily Sales Trend – Historical Analysis",
                xaxis_title="Day of Month",
                yaxis_title="Sales (AED)",
                hovermode='x unified',
                template='plotly_white',
                height=400,
                dragmode='pan'
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error creating historical trend: {e}")
            return json.dumps({})
    
    @staticmethod
    def create_weekday_average_chart(weekday_averages):
        """
        Graph 2: Average Sales by Weekday
        Bar chart with value labels
        
        Returns:
            str: JSON representation of Plotly figure
        """
        try:
            weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
            values = [weekday_averages.get(day, 0) for day in weekdays]
            
            fig = go.Figure(data=[
                go.Bar(
                    x=weekdays,
                    y=values,
                    text=[f'AED {v:,.0f}' for v in values],
                    textposition='auto',
                    marker=dict(color='#2E7D32'),
                    name='Average Sales'
                )
            ])
            
            fig.update_layout(
                title="Average Sales by Weekday (Historical Analysis)",
                xaxis_title="Day of Week",
                yaxis_title="Average Sales (AED)",
                showlegend=False,
                template='plotly_white',
                height=400
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error creating weekday chart: {e}")
            return json.dumps({})
    
    @staticmethod
    def create_monthly_forecast(daily_actual, daily_projected, simple_daily_target, today, month_name):
        """
        Graph 3: Sales Projection – Current Month
        
        Shows:
        1. Solid line: Actual daily sales (completed days only)
        2. Dashed line: Projected daily sales (weekday-weighted, varies by weekday)
        3. Dotted line: Simple daily target reference (target ÷ days)
        4. Vertical marker: TODAY
        
        Business Logic:
        - Actual: Sum of daily totals from current month Excel (TOTAL row excluded)
        - Projected: Weekday-weighted projection normalized to hit remaining target exactly
        - Simple Daily Target: Monthly Target ÷ Total days (reference line only)
        
        Weekday-Weighted Logic:
        - Sundays are lower (weight < 1)
        - Thu/Fri/Sat are higher (weight > 1)
        - Total projection = Remaining Target (hits target exactly)
        
        Returns:
            str: JSON representation of Plotly figure
        """
        try:
            days = list(range(1, len(daily_actual) + 1))
            
            fig = go.Figure()
            
            # Actual sales (completed days only)
            actual_mask = [day < today for day in days]
            actual_days = [d for d, m in zip(days, actual_mask) if m]
            actual_values = [daily_actual[i] for i, m in enumerate(actual_mask) if m]
            
            fig.add_trace(go.Scatter(
                x=actual_days,
                y=actual_values,
                mode='lines+markers',
                name='Actual Sales',
                line=dict(color='#2E7D32', width=2),
                marker=dict(size=4)
            ))
            
            # Projected Sales (from today onwards) - dashed line, weekday-weighted
            projected_mask = [day >= today for day in days]
            projected_days = [d for d, m in zip(days, projected_mask) if m]
            projected_values = [daily_projected[i] for i, m in enumerate(projected_mask) if m]
            
            if projected_values:
                fig.add_trace(go.Scatter(
                    x=projected_days,
                    y=projected_values,
                    mode='lines+markers',
                    name='Projected Sales',
                    line=dict(color='#A31D3C', width=2, dash='dash'),
                    marker=dict(size=4)
                ))
            
            # Simple Daily Target (reference line) - dotted horizontal line
            if simple_daily_target > 0:
                fig.add_hline(
                    y=simple_daily_target,
                    line_dash="dot",
                    line_color="#FF6B6B",
                    annotation_text=f"Simple Daily Target: AED {simple_daily_target:,.0f}",
                    annotation_position="right"
                )
            
            # Add vertical line at today
            fig.add_vline(x=today, line_dash="dot", line_color="gray",
                         annotation_text="Today", annotation_position="top right")
            
            fig.update_layout(
                title=f"Sales Projection – {month_name}",
                xaxis_title="Day of Month",
                yaxis_title="Sales (AED)",
                hovermode='x unified',
                template='plotly_white',
                height=400,
                dragmode='pan'
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error creating forecast chart: {e}")
            return json.dumps({})
    
    @staticmethod
    def create_cumulative_vs_target(cumulative_forecast, cumulative_target):
        """
        Graph 4: Cumulative Projection vs Target
        Area + line chart
        
        Returns:
            str: JSON representation of Plotly figure
        """
        try:
            days = list(range(1, len(cumulative_forecast) + 1))
            
            fig = go.Figure()
            
            # Cumulative forecast (green area)
            fig.add_trace(go.Scatter(
                x=days,
                y=cumulative_forecast,
                fill='tozeroy',
                name='Cumulative Actual + Forecast',
                line=dict(color='#2E7D32', width=2),
                fillcolor='rgba(46, 125, 50, 0.3)'
            ))
            
            # Cumulative target (red dashed line)
            fig.add_trace(go.Scatter(
                x=days,
                y=cumulative_target,
                mode='lines',
                name='Cumulative Target',
                line=dict(color='#A31D3C', width=2, dash='dash')
            ))
            
            fig.update_layout(
                title="Projected Monthly Sales vs Target",
                xaxis_title="Day of Month",
                yaxis_title="Cumulative Sales (AED)",
                hovermode='x unified',
                template='plotly_white',
                height=400,
                dragmode='pan'
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error creating cumulative chart: {e}")
            return json.dumps({})
    
    @staticmethod
    @staticmethod
    def create_actual_vs_required(daily_actual, daily_projected, today, month_days):
        """
        Graph 5: Projected Sales vs Actual Sales (Daily)
        Grouped bar chart showing side-by-side daily comparison
        
        FOR EACH DAY (1–31):
        - LEFT BAR  (RED):   Projected/Required Daily Sale (weekday-weighted, ALL days)
        - RIGHT BAR (GREEN): Actual Daily Sale (past days only)
        
        Business Logic:
        - Actual: Sum of daily totals from current month Excel (TOTAL row excluded)
        - Required: Weekday-weighted projection (same as Graph 3)
        - Grouping: True grouped bars with RED left, GREEN right per day
        
        Bar Positioning:
        - Both traces share same x-axis (day numbers)
        - Plotly barmode='group' handles LEFT/RIGHT placement
        - First trace (RED) = LEFT, Second trace (GREEN) = RIGHT
        
        Returns:
            str: JSON representation of Plotly figure
        """
        try:
            fig = go.Figure()
            
            # REQUIRED DAILY SALES - Red bars (ALL days with weekday-weighted projection)
            required_days = list(range(1, month_days + 1))
            required_vals = [daily_projected[i] if daily_projected[i] is not None else 0 for i in range(month_days)]
            
            fig.add_trace(go.Bar(
                x=required_days,
                y=required_vals,
                name='Projected Sales',
                marker=dict(color='#A31D3C'),
                text=[f"AED {v:,.0f}" if v > 0 else "" for v in required_vals],
                textposition='outside'
            ))
            
            # ACTUAL SALES - Green bars (past days & today only)
            actual_days = []
            actual_vals = []
            actual_texts = []
            
            for day_idx in range(month_days):
                if day_idx < today:  # Past days and today
                    actual_days.append(day_idx + 1)
                    actual_val = daily_actual[day_idx] if daily_actual[day_idx] is not None else 0
                    actual_vals.append(actual_val)
                    actual_texts.append(f"AED {actual_val:,.0f}" if actual_val > 0 else "")
            
            fig.add_trace(go.Bar(
                x=actual_days,
                y=actual_vals,
                name='Actual Sales',
                marker=dict(color='#2E7D32'),
                text=actual_texts,
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Projected Sales vs Actual Sales (Daily)",
                xaxis_title="Day of Month",
                yaxis_title="Sales (AED)",
                barmode='group',
                hovermode='x unified',
                template='plotly_white',
                height=450,
                margin=dict(t=100, b=80, l=60, r=60),
                dragmode='pan'
            )
            
            return fig.to_json()
            
        except Exception as e:
            print(f"Error creating actual vs required chart: {e}")
            return json.dumps({})
    
    @staticmethod
    def create_monthly_comparison(historical_dfs, month1, month2):
        """
        Graph 6: Monthly Sales Comparison
        Dual-line comparison with statistics
        
        Returns:
            tuple: (json_figure, stats_dict)
        """
        try:
            fig = go.Figure()
            
            stats = {'month1': None, 'month2': None, 'diff': 0, 'pct_change': 0}
            
            if not historical_dfs:
                return fig.to_json(), stats
            
            # Get data for month1
            m1_data = None
            m2_data = None
            
            for filename, df in historical_dfs.items():
                if month1 in filename:
                    m1_data = df
                if month2 in filename:
                    m2_data = df
            
            if m1_data is not None:
                days = list(range(1, len(m1_data.columns)))
                m1_totals = [float(m1_data.iloc[:, i+1].sum()) for i in range(len(m1_data.columns)-1)]
                m1_total = sum(m1_totals)
                
                fig.add_trace(go.Scatter(
                    x=days,
                    y=m1_totals,
                    mode='lines+markers',
                    name=month1,
                    line=dict(color='#2E7D32', width=2)
                ))
                
                stats['month1'] = m1_total
            
            if m2_data is not None:
                days = list(range(1, len(m2_data.columns)))
                m2_totals = [float(m2_data.iloc[:, i+1].sum()) for i in range(len(m2_data.columns)-1)]
                m2_total = sum(m2_totals)
                
                fig.add_trace(go.Scatter(
                    x=days,
                    y=m2_totals,
                    mode='lines+markers',
                    name=month2,
                    line=dict(color='#A31D3C', width=2)
                ))
                
                stats['month2'] = m2_total
            
            # Calculate differences
            if stats['month1'] and stats['month2']:
                stats['diff'] = stats['month2'] - stats['month1']
                stats['pct_change'] = (stats['diff'] / stats['month1']) * 100 if stats['month1'] > 0 else 0
            
            # Format stats for display
            stats['month1_formatted'] = f"AED {stats['month1']:,.0f}" if stats['month1'] else "N/A"
            stats['month2_formatted'] = f"AED {stats['month2']:,.0f}" if stats['month2'] else "N/A"
            stats['diff_formatted'] = f"AED {abs(stats['diff']):,.0f}" if stats['diff'] else "N/A"
            stats['pct_change_formatted'] = f"{stats['pct_change']:.1f}%" if stats['pct_change'] else "N/A"
            stats['diff_sign'] = 'positive' if stats['diff'] >= 0 else 'negative'
            stats['pct_sign'] = 'positive' if stats['pct_change'] >= 0 else 'negative'
            
            fig.update_layout(
                title="Monthly Sales Comparison",
                xaxis_title="Day of Month",
                yaxis_title="Daily Sales (AED)",
                hovermode='x unified',
                template='plotly_white',
                height=400,
                dragmode='pan'
            )
            
            return fig.to_json(), stats
            
        except Exception as e:
            print(f"Error creating comparison chart: {e}")
            return json.dumps({}), {}
