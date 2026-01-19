# CC Sales Dashboard - Setup & Running Guide

## Quick Start

### Option 1: Batch File (Easiest for Windows)
```bash
run_app.bat
```
Double-click this file or run it from Command Prompt. It will:
- Check for Python
- Create/verify virtual environment
- Install all dependencies
- Start the application at http://localhost:5000

### Option 2: PowerShell Script
```powershell
.\run_app.ps1
```
Run in PowerShell. Same functionality as batch file with detailed output.

### Option 3: Manual Setup
```powershell
# 1. Create virtual environment
py -3 -m venv venv

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r sales_app\requirements.txt

# 4. Run the application
python sales_app\app.py
```

## System Requirements

- **Python**: 3.10 or later (not 3.14 with broken installation)
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: At least 500MB free space
- **Port 5000**: Must be available (not in use by another application)

## Installation Issues

### Issue: "Python not found"
**Solution**: 
1. Download Python from https://www.python.org/
2. During installation, **check the box** "Add Python to PATH"
3. Restart your terminal/command prompt
4. Run the setup script again

### Issue: "Port 5000 already in use"
**Solution**:
1. Find what's using port 5000: `netstat -ano | findstr :5000`
2. Either close that application or change port in `sales_app/app.py` (line ~385)
3. Change `port=5000` to `port=5001` (or another available port)

### Issue: "Module not found" or Import errors
**Solution**:
1. Run the setup script again: `.\setup.ps1` or `run_app.bat`
2. If still failing, try manual installation:
   ```powershell
   .\venv\Scripts\Activate.ps1
   pip install --upgrade pip
   pip install -r sales_app\requirements.txt
   ```

### Issue: Virtual environment is corrupted
**Solution**:
```powershell
# Remove the corrupted venv
Remove-Item venv -Recurse -Force

# Run setup script (creates new venv)
.\setup.ps1
```

## Application Access

Once running, access the dashboard at:
```
http://localhost:5000
```

### Default Login Credentials
- **Username**: Admin
- **Password**: Champ@123

## File Structure

```
CC Sales Dashboard/
├── sales_app/
│   ├── app.py                 # Main Flask application
│   ├── requirements.txt        # Python dependencies
│   ├── excel_loader.py
│   ├── file_manager.py
│   ├── forecast.py
│   ├── visualizer.py
│   ├── data/                  # Data files
│   ├── static/                # CSS, JS, images
│   └── templates/             # HTML templates
├── venv/                      # Virtual environment (created by setup)
├── setup.ps1                  # PowerShell setup script
├── run_app.ps1                # PowerShell run script
└── run_app.bat                # Windows batch run script
```

## Troubleshooting Commands

### Check Python installation
```powershell
python --version
py -3 --version
```

### Verify virtual environment
```powershell
# Activate venv first
.\venv\Scripts\Activate.ps1

# Check Python executable
python --version

# List installed packages
pip list
```

### Test Flask setup
```powershell
.\venv\Scripts\Activate.ps1
python -c "import flask; print(f'Flask version: {flask.__version__}')"
```

### Check if port 5000 is in use
```powershell
# Windows
netstat -ano | findstr :5000

# PowerShell alternative
Get-NetTCPConnection -LocalPort 5000 -ErrorAction SilentlyContinue
```

## Stopping the Application

Press `Ctrl+C` in the terminal/command prompt where the app is running.

## Advanced Configuration

To change the port, edit `sales_app/app.py` and change this line:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Change 5000 to your port
```

To disable debug mode, change `debug=True` to `debug=False` (recommended for production).

## Support

If you encounter issues:
1. Check this troubleshooting guide first
2. Run the setup script again to verify all dependencies
3. Check the application logs in the terminal for detailed error messages
4. Ensure Python 3.10+ is properly installed and in your PATH

---

**Last Updated**: January 19, 2026
