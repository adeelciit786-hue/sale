import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Forecaster:
    """Implements weekday-based forecasting logic."""
    
    WEEKDAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    
    @staticmethod
    def calculate_weekday_averages(historical_dfs, weekday_maps=None):
        """
        Calculate average sales per weekday from historical data.
        
        CORRECT LOGIC:
        1. For EACH historical file:
           - Use the weekday mapping from the file
           - SUM sales across ALL branches for each day
           - Get the WEEKDAY for each day from the mapping
        2. Group daily totals by WEEKDAY (MON–SUN)
        3. For each weekday:
           - Compute AVERAGE of ONLY EXISTING daily totals
           - DO NOT divide by number of weeks or include missing days
        
        Args:
            historical_dfs: Dict of {filename: DataFrame}
            weekday_maps: Dict of {filename: {col_idx: weekday_name}}
                         Provides the correct weekday for each column
            
        Returns:
            dict: {weekday: average_sales} for MON-SUN
        """
        if not historical_dfs:
            return {day: 0 for day in Forecaster.WEEKDAYS}
        
        if weekday_maps is None:
            weekday_maps = {}
        
        try:
            # Store daily totals per weekday
            # Structure: {weekday: [daily_total_1, daily_total_2, ...]}
            weekday_daily_totals = {day: [] for day in Forecaster.WEEKDAYS}
            
            # Process each historical file
            for filename, df in historical_dfs.items():
                if df is None or df.empty:
                    continue
                
                # Get day columns (all columns except first which is branch names)
                day_columns = df.columns[1:]
                weekday_map_for_file = weekday_maps.get(filename, {})
                
                # For each day in this file
                for col_idx, col in enumerate(day_columns):
                    # Get the weekday for this column (1-indexed: col_idx + 1 because first col is branch names)
                    col_position = col_idx + 1
                    weekday = weekday_map_for_file.get(col_position)
                    
                    if weekday is None:
                        # No weekday mapping, skip this column
                        continue
                    
                    # SUM across ALL branches for this day (not average per branch)
                    daily_total = float(df[col].sum())
                    
                    # Store the daily total for this weekday
                    # Include all days with data
                    weekday_daily_totals[weekday].append(daily_total)
            
            # Calculate average of DAILY TOTALS per weekday
            # Average ONLY the existing daily totals, NOT padded with zeros
            averages = {}
            for day in Forecaster.WEEKDAYS:
                daily_totals = weekday_daily_totals[day]
                if daily_totals:
                    # Average of only existing daily totals
                    averages[day] = sum(daily_totals) / len(daily_totals)
                else:
                    # No data for this weekday
                    averages[day] = 0
            
            return averages
            
        except Exception as e:
            print(f"Error calculating weekday averages: {e}")
            return {day: 0 for day in Forecaster.WEEKDAYS}
    
    @staticmethod
    def get_current_day_of_month():
        """Get today's day of month (1-31)."""
        return datetime.now().day
    
    @staticmethod
    def forecast_current_month(current_df, weekday_averages, month_days=31):
        """
        Forecast current month sales.
        
        Args:
            current_df: Current month DataFrame (may have partial data)
            weekday_averages: Dict of weekday averages
            month_days: Total days in month
            
        Returns:
            dict: Forecasting results
        """
        try:
            today = Forecaster.get_current_day_of_month()
            day_columns = list(current_df.columns[1:])
            
            actual_sales = []
            forecast_sales = []
            
            # For each day in the month
            for day_idx in range(len(day_columns)):
                if day_idx < len(day_columns):
                    col = day_columns[day_idx]
                    day_num = day_idx + 1
                    
                    # Get actual sales total across all branches
                    if current_df[col].notna().any():
                        actual_total = float(current_df[col].sum())
                        actual_sales.append(actual_total)
                        forecast_sales.append(actual_total)
                    else:
                        # No data for this day
                        actual_sales.append(0)
                        
                        # Use weekday forecast for future days
                        weekday_idx = day_idx % 7
                        weekday = Forecaster.WEEKDAYS[weekday_idx]
                        forecast_value = weekday_averages.get(weekday, 0)
                        forecast_sales.append(forecast_value)
            
            # Calculate projections
            actual_total = sum(actual_sales)
            forecast_total = sum(forecast_sales)
            
            # Daily breakdown
            daily_actual = actual_sales
            daily_forecast = forecast_sales
            
            return {
                'actual_total': actual_total,
                'projected_total': forecast_total,
                'daily_actual': daily_actual,
                'daily_forecast': daily_forecast,
                'today': today,
                'month_days': month_days,
                'today_projected_sale': 0  # Will be calculated separately with target
            }
            
        except Exception as e:
            print(f"Error forecasting current month: {e}")
            return {
                'actual_total': 0,
                'projected_total': 0,
                'daily_actual': [],
                'daily_forecast': [],
                'today': 1,
                'month_days': 31,
                'today_projected_sale': 0
            }

    
    @staticmethod
    def calculate_kpi_today_projected_sale(actual_sales_list, monthly_target, today_day, month_days):
        """
        Calculate TODAY'S PROJECTED SALE using required daily pace logic.
        
        Logic:
        1. Calculate total actual sales up to YESTERDAY
        2. Calculate remaining days after today
        3. Calculate required daily sales to hit target
        
        Args:
            actual_sales_list: List of daily actual sales [day1, day2, ...]
            monthly_target: Target revenue in AED
            today_day: Current day of month (1-31)
            month_days: Total days in month
            
        Returns:
            float: Today's projected sale (required daily pace)
        """
        try:
            if today_day <= 1:
                # First day - full target divided by days
                return monthly_target / month_days if month_days > 0 else 0
            
            # Get actual sales up to YESTERDAY (completed days)
            completed_days = today_day - 1
            actual_up_to_yesterday = sum(actual_sales_list[:completed_days])
            
            # Remaining target
            remaining_target = max(0, monthly_target - actual_up_to_yesterday)
            
            # Remaining days starting from today
            remaining_days = month_days - completed_days
            
            if remaining_days <= 0:
                return 0
            
            # Required daily sale today
            today_projected = remaining_target / remaining_days
            
            return today_projected
            
        except Exception as e:
            print(f"Error calculating today's projected sale: {e}")
            return 0
    
    @staticmethod
    def calculate_kpi_monthly_projection(actual_sales_list, today_day, month_days):
        """
        Calculate MONTHLY PROJECTION using run-rate logic (based on ACTUAL sales only).
        
        Logic:
        1. Sum all actual sales up to TODAY
        2. Calculate average daily sales so far
        3. Project to end of month
        
        Args:
            actual_sales_list: List of daily actual sales [day1, day2, ...]
            today_day: Current day of month (1-31)
            month_days: Total days in month
            
        Returns:
            float: Projected monthly total
        """
        try:
            if today_day <= 0 or not actual_sales_list:
                return 0
            
            # Total actual sales completed including today
            completed_days = min(today_day, len(actual_sales_list))
            
            # If no actual sales yet, return 0
            if completed_days == 0:
                return 0
            
            actual_so_far = sum(actual_sales_list[:completed_days])
            
            # Avoid division by zero
            if actual_so_far == 0:
                return 0
            
            # Average daily sales
            avg_daily_sales = actual_so_far / completed_days
            
            # Project to end of month
            monthly_projection = avg_daily_sales * month_days
            
            return monthly_projection
            
        except Exception as e:
            print(f"Error calculating monthly projection: {e}")
            return 0
    
    @staticmethod
    def calculate_gap(projected_total, target):
        """Calculate gap between projection and target."""
        return projected_total - target
    
    @staticmethod
    def get_cumulative_series(daily_forecast, target, month_days):
        """
        Generate cumulative sales vs cumulative target series.
        
        Returns:
            tuple: (cumulative_actual_forecast, cumulative_target)
        """
        try:
            daily_target = target / month_days if month_days > 0 else 0
            
            cumulative_forecast = []
            cumulative_target = []
            
            for day_idx, sales in enumerate(daily_forecast):
                cumulative_forecast.append(sum(daily_forecast[:day_idx + 1]))
                cumulative_target.append(daily_target * (day_idx + 1))
            
            return cumulative_forecast, cumulative_target
            
        except Exception as e:
            print(f"Error calculating cumulative series: {e}")
            return [], []
    
    @staticmethod
    def get_required_daily_sales(target, remaining_days):
        """Calculate required daily sales to hit target."""
        if remaining_days <= 0:
            return 0
        return target / remaining_days
    
    @staticmethod
    def calculate_graph3_projections(actual_sales_list, monthly_target, today_day, month_days, weekday_averages):
        """
        Calculate Graph 3 projection lines: Weekday-weighted projection.
        
        Graph 3 MUST show:
        1. Actual daily sales (completed days only) - solid line
        2. Projected sales for remaining days - dashed line, WEEKDAY-WEIGHTED
        3. Simple Daily Target reference line - dotted line
        
        WEEKDAY-WEIGHTED LOGIC:
        - Calculate weekday weights from historical averages
        - For remaining days, apply weekday weights
        - Normalize so total projection = remaining target
        
        This ensures:
        - Sundays are lower, Thu/Fri/Sat are higher
        - TOTAL MONTH HITS TARGET EXACTLY
        
        Args:
            actual_sales_list: List of daily actual sales [day1, day2, ...]
            monthly_target: Monthly target in AED
            today_day: Current day of month (1-31)
            month_days: Total days in month (e.g., 31)
            weekday_averages: Dict of {weekday: average_daily_sales}
            
        Returns:
            dict with keys:
                - 'daily_projected': list of weekday-weighted projections (only for today onwards)
                - 'simple_daily_target': float (reference line value)
        """
        try:
            # Simple Daily Target reference: monthly target / month days
            simple_daily_target = monthly_target / month_days if month_days > 0 else 0
            
            # Calculate remaining target
            completed_days = today_day - 1
            actual_up_to_yesterday = sum(actual_sales_list[:completed_days])
            remaining_target = max(0, monthly_target - actual_up_to_yesterday)
            
            # Calculate weekday weights from historical averages
            # Weight = Weekday Average ÷ Average of all weekday averages
            if not weekday_averages or all(v == 0 for v in weekday_averages.values()):
                # Fallback: use flat daily target if no historical data
                flat_daily = remaining_target / (month_days - completed_days) if (month_days - completed_days) > 0 else 0
                daily_projected = [None] * month_days
                for day_idx in range(completed_days, month_days):
                    daily_projected[day_idx] = flat_daily
                return {
                    'daily_projected': daily_projected,
                    'simple_daily_target': simple_daily_target
                }
            
            # Calculate average of all weekday averages
            avg_of_averages = sum(weekday_averages.values()) / len(weekday_averages)
            
            if avg_of_averages == 0:
                # Fallback: use flat daily target
                flat_daily = remaining_target / (month_days - completed_days) if (month_days - completed_days) > 0 else 0
                daily_projected = [None] * month_days
                for day_idx in range(completed_days, month_days):
                    daily_projected[day_idx] = flat_daily
                return {
                    'daily_projected': daily_projected,
                    'simple_daily_target': simple_daily_target
                }
            
            # Calculate weights for each remaining day
            remaining_days = month_days - completed_days
            weights = []
            
            for day_idx in range(completed_days, month_days):
                # Determine weekday (day_idx 0 = Monday)
                weekday_idx = day_idx % 7
                weekday = Forecaster.WEEKDAYS[weekday_idx]
                
                # Weight = weekday average / avg of all averages
                weight = weekday_averages.get(weekday, 0) / avg_of_averages if avg_of_averages > 0 else 1.0
                weights.append(weight)
            
            # Normalize weights so they sum to remaining_target
            sum_weights = sum(weights) if weights else 1
            if sum_weights == 0:
                sum_weights = 1
            
            normalization_factor = remaining_target / sum_weights if sum_weights > 0 else 0
            
            # Build daily_projected list
            daily_projected = [None] * month_days
            for i, day_idx in enumerate(range(completed_days, month_days)):
                # Projected value = weight × normalization factor
                projected_value = weights[i] * normalization_factor
                daily_projected[day_idx] = projected_value
            
            return {
                'daily_projected': daily_projected,
                'simple_daily_target': simple_daily_target
            }
            
        except Exception as e:
            print(f"Error calculating graph3 weekday-weighted projections: {e}")
            return {
                'daily_projected': [],
                'simple_daily_target': 0
            }
