# CC Sales Dashboard - Installation & Running Guide

## 📋 What We've Added for Reliability

```
✅ Dependency Validation - Checks packages before startup
✅ Auto-Setup Scripts - Creates venv and installs packages
✅ Enhanced Error Handling - Clear error messages with solutions
✅ Multiple Run Methods - Batch, PowerShell, and manual
✅ Detailed Documentation - Comprehensive troubleshooting guides
```

---

## 🚀 Getting Started

### Step 1: Choose Your Method

```
Method 1 (Easiest)
└─→ Double-click: run_app.bat
    └─→ Automatic setup and launch

Method 2 (PowerShell)
└─→ Command: .\run_app.ps1
    └─→ Same as Method 1 with detailed output

Method 3 (Manual)
└─→ Create venv manually
└─→ Install packages
└─→ Run app
```

### Step 2: Fix Python (if needed)

If Methods 1 & 2 fail:
1. Read: `PYTHON_FIX.md`
2. Uninstall Python 3.14
3. Install Python 3.12 or 3.13
4. Try again

### Step 3: Access the App

```
http://localhost:5000
```

Login:
- Username: `Admin`
- Password: `Champ@123`

---

## 🛠️ What Was Improved

### Before
- ❌ Cryptic "ERR_CONNECTION_REFUSED" errors
- ❌ No indication of what's wrong
- ❌ Manual setup required
- ❌ No dependency validation

### After
- ✅ Clear error messages with solutions
- ✅ Auto-diagnosis of problems
- ✅ Automatic setup on first run
- ✅ Dependency validation before startup
- ✅ Multiple ways to run the app
- ✅ Comprehensive documentation

---

## 📁 New Files Created

```
d:\CC Projects\CC Sales Dashboard\
├── run_app.bat                 ⭐ Double-click to run
├── run_app.ps1                 ⭐ PowerShell run script  
├── setup.ps1                   ⭐ Manual setup script
├── START_HERE.md               📖 Quick start guide
├── SETUP_GUIDE.md              📖 Complete guide
├── PYTHON_FIX.md               📖 Python troubleshooting
└── IMPROVEMENTS_SUMMARY.md     📖 What was improved
```

---

## 🔍 Enhanced Code

### Dependency Checking
```python
# app.py now validates all packages on startup
- Flask
- pandas  
- openpyxl
- plotly
- matplotlib
```

### Error Handling
```
- Port conflict detection
- Missing package warnings
- Virtual environment validation
- Clear startup messages
```

---

## ⚡ Quick Reference

| Want to... | Do this |
|-----------|--------|
| Run app (easiest) | Double-click `run_app.bat` |
| Run app (PowerShell) | `.\run_app.ps1` |
| Manual setup | `python -m venv venv` then `pip install -r sales_app\requirements.txt` |
| Fix Python | Read `PYTHON_FIX.md` |
| Troubleshoot | Read `SETUP_GUIDE.md` |
| See improvements | Read `IMPROVEMENTS_SUMMARY.md` |

---

## 🚨 If Something Goes Wrong

### Error: "ERR_CONNECTION_REFUSED"
→ App didn't start. Run: `run_app.bat` and watch for error messages.

### Error: "Python not found"
→ Python isn't installed. Follow: `PYTHON_FIX.md`

### Error: "Port 5000 already in use"
→ Another app uses port 5000. Close it or change port in `sales_app\app.py`

### Error: "Module not found"
→ Dependency missing. Run: `run_app.bat` to auto-fix.

---

## 💡 Pro Tips

1. **Always use `run_app.bat`** - It auto-detects and fixes issues
2. **Check error messages** - They now tell you exactly what's wrong
3. **Keep it simple** - Don't manually edit code unless instructed
4. **Verify Python** - Run `python --version` before troubleshooting

---

## 📞 Support Checklist

- [ ] Run `run_app.bat`
- [ ] Check error message in terminal
- [ ] Read relevant documentation file
- [ ] Try deleting `venv` and running again
- [ ] If Python error, read `PYTHON_FIX.md`
- [ ] If general error, read `SETUP_GUIDE.md`

---

**Last Updated**: January 19, 2026  
**Status**: Production Ready ✅
