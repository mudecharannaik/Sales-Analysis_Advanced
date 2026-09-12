# Superstore Sales Analysis

A comprehensive data analysis project for the Superstore dataset, covering data quality assessment, exploratory analysis, statistical testing, time series forecasting, customer/product/geographic analytics, predictive modelling, and automated reporting.

## Project Structure

```
SalesAnalysis/
├── Data/
│   └── superstore_raw.csv              # Raw dataset (51,290 rows)
├── Documentation/                      # Project documentation
├── Excel/                              # Generated Excel reports
├── Logs/                               # Pipeline log files
├── Outputs/                            # Reports and summaries
├── Python/
│   ├── notebooks/                      # Jupyter notebooks (if any)
│   ├── scripts/                        # All analysis modules
│   │   ├── __init__.py
│   │   ├── config.py                   # Configuration, paths, logging
│   │   ├── data_loader.py              # Data ingestion
│   │   ├── data_quality.py             # Data quality profiling
│   │   ├── preprocessing.py            # Cleaning, imputation, feature engineering
│   │   ├── outlier_detection.py        # Z-score / IQR outlier detection
│   │   ├── eda.py                      # Exploratory data analysis helpers
│   │   ├── statistical_analysis.py     # Hypothesis testing
│   │   ├── time_series_analysis.py     # Decomposition, forecasting, anomalies
│   │   ├── customer_analytics.py       # RFM, CLV, repeat analysis
│   │   ├── product_analytics.py        # Category, Pareto, affinity
│   │   ├── geographic_analysis.py      # Geographic breakdowns
│   │   ├── predictive_modeling.py      # Random Forest / XGBoost models
│   │   ├── visualization.py            # Chart gallery (matplotlib/seaborn)
│   │   ├── sql_export.py               # SQLite export
│   │   ├── excel_export.py             # Excel workbook generation
│   │   ├── report_generator.py         # Markdown report generation
│   │   └── main.py                     # Main orchestrator
│   └── requirements.txt
├── Reports/
├── SQL/                                # SQLite database output
├── Visualizations/                     # Generated charts (PNG)
└── skills/                             # Analysis skills
```

## Setup Instructions

1. **Python 3.10+** is required.

2. **Install dependencies:**

   ```bash
   pip install -r Python/requirements.txt
   ```

3. **Optional dependencies** (pipeline degrades gracefully without them):
   - `prophet` - Facebook Prophet forecasting
   - `python-docx` - Word document generation
   - `mlxtend` - Advanced market basket analysis
   - `wordcloud` - Word cloud visualisations
   - `xgboost` - XGBoost model (falls back to Random Forest if absent)

4. **Place the raw dataset** at `Data/superstore_raw.csv`.

## How to Run

Execute the main orchestrator from the project root:

```bash
cd D:\All_Data_Projects\Final\GoodProjects\SalesAnalysis
python Python/scripts/main.py
```

The pipeline will:
1. Load and profile the raw data
2. Run data quality checks
3. Clean, impute and engineer features
4. Perform EDA and statistical tests
5. Run time series decomposition and forecasting
6. Compute customer RFM, CLV and repeat analysis
7. Analyse product categories, Pareto and affinity
8. Analyse geographic performance
9. Train predictive models (Random Forest + XGBoost if available)
10. Generate 25+ visualisation charts
11. Export data to SQLite
12. Create an Excel report
13. Generate a comprehensive markdown report

## Outputs

| Output | Location |
|--------|----------|
| Charts (PNG) | `Visualizations/` |
| SQLite DB | `SQL/superstore.db` |
| Excel Report | `Excel/SalesAnalysis_Report.xlsx` |
| Markdown Report | `Outputs/final_report.md` |
| Logs | `Logs/` |

## Dependencies

- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **matplotlib / seaborn** - Visualisation
- **plotly** - Interactive charts (optional)
- **scipy / statsmodels** - Statistics and time series
- **scikit-learn** - Machine learning
- **openpyxl / xlsxwriter** - Excel export
- **SQLAlchemy** - Database ORM
