from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from pathlib import Path
import os
import sys
from datetime import datetime

# ============================================
# DEPENDENCY CHECK
# ============================================
def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = {
        'flask': 'flask',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl',
        'plotly': 'plotly',
        'matplotlib': 'matplotlib',
    }
    
    missing_packages = []
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
        except ImportError:
            missing_packages.append(package_name.lower())
    
    if missing_packages:
        error_msg = f"Missing required packages: {', '.join(missing_packages)}\n"
        error_msg += "Please install them using:\n"
        error_msg += f"pip install {' '.join(missing_packages)}"
        print(f"ERROR: {error_msg}", file=sys.stderr)
        sys.exit(1)

check_dependencies()

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from excel_loader import ExcelLoader
from file_manager import FileManager
from forecast import Forecaster
from visualizer import Visualizer

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data'
app.secret_key = 'sales-dashboard-secret-key-2026'  # Required for sessions

# Admin credentials
ADMIN_USERNAME = 'Admin'
ADMIN_PASSWORD = 'Champ@123'

# Initialize file manager
fm = FileManager(app.config['UPLOAD_FOLDER'])

# ============================================
# HELPER FUNCTIONS
# ============================================

def get_current_month_name():
    """Get current month name from system date (e.g., 'January 2026')."""
    return datetime.now().strftime("%B %Y")

def get_current_month_filename():
    """Get current month name and year."""
    return datetime.now().strftime("%B %Y")

def load_all_historical_data():
    """Load all historical Excel files."""
    historical_dfs = {}
    weekday_maps = {}
    for filename, filepath in fm.get_historical_files():
        df, error, weekday_map = ExcelLoader.load_file(filepath)
        if error:
            print(f"Error loading {filename}: {error}")
        else:
            historical_dfs[filename] = df
            if weekday_map:
                weekday_maps[filename] = weekday_map
    return historical_dfs, weekday_maps

def load_current_month_data():
    """Load current month Excel file."""
    filename, filepath = fm.get_current_month_file()
    if filepath:
        df, error, _ = ExcelLoader.load_file(filepath)
        if error:
            return None, None, error
        return filename, df, None
    return None, None, None

def get_dashboard_data():
    """Prepare all data for dashboard."""
    try:
        # Load data
        historical_dfs, weekday_maps = load_all_historical_data()
        current_filename, current_df, current_error = load_current_month_data()
        
        # Calculate weekday averages from historical data
        weekday_averages = Forecaster.calculate_weekday_averages(historical_dfs, weekday_maps)
        
        # Get current month target
        target = fm.get_target_for_current_month(current_filename) if current_filename else 0
        
        # Forecast current month
        if current_df is not None:
            forecast_data = Forecaster.forecast_current_month(current_df, weekday_averages)
        else:
            forecast_data = {
                'actual_total': 0,
                'projected_total': 0,
                'daily_actual': [],
                'daily_forecast': [],
                'today': 1,
                'month_days': 31,
                'today_projected_sale': 0
            }
        
        # Calculate KPIs using correct business logic
        today_date = datetime.now().strftime("%d %b")
        
        # TOTAL SALES TILL TODAY: Sum of actual daily sales from day 1 to today (inclusive)
        completed_days = forecast_data['today']
        total_sales_till_today = sum(forecast_data['daily_actual'][:completed_days])
        
        # TODAY'S PROJECTED SALE: Required daily pace to hit target
        today_projected_sale = Forecaster.calculate_kpi_today_projected_sale(
            forecast_data['daily_actual'],
            target,
            forecast_data['today'],
            forecast_data['month_days']
        )
        
        # MONTHLY PROJECTION: Run-rate based on actual sales so far
        monthly_projection = Forecaster.calculate_kpi_monthly_projection(
            forecast_data['daily_actual'],
            forecast_data['today'],
            forecast_data['month_days']
        )
        
        monthly_target = target
        
        # SHORTFALL: Monthly Target - Total Sales Till Today
        shortfall = monthly_target - total_sales_till_today
        
        # Calculate cumulative series
        cumulative_forecast, cumulative_target = Forecaster.get_cumulative_series(
            forecast_data['daily_forecast'],
            target,
            forecast_data['month_days']
        )
        
        # Get month names for comparison
        historical_files = fm.get_historical_files()
        month_options = [f[0].replace('.xlsx', '') for f in historical_files]
        
        # Calculate Graph 3 projections (Weekday-weighted projection)
        graph3_data = Forecaster.calculate_graph3_projections(
            forecast_data['daily_actual'],
            target,
            forecast_data['today'],
            forecast_data['month_days'],
            weekday_averages
        )
        
        # Create graphs
        graphs = {
            'historical_trend': Visualizer.create_historical_daily_trend(historical_dfs),
            'weekday_avg': Visualizer.create_weekday_average_chart(weekday_averages),
            'monthly_forecast': Visualizer.create_monthly_forecast(
                forecast_data['daily_actual'],
                graph3_data['daily_projected'],
                graph3_data['simple_daily_target'],
                forecast_data['today'],
                get_current_month_name()
            ),
            'cumulative_vs_target': Visualizer.create_cumulative_vs_target(
                cumulative_forecast,
                cumulative_target
            ),
            'actual_vs_required': Visualizer.create_actual_vs_required(
                forecast_data['daily_actual'],
                graph3_data['daily_projected'],
                forecast_data['today'],
                forecast_data['month_days']
            )
        }
        
        # Comparison chart (default: first two months)
        comparison_json = '{}'
        comparison_stats = {}
        if len(month_options) >= 2:
            comparison_json, comparison_stats = Visualizer.create_monthly_comparison(
                historical_dfs,
                month_options[0],
                month_options[1]
            )
        
        graphs['monthly_comparison'] = comparison_json
        
        return {
            'kpis': {
                'today_date': today_date,
                'total_sales_till_today': f"AED {total_sales_till_today:,.0f}",
                'today_projected_sale': f"AED {today_projected_sale:,.0f}",
                'monthly_projection': f"AED {monthly_projection:,.0f}",
                'monthly_target': f"AED {monthly_target:,.0f}",
                'shortfall': f"AED {abs(shortfall):,.0f}",
                'shortfall_type': 'shortfall' if shortfall > 0 else 'surplus'
            },
            'graphs': graphs,
            'historical_count': len(historical_dfs),
            'current_month': current_filename,
            'month_options': month_options,
            'comparison_stats': comparison_stats
        }
        
    except Exception as e:
        print(f"Error preparing dashboard data: {e}")
        return {
            'kpis': {
                'today_date': datetime.now().strftime("%d %b"),
                'total_sales_till_today': 'N/A',
                'today_projected_sale': 'N/A',
                'monthly_projection': 'N/A',
                'monthly_target': 'N/A',
                'shortfall': 'N/A',
                'shortfall_type': 'neutral'
            },
            'graphs': {},
            'error': str(e)
        }

