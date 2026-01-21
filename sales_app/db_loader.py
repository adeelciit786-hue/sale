import pandas as pd
from datetime import date
from sqlalchemy import text
from sales_app.db import engine


# =========================================================
# CREATE TABLES (SAFE TO RUN MULTIPLE TIMES)
# =========================================================
def create_tables_if_not_exist():
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales_data (
                id SERIAL PRIMARY KEY,
                sale_date DATE NOT NULL,
                branch TEXT NOT NULL,
                amount NUMERIC(12,2) NOT NULL,
                month_label TEXT NOT NULL,
                data_type TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS targets (
                id SERIAL PRIMARY KEY,
                month_label TEXT UNIQUE,
                target_amount NUMERIC(12,2),
                created_at TIMESTAMP DEFAULT NOW()
            );
        """))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS uploads_log (
                id SERIAL PRIMARY KEY,
                month_label TEXT,
                data_type TEXT,
                uploaded_at TIMESTAMP DEFAULT NOW()
            );
        """))


# =========================================================
# INSERT SALES DATA
# =========================================================
def insert_sales_dataframe(df, year, month, month_label, data_type):
    branch_col = df.columns[0]
    day_columns = df.columns[1:]

    records = []

    for day_index, col in enumerate(day_columns):
        sale_day = day_index + 1
        sale_date = date(year, month, sale_day)

        for _, row in df.iterrows():
            records.append({
                "sale_date": sale_date,
                "branch": str(row[branch_col]).strip(),
                "amount": float(row[col]),
                "month_label": month_label,
                "data_type": data_type
            })

    if not records:
        return 0

    pd.DataFrame(records).to_sql(
        "sales_data",
        engine,
        if_exists="append",
        index=False,
        chunksize=1000
    )

    return len(records)


# =========================================================
# LOAD HISTORICAL DATA (DB → DATAFRAMES)
# =========================================================
def load_historical_dataframes():
    query = """
        SELECT sale_date, branch, amount, month_label
        FROM sales_data
        WHERE data_type = 'historical'
        ORDER BY sale_date
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {}, {}

    historical_dfs = {}
    weekday_maps = {}

    for month_label, month_df in df.groupby("month_label"):
        pivot = month_df.pivot_table(
            index="branch",
            columns=month_df["sale_date"].dt.day,
            values="amount",
            aggfunc="sum",
            fill_value=0
        )

        historical_dfs[f"{month_label}.xlsx"] = pivot
        weekday_maps[f"{month_label}.xlsx"] = {
            d: month_df[month_df["sale_date"].dt.day == d]["sale_date"].dt.strftime("%a").iloc[0].upper()
            for d in pivot.columns
        }

    return historical_dfs, weekday_maps


# =========================================================
# LOAD CURRENT MONTH DATA
# =========================================================
def load_current_month_dataframe():
    query = """
        SELECT sale_date, branch, amount, month_label
        FROM sales_data
        WHERE data_type = 'current'
        ORDER BY sale_date
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return None, None

    month_label = df["month_label"].iloc[0]

    pivot = df.pivot_table(
        index="branch",
        columns=df["sale_date"].dt.day,
        values="amount",
        aggfunc="sum",
        fill_value=0
    )

    return f"{month_label}.xlsx", pivot
