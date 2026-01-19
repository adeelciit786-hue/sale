# Enterprise Sales Forecasting Dashboard

A professional-grade Flask application for sales analysis and forecasting with real-time KPI tracking and interactive visualizations.

## Overview

This dashboard provides management with:
- **Real-time KPI Tracking**: Today's projected sales, monthly projections, target alignment
- **Smart Forecasting**: Weekday-based statistical model using historical sales patterns
- **Interactive Visualizations**: 6 comprehensive graphs for trend analysis and decision-making
- **Data Management**: Secure file uploads, automatic processing, persistent storage
- **Responsive Design**: Corporate interface with soft gradients and professional styling

## Features

### Dashboard KPIs
- **Today's Date**: Current date display
- **Today's Projected Sale**: Forecasted sales based on weekday averages
- **Monthly Projection**: Estimated total monthly sales
- **Monthly Target**: Revenue goal (configurable)
- **Gap (Surplus/Shortfall)**: Visual indicator of target alignment

### Interactive Graphs
1. **Daily Sales Trend** - Historical daily sales patterns across all months
2. **Average Sales by Weekday** - Weekday distribution (foundation of forecasting)
3. **Sales Projection** - Current month actual vs forecast with today's marker
4. **Cumulative vs Target** - Progress toward monthly target
5. **Daily vs Required Sales** - Actual vs required pace to hit target
6. **Monthly Comparison** - Compare any two months side-by-side

### Admin Capabilities
- **Upload Historical Data**: Multiple months (Aug 2025 - Dec 2025 example)
- **Upload Current Month**: Replace existing current month file
- **Set Monthly Targets**: AED-based revenue goals
- **Delete Files**: Safe removal of historical or current data
- **View File List**: Track all uploaded data

## Technology Stack

- **Backend**: Flask 2.3.3 (Python web framework)
- **Data Processing**: Pandas 2.0.3, OpenPyXL 3.1.2
- **Visualizations**: Plotly 5.18.0 (interactive charts)
- **Web Server**: Gunicorn 21.2.0 (production)
- **Styling**: Custom CSS with responsive design

## Project Structure

```
sales_app/
├── app.py                          # Flask application & routes
├── excel_loader.py                 # Excel file parsing & validation
├── forecast.py                     # Forecasting algorithm
├── file_manager.py                 # File operations & persistence
├── visualizer.py                   # Graph generation (Plotly)
├── requirements.txt                # Python dependencies
├── templates/
│   ├── base.html                   # Base template with navigation
│   ├── dashboard.html              # Main dashboard page
│   ├── upload.html                 # Admin upload interface
│   ├── about.html                  # Documentation & methodology
│   └── error.html                  # Error page
├── static/
│   └── css/
│       └── style.css               # Corporate styling
└── data/
    ├── historical/                 # Historical Excel files
    ├── current/                    # Current month Excel file
    └── targets.json               # Persistent targets storage
```

## Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)

### Local Setup

1. **Create and activate virtual environment:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
python app.py
```

The app will start on `http://127.0.0.1:5000`

### Directory Structure After First Run

The app automatically creates:
```
data/
├── historical/          # Store historical Excel files
├── current/            # Current month file (only one)
└── targets.json        # Auto-created on first target save
```

## Excel File Format (REQUIRED)

### Row 1: Headers
- Column A: "Branch"
- Columns B-H: Weekday codes (MON, TUE, WED, THU, FRI, SAT, SUN)

### Row 2 Onwards: Data
- Column A: Branch name (e.g., "Dubai Store", "Abu Dhabi Store")
- Columns B-H: Daily sales figures (AED amounts)
- Data cells: Numbers, "-" (zero), or empty

### Last Row: TOTAL
- Column A: "TOTAL" (label)
- Columns B-H: Formulas (auto-calculated, NOT used in forecasting)

### Example Format
```
Branch          MON     TUE     WED     THU     FRI     SAT     SUN
Dubai Store     125000  130000  115000  140000  150000  160000  170000
Abu Dhabi Store 95000   100000  90000   105000  120000  130000  140000
Sharjah Store   75000   80000   70000   85000   95000   105000  115000
Ajman Store     55000   60000   50000   65000   75000   85000   95000
TOTAL           350000  370000  325000  395000  440000  480000  520000
```

**IMPORTANT RULES:**
- TOTAL row is **automatically excluded** from all calculations
- Dashes ("-") are converted to 0
- Empty cells are treated as 0
- File names serve as identifiers (use descriptive names like "August2025.xlsx")

## Forecasting Algorithm

### Model Type: Weekday-Based Statistical Forecasting

**Step 1: Calculate Weekday Averages**
- Analyze all historical data (minimum 2 months required)
- Compute average sales for each weekday (MON-SUN)
- Exclude TOTAL row automatically

