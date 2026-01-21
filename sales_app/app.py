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

# DB init (Render-safe)
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

# =========================================================
# AUTH ROUTES
# =========================================================
@app.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    error = None
    if request.method == "POST":
        if (
            request.form.get("username") == ADMIN_USERNAME
            and request.form.get("password") == ADMIN_PASSWORD
        ):
            session["is_admin"] = True
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)


@app.route("/logout", endpoint="logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("dashboard"))

# =========================================================
# UPLOAD ROUTES (ALIASES INCLUDED)
# =========================================================
@app.route("/upload", methods=["GET", "POST"], endpoint="upload")
@app.route("/upload-data", methods=["GET", "POST"], endpoint="upload_data")
def upload():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    message = None
    message_type = None

    if request.method == "POST":

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

                    message = f"Current month uploaded ({rows} rows)"
                    message_type = "success"

        elif "current_month" in request.form and "target_value" in request.form:
            try:
                target_value = float(request.form["target_value"])
                fm.save_target_for_month(
                    request.form["current_month"], target_value
                )
                message = "Target saved successfully"
                message_type = "success"
            except ValueError:
                message = "Target must be numeric"
                message_type = "error"

    return render_template(
        "upload.html",
        message=message,
        message_type=message_type,
    )

# =========================================================
# DASHBOARD DATA (SAFE)
# =========================================================
def get_dashboard_data():
    historical_dfs, weekday_maps = load_historical_dataframes()
    current_filename, current_df = load_current_month_dataframe()

    weekday_averages = Forecaster.calculate_weekday_averages(
        historical_dfs, weekday_maps
    )

    target = fm.get_target_for_month(current_filename) if current_filename else 0

    if current_df is not None:
        forecast_data = Forecaster.forecast_current_month(
            current_df, weekday_averages
        )
    else:
        forecast_data = {
            "daily_actual": [],
            "daily_forecast": [],
            "today": 0,
            "month_days": 0,
        }

    graphs = {}
    try:
        graphs["historical_trend"] = Visualizer.create_historical_daily_trend(
            historical_dfs
        )
        graphs["weekday_avg"] = Visualizer.create_weekday_average_chart(
            weekday_averages
        )
    except Exception as e:
        print("Graph error:", e)

    return {
        "kpis": {
            "today_date": datetime.now().strftime("%d %b"),
            "total_sales": "AED 0",
            "monthly_target": f"AED {target:,.0f}",
            "today_projected_sale": "AED 0",
            "monthly_projection": "AED 0",
            "shortfall": "AED 0",
            "shortfall_type": "neutral",
        },
        "graphs": graphs,
        "current_month": current_filename,
    }

# =========================================================
# DASHBOARD ROUTES (ALIASES INCLUDED)
# =========================================================
@app.route("/", endpoint="home")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard", endpoint="dashboard")
@app.route("/dashboard-view", endpoint="dashboard_view")
def dashboard():
    return render_template("dashboard.html", data=get_dashboard_data())

@app.route("/about", endpoint="about")
def about():
    return render_template("about.html")

# =========================================================
# ERROR HANDLERS
# =========================================================
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", error="Server error"), 500

# =========================================================
# LOCAL RUN ONLY
# =========================================================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
