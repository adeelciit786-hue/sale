# Sales Dashboard Setup Script
# This script initializes the Python environment and installs dependencies

Write-Host "================================================"
Write-Host "CC Sales Dashboard - Setup Script"
Write-Host "================================================" -ForegroundColor Green
Write-Host ""

# Check for Python
Write-Host "Checking for Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = & py -3 --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found. Please install Python 3.10 or later from https://www.python.org/" -ForegroundColor Red
    Write-Host "  Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Red
    exit 1
}

# Check if venv exists and is valid
Write-Host ""
Write-Host "Checking virtual environment..." -ForegroundColor Yellow
$venvPath = ".\venv"
$venvPython = "$venvPath\Scripts\python.exe"

if (Test-Path $venvPython) {
    Write-Host "✓ Virtual environment found" -ForegroundColor Green
    
    # Verify venv is not corrupted
    try {
        $venvVersion = & $venvPython --version 2>&1
        Write-Host "✓ Virtual environment is valid: $venvVersion" -ForegroundColor Green
    } catch {
        Write-Host "✗ Virtual environment is corrupted. Recreating..." -ForegroundColor Yellow
        Remove-Item $venvPath -Recurse -Force
        & py -3 -m venv $venvPath
    }
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & py -3 -m venv $venvPath
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& "$venvPath\Scripts\Activate.ps1"

# Install requirements
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
$requirementsFile = ".\sales_app\requirements.txt"

if (Test-Path $requirementsFile) {
    try {
        pip install -q -r $requirementsFile
        Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        Write-Host $_.Exception.Message
        exit 1
    }
} else {
    Write-Host "✗ requirements.txt not found at $requirementsFile" -ForegroundColor Red
    exit 1
}

# Verify all required packages
Write-Host ""
Write-Host "Verifying packages..." -ForegroundColor Yellow
$requiredPackages = @("flask", "pandas", "openpyxl", "plotly", "matplotlib")
$allPackagesFound = $true

foreach ($package in $requiredPackages) {
    try {
        python -c "import $package" 2>&1 | Out-Null
        Write-Host "✓ $package" -ForegroundColor Green
    } catch {
        Write-Host "✗ $package not found" -ForegroundColor Red
        $allPackagesFound = $false
    }
}

if (-not $allPackagesFound) {
    Write-Host ""
    Write-Host "Some packages are missing. Retrying installation..." -ForegroundColor Yellow
    pip install --upgrade pip
    pip install -r $requirementsFile
}

Write-Host ""
Write-Host "================================================"
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "================================================"
Write-Host ""
Write-Host "To start the application, run:"
Write-Host "  .\run_app.ps1"
Write-Host ""