**Step 2: Current Month Forecast**
- Past days: Use actual sales
- Today: Use actual if available, else weekday average
- Future days: Use weekday average forecast

**Step 3: Project Monthly Total**
```
Monthly Projection = SUM(actual past days) + SUM(forecasted future days)
```

**Data Quality Indicator:**
- **Excellent**: 4+ historical months
- **Good**: 3 historical months
- **Limited**: 2 historical months (minimum)

## Usage Guide

### For Management (Dashboard)
1. Open `http://localhost:5000` or deployed URL
2. View **KPI Cards** at top for quick status
3. Analyze **6 graphs** for detailed insights
4. Track **Gap** (Surplus/Shortfall) against target
5. Compare **monthly trends** using comparison graph

### For Administrators (Upload Data)
1. Navigate to **Upload Data** tab
2. **Upload Historical Files**: Drag-and-drop multiple months
3. **Upload Current Month**: Replace existing file as needed
4. **Set Target**: Enter monthly revenue goal in AED
5. **Delete Files**: Remove outdated data (app stays stable)

### Important Upload Rules
- **Historical**: Multiple files allowed (e.g., Aug-Dec 2025)
- **Current Month**: Only ONE file (new uploads replace old)
- **Targets**: Persisted across restarts & deployments
- **Same Filename**: Automatically replaces previous file

## Deployment (Render)

### Environment Setup (Render)
1. Create Procfile:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT sales_app.app:app
```

2. Create runtime.txt (optional):
```
python-3.11.0
```

3. Push to GitHub (if using Render's Git integration)

### Configuration
- Set environment variable if needed: `FLASK_ENV=production`
- Render will auto-install from requirements.txt
- Port: Render assigns dynamically (Gunicorn binds to $PORT)

### Data Persistence
- Files stored in `data/` directory (persists on Render's managed storage if configured)
- For Render: Use external storage (e.g., AWS S3) for persistent data across deployments
- Targets.json survives restarts on local, configure external storage for cloud

## File Safety & Stability

**Built-in Protection:**
- ✅ Missing files handled gracefully
- ✅ File deletions never crash app
- ✅ File replacements are atomic
- ✅ Empty folders allowed
- ✅ Invalid Excel files show user-friendly errors
- ✅ All file I/O wrapped in try/except
- ✅ TOTAL row always excluded from calculations

## API Endpoints

### GET Routes
- `/` - Redirect to dashboard
- `/dashboard` - Main dashboard page
- `/upload` - Admin upload interface
- `/about` - Documentation page

### POST Routes
- `/upload` (POST) - Handle file uploads and target setting
- `/api/comparison` (POST) - Get monthly comparison data

## Error Handling

**Business-Friendly Error Messages:**
- No Python tracebacks shown to users
- Clear explanations for upload failures
- Graceful handling of missing data
- Validation warnings for data quality issues

## Configuration

### Flask Settings
- `MAX_CONTENT_LENGTH`: 16MB file upload limit
- `DEBUG`: True (development), False (production)
- `HOST`: 0.0.0.0 (all interfaces)
- `PORT`: 5000 (development), $PORT (Render)

### Forecast Settings
- Minimum historical months: 2
- Weekdays: MON-SUN (7 days)
- Tolerance for data validation: ±1%

## Performance Notes

- **Historical Data**: Handles 12+ months efficiently
- **File Uploads**: <5 second upload for typical files
- **Calculations**: <1 second for dashboard rendering
- **Graphs**: Plotly renders responsively in browser

## Security Notes

- ✅ Files stored server-side (not accessible directly via URL)
- ✅ File names sanitized (special characters removed)
- ✅ Upload size limited to 16MB
- ✅ No user authentication (assumes admin-only access)
- ⚠️ For production: Add user authentication & role management

## Troubleshooting

### Dashboard shows "N/A" for KPIs
- **Solution**: Upload current month file first via Upload Data tab

### No graphs displayed
- **Solution**: Ensure 2+ historical files are uploaded

### "Could not find Excel file" error
- **Solution**: Verify file format matches specification (MON-SUN headers, TOTAL row)

### File upload fails
- **Solution**: Check file size (<16MB) and ensure .xlsx format

### Deleted file still appears
- **Solution**: Browser cache - refresh page (Ctrl+F5)

## Support & Maintenance

### Regular Tasks
- **Monthly**: Review forecasting accuracy vs actual
- **Quarterly**: Archive old historical data
- **As needed**: Update targets, upload current month

### Maintenance
- Check `data/targets.json` for persistence
- Monitor `data/historical/` for storage usage
- Review error logs for upload issues

## License & Attribution

Professional Enterprise Dashboard
Version 1.0 | 2025

---

**For detailed methodology, visit the About tab in the application.**
