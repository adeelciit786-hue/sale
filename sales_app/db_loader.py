import pandas as pd
from sqlalchemy import create_engine, text
import os

# =========================================================
# DATABASE CONFIG
# =========================================================
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
)

# =========================================================
# CREATE TABLES (SAFE & BACKWARD COMPATIBLE)
# =========================================================
def create_tables_if_not_exist():
    with engine.begin() as conn:

        # Ensure sales_data table with branch
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sales_data (
                id SERIAL PRIMARY KEY,
                sale_date DATE NOT NULL,
                branch TEXT NOT NULL,
                amount NUMERIC NOT NULL,
                month_label TEXT NOT NULL,
                data_type TEXT NOT NULL
            );
        """))

        # Ensure branch column exists (for older DBs)
        conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'sales_data'
                    AND column_name = 'branch'
                ) THEN
                    ALTER TABLE sales_data
                    ADD COLUMN branch TEXT NOT NULL DEFAULT 'ALL';
                END IF;
            END$$;
        """))

        # Monthly targets
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS monthly_targets (
                month_label TEXT PRIMARY KEY,
                target NUMERIC NOT NULL
            );
        """))

# =========================================================
# INSERT DATAFRAME (FIXED & STABLE)
# =========================================================
def insert_sales_dataframe(df, year, month, month_label, data_type, branch="ALL"):
    """
    Aggregates daily totals and inserts them with a fixed branch.
    """
    rows = []

    for day_idx, col in enumerate(df.columns[1:], start=1):
        sale_date = pd.to_datetime(
            f"{year}-{month:02d}-{day_idx}",
            errors="coerce"
        )

        if pd.isna(sale_date):
            continue

        total_amount = df[col].sum()

        rows.append({
            "sale_date": sale_date.date(),
            "branch": branch,            # ✅ FIX
            "amount": float(total_amount),
            "month_label": month_label,
            "data_type": data_type,
        })

    if not rows:
        return 0

    pd.DataFrame(rows).to_sql(
        "sales_data",
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    return len(rows)

# =========================================================
# LOAD HISTORICAL DATA
# =========================================================
def load_historical_dataframes():
    query = """
        SELECT sale_date, amount, month_label
        FROM sales_data
        WHERE data_type = 'historical'
        ORDER BY sale_date;
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {}, {}

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df = df.dropna(subset=["sale_date"])

    historical_dfs = {}
    weekday_maps = {}

    for month, month_df in df.groupby("month_label"):
        month_df = month_df.copy()
        month_df["sale_date"] = pd.to_datetime(month_df["sale_date"], errors="coerce")
        month_df = month_df.dropna(subset=["sale_date"])

        if month_df.empty:
            continue

        pivot = month_df.pivot_table(
            values="amount",
            columns=month_df["sale_date"].dt.day,
            aggfunc="sum",
            fill_value=0,
        )

        historical_dfs[month] = pivot

        weekday_maps[month] = {
            day: month_df.loc[
                month_df["sale_date"].dt.day == day,
                "sale_date"
            ].iloc[0].strftime("%a").upper()
            for day in pivot.columns
        }

    return historical_dfs, weekday_maps

# =========================================================
# LOAD CURRENT MONTH
# =========================================================
def load_current_month_dataframe():
    query = """
        SELECT sale_date, amount, month_label
        FROM sales_data
        WHERE data_type = 'current'
        ORDER BY sale_date;
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return None, None

    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df = df.dropna(subset=["sale_date"])

    if df.empty:
        return None, None

    month_label = df["month_label"].iloc[0]

    pivot = df.pivot_table(
        values="amount",
        columns=df["sale_date"].dt.day,
        aggfunc="sum",
        fill_value=0,
    )

    return month_label, pivot
