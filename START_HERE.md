# 🚀 Quick Start - Choose Your Method

## Fastest Way to Run (Choose One)

### ⭐ Method 1: Double-Click (Easiest)
1. Go to: `d:\CC Projects\CC Sales Dashboard`
2. Double-click: **`run_app.bat`**
3. Wait for automatic setup
4. Open: **http://localhost:5000**

### ⭐ Method 2: PowerShell (More Details)
```powershell
cd "d:\CC Projects\CC Sales Dashboard"
.\run_app.ps1
```

### ⭐ Method 3: Manual (If Other Methods Fail)
```bash
cd "d:\CC Projects\CC Sales Dashboard"
python -m venv venv
venv\Scripts\activate
pip install -r sales_app\requirements.txt
python sales_app\app.py
```

---

## 🔴 Current Problem

Your Python installation (3.14) is corrupted. The venv can't find the Python executable.

## ✅ Solution

### Quick Fix (Try This First)
Run: `run_app.bat` or `.\run_app.ps1`

These scripts will:
- ✅ Try to repair the virtual environment
- ✅ Reinstall all packages if needed
- ✅ Give you clear error messages

### If Quick Fix Doesn't Work

Follow the detailed guide: **PYTHON_FIX.md**

This will:
1. Uninstall broken Python 3.14
2. Install fresh Python (3.12 or 3.13)
3. Get everything working again

---

## 🎯 Access Your App

Once running:
- **URL**: http://localhost:5000
- **Username**: Admin
- **Password**: Champ@123

---

## 📚 Documentation Files

| File | Purpose |
|------|---------|
| `SETUP_GUIDE.md` | Complete setup & troubleshooting |
| `PYTHON_FIX.md` | How to fix Python corruption |
| `IMPROVEMENTS_SUMMARY.md` | What was improved & why |

---

## ❓ Still Having Issues?

1. **Check**: `PYTHON_FIX.md` for Python problems
2. **Check**: `SETUP_GUIDE.md` for general issues
3. **Run**: `.\run_app.ps1` with verbose output
4. **Delete** `venv` folder and try again

---

**Created**: January 19, 2026
