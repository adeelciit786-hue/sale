@echo off
REM Sales Dashboard - Quick Start Batch Script for Windows

setlocal enabledelayedexpansion

echo.
echo ================================================
echo CC Sales Dashboard - Starting Application
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    py -3 --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Python is not installed or not in PATH
        echo.
        echo Please install Python from https://www.python.org/
        echo Make sure to check "Add Python to PATH" during installation
        echo.
        echo For detailed instructions, see: PYTHON_FIX.md
        echo.
        pause
        exit /b 1
    )
    set PYTHON_CMD=py -3
) else (
    set PYTHON_CMD=python
)

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo Virtual environment not found. Creating one...
    %PYTHON_CMD% -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        echo.
        echo This often happens when Python installation is corrupted.
        echo See PYTHON_FIX.md for detailed troubleshooting
        echo.
        pause
        exit /b 1
    )
)

REM Activate venv and install requirements
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    echo.
    echo Try deleting the venv folder and running this script again:
    echo   rmdir /s /q venv
    echo.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r sales_app\requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Trying again with verbose output...
    pip install -r sales_app\requirements.txt
    echo.
    pause
    exit /b 1
)

REM Run the app
echo.
echo ================================================
echo Starting Flask Application...
echo The app will be available at: http://localhost:5000
echo.
echo Login Credentials:
echo   Username: Admin
echo   Password: Champ@123
echo.
echo Press Ctrl+C to stop the server
echo ================================================
echo.

python sales_app\app.py
if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    echo.
    echo Common causes:
    echo - Port 5000 is already in use
    echo - Missing Python packages
    echo - Corrupted virtual environment
    echo.
    echo Try deleting venv and running this script again
    echo.
)

pause
