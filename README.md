# 🔬 DataWrangler Pro

**AI-Powered Data Preparation & Visualization Studio**
Data Wrangling & Visualization Coursework (5COSC038C) · IDs: 00017592 & 00018555

---

## 🚀 Quick Start

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📂 Project Structure

```
datawrangler/
├── streamlit_app.py          # Home page & navigation
├── utils.py                  # Shared theme, CSS, Plotly helpers
├── theme.py                  # Alias for utils.py (backward compat)
├── requirements.txt
├── README.md
├── sample_data/
│   ├── employee_dataset.csv  # 1530 rows, 12 cols, mixed types + missing
│   └── sales_dataset.csv     # 1220 rows, 13 cols, time-series + categories
└── pages/
    ├── 1_Upload.py           # Page A – Upload & Data Profile
    ├── 2_Cleaning.py         # Page B – Cleaning & Preparation Studio
    ├── 3_Visualization.py    # Page C – Visualization Builder (12 chart types)
    ├── 4_Export.py           # Page D – Export & Report
    └── 5_AI_Assistant.py     # AI Assistant (Claude-powered)
```

## ✅ Features

### Page A – Upload & Profile
- CSV, Excel (.xlsx), JSON upload + Google Sheets integration
- Shape, dtypes, missing values, duplicates, summary stats
- Reset session button

### Page B – Cleaning & Preparation
- Missing values (drop, mean/median/mode, ffill/bfill, constant)
- Duplicate detection & removal (full row or subset)
- Type conversion (numeric, string, datetime with dirty-numeric cleaning)
- Categorical tools (case, mapping, rare grouping, one-hot encoding)
- Outlier detection (IQR / Z-score) + remove or winsorize
- Normalization (Min-Max, Z-score) with before/after stats
- Column operations: rename, drop, create (formula), bin
- Data validation rules with violations export
- Undo last step + transformation log

### Page C – Visualization Builder
- **12 chart types:** Histogram, Bar, Grouped Bar, Scatter (with OLS trendline), Line, Box, Violin, Correlation Heatmap, **3D Scatter**, Pie/Donut, Area, Bubble
- Analytical Dashboard (6 always-on charts)
- Matplotlib section (histogram, KDE, box, violin)
- Every chart: full axis labels, titles, legends
- Download PNG (kaleido) + interactive HTML after each chart
- Global filters (category + numeric range)
- Smart Interpretation (skewness, outliers, mean vs median)
- Dark/light mode aware chart colors

### Page D – Export & Report
- Export CSV, Excel, JSON
- Transformation Report (human-readable JSON)
- Transformation Recipe (machine-readable JSON for replay)

### AI Assistant (Page 5)
- Toggle on/off (app works fully without it)
- Modes: free chat, cleaning suggestions, viz recommendations, full analysis
- Uses Claude claude-sonnet-4-20250514 via Anthropic API
- Always-visible rule-based fallback suggestions (no API needed)
- Dataset profile shown to AI for context-aware advice

## 🌙 Dark Mode
Toggle in the sidebar on every page.

## 📦 Sample Datasets
| Dataset | Rows | Cols | Features |
|---------|------|------|---------|
| employee_dataset.csv | 1530 | 12 | Missing values, duplicates, mixed types |
| sales_dataset.csv | 1220 | 13 | Time series, categories, revenue metrics |