# ============================================
# ROUTES
# ============================================
# AUTHENTICATION
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page."""
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('upload'))
        else:
            error = 'Invalid username or password'
    
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    """Admin logout."""
    session.pop('is_admin', None)
    return redirect(url_for('dashboard'))

# ============================================

@app.route('/')
def index():
    """Redirect to dashboard."""
    return redirect(url_for('dashboard'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload data page (Admin)."""
    # Check if user is authenticated
    if not session.get('is_admin'):
        return redirect(url_for('login'))
    
    message = None
    message_type = None
    
    if request.method == 'POST':
        # Handle historical data upload
        if 'historical_file' in request.files:
            file = request.files['historical_file']
            if file and file.filename:
                success, msg, _ = fm.save_historical_file(file, file.filename)
                message = msg
                message_type = 'success' if success else 'error'
        
        # Handle current month upload
        elif 'current_month_file' in request.files:
            file = request.files['current_month_file']
            if file and file.filename:
                success, msg, _ = fm.save_current_month_file(file, file.filename)
                message = msg
                message_type = 'success' if success else 'error'
        
        # Handle target input
        elif 'current_month' in request.form and 'target_value' in request.form:
            current_month = request.form['current_month']
            try:
                target_value = float(request.form['target_value'])
                success, msg = fm.save_target_for_current_month(current_month, target_value)
                message = msg
                message_type = 'success' if success else 'error'
            except ValueError:
                message = "Target must be a valid number"
                message_type = 'error'
        
        # Handle file deletion
        elif 'delete_file' in request.form:
            filename = request.form['delete_file']
            success, msg = fm.delete_historical_file(filename)
            message = msg
            message_type = 'success' if success else 'error'
        
        # Handle current month deletion
        elif 'delete_current' in request.form:
            success, msg = fm.delete_current_month_file()
            message = msg
            message_type = 'success' if success else 'error'
    
    # Get current files and targets
    historical_files = fm.get_historical_files()
    current_filename, _ = fm.get_current_month_file()
    targets = fm.load_targets()
    current_target = targets.get(Path(current_filename).stem, 0) if current_filename else 0
    
    return render_template(
        'upload.html',
        message=message,
        message_type=message_type,
        historical_files=historical_files,
        current_month_file=current_filename,
        current_target=current_target
    )

@app.route('/dashboard')
def dashboard():
    """Main dashboard page."""
    data = get_dashboard_data()
    return render_template('dashboard.html', data=data)

@app.route('/about')
def about():
    """About page."""
    return render_template('about.html')

@app.route('/api/comparison', methods=['POST'])
def api_comparison():
    """API endpoint for monthly comparison."""
    try:
        data = request.get_json()
        month1 = data.get('month1')
        month2 = data.get('month2')
        
        historical_dfs, _ = load_all_historical_data()
        comparison_json, stats = Visualizer.create_monthly_comparison(
            historical_dfs, month1, month2
        )
        
        return jsonify({
            'success': True,
            'chart': comparison_json,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler."""
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(error):
    """500 error handler."""
    return render_template('error.html', error="Server error occurred"), 500

# ============================================
# APP CONFIG
# ============================================

if __name__ == '__main__':
    try:
        # Create data directories
        Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
        (Path(app.config['UPLOAD_FOLDER']) / 'historical').mkdir(exist_ok=True)
        (Path(app.config['UPLOAD_FOLDER']) / 'current').mkdir(exist_ok=True)
        
        print("=" * 60)
        print("CC Sales Dashboard - Starting Server")
        print("=" * 60)
        print(f"Debug Mode: ON")
        print(f"Server running at: http://localhost:5000")
        print(f"Admin Login: {ADMIN_USERNAME} / ****")
        print("=" * 60)
        print("Press Ctrl+C to stop the server\n")
        
        # Run app
        app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=True)
        
    except OSError as e:
        if "Address already in use" in str(e):
            print("\n" + "=" * 60)
            print("ERROR: Port 5000 is already in use!")
            print("=" * 60)
            print("Try one of the following:")
            print("1. Close the other application using port 5000")
            print("2. Wait a few seconds and try again")
            print("3. Change the port number in app.py")
            print("=" * 60 + "\n")
        else:
            print(f"\nERROR: {e}\n")
        sys.exit(1)
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"FATAL ERROR: {e}")
        print("=" * 60)
        print("Please check the error message above and verify:")
        print("1. All required packages are installed")
        print("2. The data directories exist and are writable")
        print("3. No other services are using port 5000")
        print("=" * 60 + "\n")
        sys.exit(1)
