# Run Sales Dashboard Application
# This script starts the Flask application with proper error handling

Write-Host "================================================"
Write-Host "CC Sales Dashboard - Starting Application"
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

$venvPath = ".\venv"
$venvPython = "$venvPath\Scripts\python.exe"
$appPath = ".\sales_app\app.py"

# Check virtual environment
if (-not (Test-Path $venvPython)) {
    Write-Host "✗ Virtual environment not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Running setup script..." -ForegroundColor Yellow
    & .\setup.ps1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "Setup failed. Please check the errors above." -ForegroundColor Red
        exit 1
    }
}

# Check if app.py exists
if (-not (Test-Path $appPath)) {
    Write-Host "✗ app.py not found at $appPath" -ForegroundColor Red
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

Write-Host ""
Write-Host "Starting Flask application..." -ForegroundColor Yellow
Write-Host "The application will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server"
Write-Host ""

# Run the application
try {
    python $appPath
} catch {
    Write-Host ""
    Write-Host "✗ Error running application:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}
