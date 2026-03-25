# DataWrangler Pro 🔬

An AI-powered data preparation and visualization Streamlit application.

**Coursework Project — Data Wrangling & Visualization (5COSC038C)**
Student IDs: 00017592 & 00018555

## Features

- **Upload**: CSV, Excel, JSON, Google Sheets
- **Clean**: Missing values, duplicates, categorical tools, outlier treatment, scaling, column operations, data validation
- **Visualize**: 8 chart types (histogram, bar, scatter, line, box, heatmap, 3D scatter, pie) with download per chart
- **AI Assistant**: Claude-powered suggestions for cleaning and visualization
- **Export**: CSV, Excel, JSON + transformation report & recipe

## Sample Datasets

Located in `sample_data/`:
- `employee_data.csv` — 1,215 rows, HR/employee dataset with mixed types, missing values, duplicates
- `sales_data.csv` — 1,120 rows, retail sales dataset with datetime, numeric, and categorical columns

## Running Locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Live Demo

Deployed on Streamlit Cloud.
