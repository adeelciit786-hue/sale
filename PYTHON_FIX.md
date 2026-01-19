# 🔧 FIXING PYTHON CORRUPTION - STEP BY STEP

## 🚨 Your Issue
Your Python 3.14 installation is corrupted. The system can't find critical library files even though the folder exists.

---

## ✅ SOLUTION: Reinstall Python (15 minutes)

### Step 1: Uninstall Python 3.14

#### Method A: Using Settings (Recommended)
1. Press `Win + I` to open Settings
2. Go to: **Apps → Installed apps**
3. Search for: **"Python"**
4. Click on **"Python 3.14"**
5. Click **"Uninstall"**
6. Follow the uninstall wizard
7. Click **"Yes"** when it asks to remove

#### Method B: Using Control Panel
1. Press `Win + R`
2. Type: `appwiz.cpl`
3. Press Enter
4. Find: **"Python 3.14"** (or similar)
5. Right-click → **Uninstall**
6. Follow the wizard

**⏱️ Expected time**: 2-3 minutes  
**✓ After uninstall**: Restart your computer

---

### Step 2: Download Python 3.12 or 3.13

Go to: **https://www.python.org/downloads/**

**⚠️ IMPORTANT: Download Python 3.12 or 3.13, NOT 3.14**

#### Steps:
1. Click: **"Downloads"** menu at top
2. Choose: **"Python 3.12"** or **"Python 3.13"**
3. Click: Download Windows Installer (64-bit)
4. File will download to your Downloads folder

**Expected filename**:
- `python-3.12.x-amd64.exe` OR
- `python-3.13.x-amd64.exe`

---

### Step 3: Install Python (CRITICAL - Read Carefully)

1. **Open Downloads folder** and find the Python installer
2. **Double-click** the `.exe` file to start installer
3. **LOOK FOR THIS BOX** at the bottom:
   ```
   ☐ Add Python 3.12 to PATH
   ```
4. **✅ CLICK THE CHECKBOX** to check it (VERY IMPORTANT!)
5. Click: **"Install Now"** (or "Customize installation")
6. Wait for installation to complete (5 minutes)
7. Click: **"Finish"** or **"Close"**

**⚠️ If you don't check the PATH box, it won't work!**

---

### Step 4: Restart Your Computer

This is important! Python won't work until you restart.

1. Save any open work
2. Restart your computer
3. Wait for it to fully boot up

---

### Step 5: Verify Installation

Open Command Prompt (Press `Win + R`, type `cmd`, press Enter):

```bash
python --version
```

**You should see**:
```
Python 3.12.x
```

or

```
Python 3.13.x
```

**If you see a version number**: ✅ Success! Continue below.

**If you see "not found"**: 
- Reinstall Python and make SURE to check the PATH box
- Restart computer again

---

### Step 6: Set Up Your Application

Go to your project folder:

```powershell
cd "d:\CC Projects\CC Sales Dashboard"
```

Now run the setup:

```powershell
.\run_app.bat
```

Or manually:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r sales_app\requirements.txt
python sales_app\app.py
```

---

### Step 7: Access Your App

Open your browser and go to:
```
http://localhost:5000
```

**Login with**:
- Username: `Admin`
- Password: `Champ@123`

---

## ✅ Quick Checklist

- [ ] Uninstalled Python 3.14
- [ ] Restarted computer
- [ ] Downloaded Python 3.12 or 3.13
- [ ] Ran the installer
- [ ] **CHECKED the "Add Python to PATH" box** ← IMPORTANT!
- [ ] Clicked "Install Now"
- [ ] Restarted computer again
- [ ] Ran: `python --version` → Shows a version number
- [ ] Ran: `.\run_app.bat`
- [ ] App started successfully
- [ ] Opened: `http://localhost:5000`
- [ ] Login worked

---

## 🆘 If Still Not Working

### "Python not found" error

