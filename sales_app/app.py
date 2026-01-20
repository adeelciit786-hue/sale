from flask import Flask, render_template, request, redirect, url_for, session
import os
import sys
from datetime import datetime

# ============================================
# DEPENDENCY CHECK
# ============================================
def check_dependencies():
    required_packages = {
        "flask": "flask",
        "pandas": "pandas",
        "openpyxl": "openpyxl",
        "plotly": "plotly",
        "matplotlib": "matplotlib",
    }
    missing = []
    for pkg, imp in required_packages.items():
        try:
            __import__(imp)
        except ImportError:
            missing.append(pkg)
    if missing:
        print(f"Missing packages: {missing}")
        sys.exit(1)

check_dependencies()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ============================================
# IMPORTS
# ============================================
try:
    from .excel_loader import ExcelLoader
    from .file_manager import FileManager
    from .forecast import Forecaster
    from .visualizer import Visualizer
    from .db_loader import (
        create_tables_if_not_exist,
        insert_sales_dataframe,
        load_historical_dataframes,
        load_current_month_dataframe,
    )
except ImportError:
    from excel_loader import ExcelLoader
    from file_manager import FileManager
    from forecast import Forecaster
    from visualizer import Visualizer
    from db_loader import (
        create_tables_if_not_exist,
        insert_sales_dataframe,
        load_historical_dataframes,
        load_current_month_dataframe,
    )

# ============================================
# APP SETUP
# ============================================
app = Flask(__name__)
app.secret_key = "sales-dashboard-secret-key-2026"
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

create_tables_if_not_exist()

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Champ@123"

fm = FileManager("data")

# ============================================
# HELPERS (DB-BACKED)
# ============================================
def get_current_month_name():
    return datetime.now().strftime("%B %Y")


def load_all_historical_data():
    return load_historical_dataframes()


def load_current_month_data():
    filename, df = load_current_month_dataframe()
    if df is None:
        return None, None, None
    return filename, df, None

# ============================================
# AUTH
# ============================================
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

# ============================================
# ROUTES
# ============================================
@app.route("/")
def index():
    return redirect(url_for("dashboard"))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    message = None
    message_type = None

    if request.method == "POST":

        # =========================
        # HISTORICAL UPLOAD
        # =========================
        if "historical_file" in request.files:
            file = request.files["historical_file"]
            if file and file.filename:
                temp_path = f"/tmp/{file.filename}"
                file.save(temp_path)

                df, error, _ = ExcelLoader.load_file(temp_path)
                if error:
                    message = error
                    message_type = "error"
                else:
                    month_label = file.filename.replace(".xlsx", "")
                    year = int(month_label.split()[-1])
                    month = datetime.strptime(
                        month_label.split()[0], "%B"
                    ).month

                    fm.clear_month_data(month_label, "historical")

                    rows = insert_sales_dataframe(
                        df, year, month, month_label, "historical"
                    )
                    fm.log_upload(month_label, "historical")

                    message = f"Historical data uploaded ({rows} rows)"
                    message_type = "success"

        # =========================
        # CURRENT MONTH UPLOAD
        # =========================
        elif "current_month_file" in request.files:
            file = request.files["current_month_file"]
            if file and file.filename:
                temp_path = f"/tmp/{file.filename}"
                file.save(temp_path)

                df, error, _ = ExcelLoader.load_file(temp_path)
                if error:
                    message = error
                    message_type = "error"
                else:
                    month_label = file.filename.replace(".xlsx", "")
                    year = int(month_label.split()[-1])
                    month = datetime.strptime(
                        month_label.split()[0], "%B"
                    ).month

                    fm.clear_month_data(month_label, "current")

                    rows = insert_sales_dataframe(
                        df, year, month, month_label, "current"
                    )
                    fm.log_upload(month_label, "current")

                    message = f"Current month data uploaded ({rows} rows)"
                    message_type = "success"

        # =========================
        # TARGET SAVE
        # =========================
        elif "current_month" in request.form and "target_value" in request.form:
            try:
                target_value = float(request.form["target_value"])
                success, msg = fm.save_target_for_month(
                    request.form["current_month"], target_value
                )
                message = msg
                message_type = "success" if success else "error"
            except ValueError:
                message = "Target must be a valid number"
                message_type = "error"

    return render_template(
        "upload.html",
        message=message,
        message_type=message_type,
    )

