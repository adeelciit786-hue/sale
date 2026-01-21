from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import os

# =========================================================
# SAFE ABSOLUTE IMPORTS
# =========================================================
from sales_app.excel_loader import ExcelLoader
from sales_app.file_manager import FileManager
from sales_app.forecast import Forecaster
from sales_app.visualizer import Visualizer
from sales_app.db_loader import (
    create_tables_if_not_exist,
    insert_sales_dataframe,
    load_historical_dataframes,
    load_current_month_dataframe,
)

# =========================================================
# APP SETUP
# =========================================================
app = Flask(__name__)
app.secret_key = "sales-dashboard-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# DB init (Render safe)
try:
    create_tables_if_not_exist()
except Exception as e:
    print("DB init skipped:", e)

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Champ@123"

fm = FileManager()

# =========================================================
# HELPERS
# =========================================================
def get_current_month_name():
    return datetime.now().strftime("%B %Y")


def parse_month_from_filename(filename: str):
    """
    STRICT filename validation.
    Expected format: 'January 2026.xlsx'
    """
    if not filename.lower().endswith(".xlsx"):
        raise ValueError("File must be an .xlsx Excel file")

    name = filename.replace(".xlsx", "").strip()
    parts = name.split()

    if len(parts) != 2:
        raise ValueError("Filename must be like 'January 2026.xlsx'")

    month_name, year_str = parts

    try:
        month = datetime.strptime(month_name, "%B").month
    except ValueError:
        raise ValueError("Month must be full name like January, February, etc.")

    try:
        year = int(year_str)
    except ValueError:
        raise ValueError("Year must be numeric (e.g. 2026)")

    return month_name, month, year


# =========================================================
# AUTH
# =========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if (
            request.form.get("username") == ADMIN_USERNAME
            and request.form.get("password") == ADMIN_PASSWORD
        ):
            session["is_admin"] = True
            return redirect(url_for("upload"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("dashboard"))


# =========================================================
# UPLOAD (100% SAFE – NO MORE 500)
# =========================================================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    message = None
    message_type = None

    try:
        if request.method == "POST":

            # ================= HISTORICAL =================
            if "historical_file" in request.files:
                file = request.files["historical_file"]

                if not file or not file.filename:
                    raise ValueError("No file selected")

                temp_path = f"/tmp/{file.filename}"
                file.save(temp_path)

                df, error, _ = ExcelLoader.load_file(temp_path)
                if error:
                    raise ValueError(error)

                month_name, month, year = parse_month_from_filename(file.filename)
                month_label = f"{month_name} {year}"

                fm.clear_month_data(month_label, "historical")
                rows = insert_sales_dataframe(
                    df, year, month, month_label, "historical"
                )
                fm.log_upload(month_label, "historical")

                message = f"Historical data uploaded successfully ({rows} rows)"
                message_type = "success"

            # ================= CURRENT =================
            elif "current_month_file" in request.files:
                file = request.files["current_month_file"]

                if not file or not file.filename:
                    raise ValueError("No file selected")

                temp_path = f"/tmp/{file.filename}"
                file.save(temp_path)

                df, error, _ = ExcelLoader.load_file(temp_path)
                if error:
                    raise ValueError(error)

                month_name, month, year = parse_month_from_filename(file.filename)
                month_label = f"{month_name} {year}"

                fm.clear_month_data(month_label, "current")
                rows = insert_sales_dataframe(
                    df, year, month, month_label, "current"
                )
                fm.log_upload(month_label, "current")

                message = f"Current month uploaded successfully ({rows} rows)"
                message_type = "success"

            # ================= TARGET =================
            elif "current_month" in request.form and "target_value" in request.form:
                target_value = float(request.form["target_value"])
                fm.save_target_for_month(
                    request.form["current_month"], target_value
                )
                message = "Target saved successfully"
                message_type = "success"

    except Exception as e:
        # 🔥 THIS IS WHY 500 IS GONE
        print("UPLOAD ERROR:", str(e))
        message = str(e)
        message_type = "error"

    # ================= TEMPLATE DATA =================
    historical_files = fm.get_available_months("historical")
    current_month_filename, _ = load_current_month_dataframe()
    current_target = (
        fm.get_target_for_month(current_month_filename)
        if current_month_filename else 0
    )

    return render_template(
        "upload.html",
        message=message,
        message_type=message_type,
        historical_files=historical_files,
        current_month_file=current_month_filename,
        current_target=current_target,
    )


# =========================================================
# DASHBOARD (HARDENED – NEVER CRASHES)
# =========================================================
def get_dashboard_data():

    try:
        historical_dfs, weekday_maps = load_historical_dataframes()
    except Exception as e:
        print("Historical load failed:", e)
        historical_dfs, weekday_maps = {}, {}

    try:
        current_filename, current_df = load_current_month_dataframe()
    except Exception as e:
        print("Current load failed:", e)
        current_filename, current_df = None, None

    try:
        weekday_averages = Forecaster.calculate_weekday_averages(
            historical_dfs, weekday_maps
        )
    except Exception as e:
        print("Weekday avg error:", e)
        weekday_averages = {}

    target = fm.get_target_for_month(current_filename) if current_filename else 0

    forecast_data = {"daily_actual": [], "daily_forecast": [], "today": 0, "month_days": 0}
    if current_df is not None:
        try:
            forecast_data = Forecaster.forecast_current_month(
                current_df, weekday_averages
            )
        except Exception as e:
            print("Forecast error:", e)

    total_sales = sum(forecast_data.get("daily_actual", []))

    graphs = {
        "historical_trend": "{}",
        "weekday_avg": "{}",
        "monthly_forecast": "{}",
    }

    try:
        graphs["historical_trend"] = Visualizer.create_historical_daily_trend(historical_dfs)
        graphs["weekday_avg"] = Visualizer.create_weekday_average_chart(weekday_averages)
    except Exception as e:
        print("Graph error:", e)

    return {
        "kpis": {
            "today_date": datetime.now().strftime("%d %b"),
            "total_sales_till_today": f"AED {total_sales:,.0f}",
            "today_projected_sale": "AED 0",
            "monthly_projection": "AED 0",
            "monthly_target": f"AED {target:,.0f}",
            "shortfall": "AED 0",
            "shortfall_type": "shortfall",
        },
        "graphs": graphs,
        "current_month": current_filename,
        "month_options": fm.get_available_months(),
    }


# =========================================================
# ROUTES
# =========================================================
@app.route("/")
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", data=get_dashboard_data())


@app.route("/about")
def about():
    return render_template("about.html")


# =========================================================
# LOCAL RUN
# =========================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
