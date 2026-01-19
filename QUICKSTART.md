# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- Windows PowerShell or Command Prompt

### Step 1: Create Virtual Environment
```powershell
cd "d:\CC Projects\CC Sales Dashboard"
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 2: Install Dependencies
```bash
cd sales_app
pip install -r requirements.txt
```

### Step 3: Run the Application
```bash
python app.py
```

You'll see:
```
 * Running on http://127.0.0.1:5000
```

### Step 4: Open in Browser
Navigate to: **http://127.0.0.1:5000**

---

## 📊 First Time Setup

1. **Visit Upload Data Tab**
2. **Upload Historical Files** (sample files provided):
   - `August2025.xlsx`
   - `September2025.xlsx`
3. **Upload Current Month**:
   - `January2026.xlsx`
4. **Set Monthly Target**:
   - Enter: `3000000` (3 million AED)
   - Click: Save Target
5. **View Dashboard**
   - See KPIs populate
   - Review all 6 graphs

---

## 📁 Project Files Included

Sample data files are in: `sales_app/data/`

- **historical/**: Historical sales files
  - August2025.xlsx
  - September2025.xlsx
- **current/**: Current month file
  - January2026.xlsx
- **targets.json**: Stores target values (auto-created)

---

## 🎯 Key Features

| Feature | Location | Use |
|---------|----------|-----|
| Dashboard | Home page | View KPIs & graphs |
| Upload Data | Tab "Upload Data" | Add/manage files |
| About | Tab "About" | Learn methodology |
| Settings | n/a | Not included (admin-only) |

---

## 💡 Tips

- **Graphs are interactive**: Hover, zoom, pan on any graph
- **File names matter**: Use descriptive names (e.g., "August2025.xlsx")
- **TOTAL row ignored**: Last row labeled "TOTAL" is auto-excluded
- **Target persists**: Monthly targets saved even after restart

---

## 🔧 Troubleshooting

**Issue**: "ModuleNotFoundError: No module named 'flask'"
- **Solution**: Ensure virtual environment is activated

**Issue**: Port 5000 already in use
- **Solution**: Kill existing process or edit port in `app.py` (line 271)

**Issue**: Dashboard shows no graphs
- **Solution**: Upload historical files first

**Issue**: "Cannot open Excel file"
- **Solution**: Verify .xlsx format and data structure matches specification in README

---

## 📦 Deployment

### Deploy to Render (Free)

1. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push
   ```

2. Connect Render:
   - Go to https://render.com
   - New > Web Service
   - Connect GitHub repo
   - Build command: `pip install -r sales_app/requirements.txt`
   - Start command: `gunicorn -w 4 -b 0.0.0.0:$PORT sales_app.app:app`
   - Deploy!

3. Access your app:
   - Render provides a unique URL
   - Data persists across restarts (local storage)

---

## ❓ Support

Refer to [README.md](README.md) for:
- Detailed feature documentation
- Excel file format specifications
- Forecasting algorithm details
- API endpoints reference

---

**Happy Forecasting! 📈**