# ============================================
# DASHBOARD (DB READY – UI BINDING NEXT)
# ============================================
def get_dashboard_data():
    """
    Prepare dashboard data from DB-backed loaders.
    Logic remains identical to earlier Excel version.
    """
    # Load data from DB
  historical_dfs, weekday_maps = load_historical_dataframes()
  current_filename, current_df = load_current_month_dataframe()

    # Calculate weekday averages
    weekday_averages = Forecaster.calculate_weekday_averages(
        historical_dfs, weekday_maps
    )

    # Target
    target = fm.get_target_for_current_month(current_filename) if current_filename else 0

    # Forecast
    if current_df is not None:
        forecast_data = Forecaster.forecast_current_month(
            current_df, weekday_averages
        )
    else:
        forecast_data = {
            "actual_total": 0,
            "projected_total": 0,
            "daily_actual": [],
            "daily_forecast": [],
            "today": 1,
            "month_days": 31,
            "today_projected_sale": 0,
        }

    # KPIs
    today_date = datetime.now().strftime("%d %b")
    completed_days = forecast_data["today"]
    total_sales_till_today = sum(
        forecast_data["daily_actual"][:completed_days]
    )

    today_projected_sale = Forecaster.calculate_kpi_today_projected_sale(
        forecast_data["daily_actual"],
        target,
        forecast_data["today"],
        forecast_data["month_days"],
    )

    monthly_projection = Forecaster.calculate_kpi_monthly_projection(
        forecast_data["daily_actual"],
        forecast_data["today"],
        forecast_data["month_days"],
    )

    shortfall = target - total_sales_till_today

    cumulative_forecast, cumulative_target = Forecaster.get_cumulative_series(
        forecast_data["daily_forecast"],
        target,
        forecast_data["month_days"],
    )

    graphs = {
        "historical_trend": Visualizer.create_historical_daily_trend(
            historical_dfs
        ),
        "weekday_avg": Visualizer.create_weekday_average_chart(
            weekday_averages
        ),
        "monthly_forecast": Visualizer.create_monthly_forecast(
            forecast_data["daily_actual"],
            forecast_data["daily_forecast"],
            None,
            forecast_data["today"],
            get_current_month_name(),
        ),
        "cumulative_vs_target": Visualizer.create_cumulative_vs_target(
            cumulative_forecast, cumulative_target
        ),
    }

    return {
        "kpis": {
            "today_date": today_date,
            "total_sales_till_today": f"AED {total_sales_till_today:,.0f}",
            "today_projected_sale": f"AED {today_projected_sale:,.0f}",
            "monthly_projection": f"AED {monthly_projection:,.0f}",
            "monthly_target": f"AED {target:,.0f}",
            "shortfall": f"AED {abs(shortfall):,.0f}",
            "shortfall_type": "shortfall" if shortfall > 0 else "surplus",
        },
        "graphs": graphs,
        "current_month": current_filename,
    }

@app.route("/dashboard")
def dashboard():
    data = get_dashboard_data()
    return render_template("dashboard.html", data=data)
@app.route("/dashboard")
def dashboard():
    data = get_dashboard_data()
    return render_template("dashboard.html", data=data)
@app.route("/dashboard")
def dashboard():
    data = get_dashboard_data()
    return render_template("dashboard.html", data=data)

@app.route("/about")
def about():
    return render_template("about.html")

# ============================================
# ERRORS
# ============================================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found"), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error="Server error"), 500

# ============================================
# RUN
# ============================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