**Solution**:
1. Uninstall Python again
2. Download Python 3.12 (not 3.13 or 3.14)
3. Re-run installer
4. **CAREFULLY CHECK the "Add Python to PATH" box**
5. Restart computer
6. Try again

### "Can't find PATH checkbox"

**Solution**:
1. Click "Customize Installation" instead of "Install Now"
2. On the next screen, you'll see more options
3. Find and check: "Add Python to PATH"
4. Continue with installation

### "venv still won't create"

**Solution**:
```powershell
# Delete the old venv
Remove-Item venv -Recurse -Force

# Try creating new one
python -m venv venv

# If that fails, try:
py -3 -m venv venv
```

### "Setup script fails to run"

**Solution**:
1. Make sure venv was created successfully
2. Try manual installation:
   ```powershell
   venv\Scripts\activate
   pip install Flask pandas openpyxl plotly matplotlib
   python sales_app\app.py
   ```

---

## 📊 Installation Reference

| Step | Time | What To Do |
|------|------|-----------|
| 1 | 3 min | Uninstall Python 3.14 |
| 2 | 1 min | Restart computer |
| 3 | 2 min | Download Python 3.12/3.13 |
| 4 | 5 min | Run installer, CHECK PATH BOX |
| 5 | 1 min | Click Finish |
| 6 | 1 min | Restart computer |
| 7 | 1 min | Verify: `python --version` |
| 8 | 3 min | Run `.\run_app.bat` |
| **TOTAL** | **17 min** | **App works!** |

---

## 💡 Pro Tips

1. **Use Python 3.12** - Most stable version
2. **ALWAYS check "Add Python to PATH"** - This is the #1 cause of problems
3. **Restart after installation** - Don't skip this step
4. **If unsure, reinstall** - It's faster than troubleshooting

---

## 🎯 After Installation

Once Python is installed:
1. Run: `.\run_app.bat`
2. App starts on: `http://localhost:5000`
3. Done!

---

**Need more help?** Check the other documentation files:
- `SETUP_GUIDE.md` - General setup
- `QUICK_REFERENCE.md` - Quick tips
- `ACTION_PLAN.md` - What to do next

---

## Quick Start After Fresh Python Install

Once Python is freshly installed, use either:

**Option A: Batch File (Easiest)**
```bash
run_app.bat
```

**Option B: PowerShell**
```powershell
.\run_app.ps1
```

**Option C: Direct Command**
```bash
python -m venv venv
venv\Scripts\activate
pip install -r sales_app\requirements.txt
python sales_app\app.py
```

---

## If You Can't Reinstall Python

Contact your system administrator or try:
1. Use a different computer with working Python
2. Use Windows Subsystem for Linux (WSL) with Python
3. Use a Docker container with Python pre-installed

---

## What We've Added for Future Prevention

The following improvements have been made to prevent this issue:

### 1. **Automatic Dependency Checker** (`app.py`)
   - Checks for required packages on startup
   - Provides clear error messages if packages are missing
   - Prevents confusing runtime errors

### 2. **Setup Script** (`setup.ps1`)
   - Validates Python installation
   - Auto-creates/repairs virtual environment
   - Installs all dependencies
   - Verifies each package is importable

### 3. **Run Scripts**
   - **run_app.ps1** - PowerShell with detailed diagnostics
   - **run_app.bat** - Windows batch file (simplest)
   - Both auto-run setup if needed

### 4. **Error Handling in app.py**
   - Clear error messages for port conflicts
   - Better diagnostics for startup failures
   - User-friendly error display

### 5. **This Guide**
   - Clear troubleshooting steps
   - Prevents future corruption

---

## Contact for Help

If issues persist after reinstalling Python:
1. Run the diagnostic: `.\run_app.ps1`
2. Copy all error messages
3. Check that Python is in your PATH: `python --version`
4. Try reinstalling dependencies: `pip install --upgrade -r sales_app\requirements.txt`

