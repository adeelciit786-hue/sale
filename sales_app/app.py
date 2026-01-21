from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

# =========================================================
# SAFE ABSOLUTE IMPORTS (RENDER + GUNICORN SAFE)
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

# Ensure DB schema exists (safe for Render cold starts)
try:
    create_tables_if_not_exist()
except Exception as e:
    print("DB init skipped:", e)

ADMIN_USERNAME = "Admin"
ADMIN_PASSWORD = "Champ@123"

fm = FileManager()

# =========================================================
# UNIVERSAL ROUTE ALIASES (PREVENT url_for ERRORS)
# =========================================================
def _redirect_dashboard():
    return redirect(url_for("dashboard"))

def _redirect_upload():
    return redirect(url_for("upload"))

# Home aliases
app.add_url_rule("/", endpoint="home", view_func=_redirect_dashboard)
app.add_url_rule("/index", endpoint="index", view_func=_redirect_dashboard)
app.add_url_rule("/dashboard-view", endpoint="dashboard_view", view_func=_redirect_dashboard)

# Upload aliases
app.add_url_rule("/upload-data", endpoint="upload_data", view_func=_redirect_upload)
app.add_url_rule("/save-target", endpoint="save_target", view_func=_redirect_upload)

# Logout alias
app.add_url_rule("/logout-user", endpoint="logout_user", view_func=lambda: logout())

# =========================================================
# HELPERS
# =========================================================
def get_current_month_name():
    return datetime.now().strftime("%B %Y")

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
# UPLOAD
# =========================================================
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    message = None
    message_type = None

    if request.method == "POST":

        # -------- HISTORICAL --------
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
                    month = datetime.strptime(month_label.split()[0], "%B").month

                    fm.clear_month_data(month_label, "historical")
                    rows = insert_sales_dataframe(
                        df, year, month, month_label, "historical"
                    )
                    fm.log_upload(month_label, "historical")

                    message = f"Historical data uploaded ({rows} rows)"
                    message_type = "success"

        # -------- CURRENT MONTH --------
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
                    month = datetime.strptime(month_label.split()[0], "%B").month

                    fm.clear_month_data(month_label, "current")
                    rows = insert_sales_dataframe(
                        df, year, month, month_label, "current"
                    )
                    fm.log_upload(month_label, "current")

                    message = f"Current month uploaded ({rows} rows)"
                    message_type = "success"

        # -------- TARGET --------
        elif "current_month" in request.form and "target_value" in request.form:
            try:
                target_value = float(request.form["target_value"])
                success, msg = fm.save_target_for_month(
                    request.form["current_month"], target_value
                )
                message = msg
                message_type = "success" if success else "error"
            except ValueError:
                message = "Target must be a number"
                message_type = "error"

    return render_template("upload.html", message=message, message_type=message_type)

# =========================================================
# DASHBOARD (DB-ONLY, ALWAYS LIVE, SAFE)
# =========================================================
def get_dashboard_data():
    historical_dfs, weekday_maps = load_historical_dataframes()
    current_filename, current_df = load_current_month_dataframe()

    weekday_averages = Forecaster.calculate_weekday_averages(
        historical_dfs, weekday_maps
    )

    target = fm.get_target_for_month(current_filename) if current_filename else 0

    # SAFE FORECAST DEFAULT
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
            "today": 0,
            "month_days": 0,
            "today_projected_sale": 0,
        }

    today_date = datetime.now().strftime("%d %b")
    total_sales = sum(forecast_data["daily_actual"])

    graphs = {}
    try:
        graphs["historical_trend"] = Visualizer.create_historical_daily_trend(
            historical_dfs
        )
        graphs["weekday_avg"] = Visualizer.create_weekday_average_chart(
            weekday_averages
        )

        if forecast_data["month_days"] > 0:
            graphs["monthly_forecast"] = Visualizer.create_monthly_forecast(
                forecast_data["daily_actual"],
                forecast_data["daily_forecast"],
                None,
                forecast_data["today"],
                get_current_month_name(),
            )
    except Exception as e:
        print("Chart error:", e)

    return {
        "kpis": {
            "today_date": today_date,
            "total_sales": f"AED {total_sales:,.0f}",
            "monthly_target": f"AED {target:,.0f}",
        },
        "graphs": graphs,
        "current_month": current_filename,
    }

# =========================================================
# ROUTES
# =========================================================
@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html", data=get_dashboard_data())

@app.route("/about")
def about():
    return render_template("about.html")

# =========================================================
# ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found"), 404

# =========================================================
# LOCAL RUN ONLY (GUNICORN IGNORES THIS)
# =========================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
