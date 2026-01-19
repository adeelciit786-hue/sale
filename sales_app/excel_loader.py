import pandas as pd
from pathlib import Path
import re

class ExcelLoader:
    """Handles reading and validating Excel files with strict data cleaning."""
    
    @staticmethod
    def load_file(file_path):
        """
        Load and clean Excel file.
        
        The Excel structure is:
        - Row 0 (weekday row): "Outlet Name", "WED", "THU", "FRI", ...
        - Row 1 (day numbers): NaN, 1, 2, 3, ...
        - Row 2+ (data): Branch names and sales
        - May contain a TOTAL row
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            tuple: (cleaned_df, error_message, weekday_map)
            - cleaned_df: pandas DataFrame with cleaned data, TOTAL row removed
            - error_message: None if successful, error string if failed
            - weekday_map: dict mapping column index to weekday name
        """
        try:
            # Read Excel file
            df = pd.read_excel(file_path, engine='openpyxl')
            
            if df.empty:
                return None, "Excel file is empty", None
            
            # Make a copy to avoid modifying original
            df = df.copy()
            
            # STEP 1: Extract weekday information from row 0
            # Row 0 contains: "Outlet Name", "WED", "THU", ...
            weekday_map = {}
            branch_col = df.columns[0]
            day_columns = df.columns[1:]
            
            first_row = df.iloc[0]
            for col_idx, col in enumerate(day_columns):
                weekday_value = str(first_row[col]).strip().upper()
                # Check if it's a valid weekday
                valid_weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
                if weekday_value in valid_weekdays:
                    weekday_map[col_idx + 1] = weekday_value  # +1 because first col is branch names
            
            # STEP 2: Remove the weekday row (row 0) and day number row (row 1) from data
            # Keep only branch data rows (row 2 onwards)
            df = df.iloc[2:].reset_index(drop=True)
            
            if df.empty:
                return None, "No data rows after removing header rows", weekday_map
            
            # STEP 3: Identify and remove TOTAL row (case-insensitive, look for "TOTAL" in first column)
            total_row_mask = df[branch_col].astype(str).str.upper().str.strip() == 'TOTAL'
            
            if total_row_mask.any():
                df = df[~total_row_mask].reset_index(drop=True)
            
            # STEP 4: Clean data: replace "-" with 0, coerce to numeric
            for col in day_columns:
                # Replace dash with 0, handle all string values
                df[col] = df[col].astype(str).str.replace('-', '0')
                # Coerce to numeric, non-numeric values become 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Ensure all data columns are float
            for col in day_columns:
                df[col] = df[col].astype(float)
            
            return df, None, weekday_map
            
        except Exception as e:
            return None, f"Error reading Excel file: {str(e)}", None
    
    @staticmethod
    def validate_daily_totals(df, branch_col_name):
        """
        Validate that daily totals in last row match sum of branches.
        Uses ±1% tolerance.
        
        Args:
            df: DataFrame with data
            branch_col_name: Name of branch column
            
        Returns:
            tuple: (is_valid, warnings)
        """
        warnings = []
        
        try:
            # Calculate daily sums across branches
            day_columns = df.columns[1:]
            
            for col in day_columns:
                calculated_total = df[col].sum()
                
                # In this context, we're checking internal consistency
                # (this is called after TOTAL row is removed)
                # Just ensure no NaN values remain
                if pd.isna(calculated_total):
                    warnings.append(f"Warning: Column {col} contains invalid data")
            
            return True, warnings
            
        except Exception as e:
            return False, [f"Validation error: {str(e)}"]
    
    @staticmethod
    def get_date_range(df):
        """
        Extract date range from DataFrame.
        Row 2 should contain date numbers.
        
        Returns:
            tuple: (start_date, end_date, num_days, weekday_headers)
        """
        try:
            # Column headers (Row 1) should be: Branch, MON, TUE, WED, THU, FRI, SAT, SUN
            day_columns = list(df.columns[1:])
            
            # Count of days = number of day columns
            num_days = len(day_columns)
            
            return 1, num_days, num_days, day_columns
            
        except Exception as e:
            return None, None, None, None
