import pandas as pd


class ExcelLoader:
    """
    Excel loader for DB-backed sales system.

    Expected Excel format:
    - Column A: Branch name
    - Column B onward: Day numbers (1, 2, 3, ...)
    - May contain a TOTAL row (will be removed)
    - '-' or empty cells are treated as 0
    """

    @staticmethod
    def load_file(file_path):
        try:
            df = pd.read_excel(file_path, engine="openpyxl")

            if df.empty:
                return None, "Excel file is empty", None

            # Drop fully empty columns
            df = df.dropna(axis=1, how="all")

            # First column = branch
            branch_col = df.columns[0]

            # Remove TOTAL rows (case-insensitive)
            df = df[
                df[branch_col]
                .astype(str)
                .str.strip()
                .str.upper()
                != "TOTAL"
            ]

            if df.empty:
                return None, "No data rows found after removing TOTAL", None

            # Replace '-' and NaN with 0
            df = df.replace("-", 0)
            df = df.fillna(0)

            # Convert all day columns to numeric
            for col in df.columns[1:]:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

            # Ensure branch column is clean string
            df[branch_col] = df[branch_col].astype(str).str.strip()

            # DB pipeline does NOT require weekday_map anymore
            weekday_map = {}

            return df, None, weekday_map

        except Exception as e:
            return None, str(e), None
