import pandas as pd
from sqlalchemy import text
from sales_app.db import engine


# ===============================
# TABLE CREATION
# ===============================
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
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS uploads_log (
            id SERIAL PRIMARY KEY,
            month_label TEXT,
            data_type TEXT,
            uploaded_at TIMESTAMP DEFAULT NOW()
        )
        """))

        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS targets (
            id SERIAL PRIMARY KEY,
            month_label TEXT UNIQUE,
            target_amount NUMERIC(12,2),
            created_at TIMESTAMP DEFAULT NOW()
        )
        """))


# ===============================
# INSERT SALES DATA
# ===============================
def insert_sales_dataframe(df, year, month, month_label, data_type):
    rows_inserted = 0

    with engine.begin() as conn:
        for _, row in df.iterrows():
            conn.execute(
                text("""
                INSERT INTO sales_data
                (sale_date, branch, amount, month_label, data_type)
                VALUES (:date, :branch, :amount, :month, :type)
                """),
                {
                    "date": row["date"],
                    "branch": row["branch"],
                    "amount": float(row["amount"]),
                    "month": month_label,
                    "type": data_type,
                }
            )
            rows_inserted += 1

    return rows_inserted


# ===============================
# LOAD HISTORICAL DATA (DB ONLY)
# ===============================
def load_historical_dataframes():
    query = """
    SELECT sale_date, branch, amount, month_label
    FROM sales_data
    WHERE data_type = 'historical'
    ORDER BY sale_date
    """

    df = pd.read_sql(text(query), engine)

    historical_dfs = {}
    weekday_maps = {}

    if df.empty:
        return historical_dfs, weekday_maps

    for month_label, mdf in df.groupby("month_label"):
        mdf = mdf.copy()
        mdf["sale_date"] = pd.to_datetime(mdf["sale_date"])
        mdf["weekday"] = mdf["sale_date"].dt.weekday
        historical_dfs[month_label] = mdf
        weekday_maps[month_label] = dict(
            zip(mdf["sale_date"].dt.date, mdf["weekday"])
        )

    return historical_dfs, weekday_maps


# ===============================
# LOAD CURRENT MONTH (DB ONLY)
# ===============================
def load_current_month_dataframe():
    query = """
    SELECT sale_date, branch, amount, month_label
    FROM sales_data
    WHERE data_type = 'current'
    ORDER BY sale_date
    """

    df = pd.read_sql(text(query), engine)

    if df.empty:
        return None, None

    df["sale_date"] = pd.to_datetime(df["sale_date"])
    current_month = df["month_label"].iloc[0]

    return current_month, df
