from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime
import traceback

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

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Champ@123"

# 🔒 Fixed logical branch (aggregated data)
BRANCH_NAME = "ALL"

fm = FileManager()

# =========================================================
# SAFE DB INIT (RENDER COLD START SAFE)
# =========================================================
try:
    create_tables_if_not_exist()
except Exception as e:
    print("DB init warning:", e)

# =========================================================
# HELPERS
# =========================================================
def parse_month_from_filename(filename):
    """
    Expected: January 2026.xlsx
    """
    name = filename.replace(".xlsx", "").strip()
    parts = name.split()
    if len(parts) != 2:
        raise ValueError("Filename must be like 'January 2026.xlsx'")

    month_name = parts[0]
    year = int(parts[1])
    month = datetime.strptime(month_name, "%B").month
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
# UPLOAD (STABLE & HARDENED)
# =========================================================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    message = None
    message_type = None

    try:
        if request.method == "POST":

            # ===============================
            # HISTORICAL UPLOAD
            # ===============================
            if "historical_files" in request.files:
                files = request.files.getlist("historical_files")

                if not files or not files[0].filename:
                    raise ValueError("No historical files selected")

                for file in files:
                    temp_path = f"/tmp/{file.filename}"
                    file.save(temp_path)

                    df, error, _ = ExcelLoader.load_file(temp_path)
                    if error:
                        raise ValueError(error)

                    month_name, month, year = parse_month_from_filename(file.filename)
                    month_label = f"{month_name} {year}"

                    fm.clear_month_data(month_label, "historical")

                    rows = insert_sales_dataframe(
                        df=df,
                        year=year,
                        month=month,
                        month_label=month_label,
                        data_type="historical",
                        branch=BRANCH_NAME,  # ✅ FIX
                    )

                    fm.log_upload(month_label, "historical")

                message = "Historical data uploaded successfully"
                message_type = "success"

            # ===============================
            # CURRENT MONTH UPLOAD
            # ===============================
            elif "current_month_file" in request.files:
                file = request.files["current_month_file"]
                if not file or not file.filename:
                    raise ValueError("No current month file selected")

                temp_path = f"/tmp/{file.filename}"
                file.save(temp_path)

                df, error, _ = ExcelLoader.load_file(temp_path)
                if error:
                    raise ValueError(error)

                month_name, month, year = parse_month_from_filename(file.filename)
                month_label = f"{month_name} {year}"

                fm.clear_month_data(month_label, "current")

                rows = insert_sales_dataframe(
                    df=df,
                    year=year,
                    month=month,
                    month_label=month_label,
                    data_type="current",
                    branch=BRANCH_NAME,  # ✅ FIX
                )

                fm.log_upload(month_label, "current")

                message = f"Current month uploaded successfully ({rows} rows)"
                message_type = "success"

            # ===============================
            # TARGET SAVE
            # ===============================
            elif "monthly_target" in request.form:
                target_value = float(request.form["monthly_target"])
                current_month = load_current_month_dataframe()[0]
                fm.save_target_for_month(current_month, target_value)

                message = "Target saved successfully"
                message_type = "success"

    except Exception as e:
        print("UPLOAD ERROR:")
        traceback.print_exc()
        message = str(e)
        message_type = "danger"

    # ===============================
    # SAFE TEMPLATE CONTEXT
    # ===============================
    historical_files = fm.get_available_months("historical") or []

    try:
        current_month_filename, _ = load_current_month_dataframe()
    except Exception:
        current_month_filename = None

    try:
        current_target = (
            fm.get_target_for_month(current_month_filename)
            if current_month_filename else 0
        )
    except Exception:
        current_target = 0

    return render_template(
        "upload.html",
        message=message,
        message_type=message_type,
        historical_files=historical_files,
        current_month_file=current_month_filename,
        current_target=current_target,
    )


# =========================================================
# DASHBOARD (UNCHANGED & SAFE)
# =========================================================
def get_dashboard_data():
    try:
        historical_dfs, weekday_maps = load_historical_dataframes()
    except Exception:
        historical_dfs, weekday_maps = {}, {}

    try:
        current_filename, current_df = load_current_month_dataframe()
    except Exception:
        current_filename, current_df = None, None

    try:
        weekday_averages = Forecaster.calculate_weekday_averages(
            historical_dfs, weekday_maps
        )
    except Exception:
        weekday_averages = {}

    target = fm.get_target_for_month(current_filename) if current_filename else 0

    forecast_data = {
        "daily_actual": [],
        "daily_forecast": [],
        "today": 0,
        "month_days": 0,
    }

    if current_df is not None:
        try:
            forecast_data = Forecaster.forecast_current_month(
                current_df, weekday_averages
            )
        except Exception:
            pass

    today_date = datetime.now().strftime("%d %b")
    total_sales = sum(forecast_data.get("daily_actual", []))

    graphs = {
        "historical_trend": "{}",
        "weekday_avg": "{}",
        "monthly_forecast": "{}",
        "cumulative_vs_target": "{}",
        "actual_vs_required": "{}",
        "monthly_comparison": "{}",
    }

    try:
        graphs["historical_trend"] = Visualizer.create_historical_daily_trend(
            historical_dfs
        )
        graphs["weekday_avg"] = Visualizer.create_weekday_average_chart(
            weekday_averages
        )
    except Exception:
        pass

    return {
        "kpis": {
            "today_date": today_date,
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
