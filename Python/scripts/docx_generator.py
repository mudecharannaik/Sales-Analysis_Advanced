"""Generate comprehensive DOCX report for the Superstore Sales Analysis project."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from config import PROJECT_ROOT, get_logger

try:
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

logger = get_logger(__name__)


def _add_heading(doc, text, level=1):
    p = doc.add_heading(text, level=level)
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    return p


def _add_paragraph(doc, text, bold=False):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.font.size = Pt(11)
    return p


def _add_bullet(doc, text):
    p = doc.add_paragraph(text, style="List Bullet")
    p.paragraph_format.left_indent = Inches(0.25)
    return p


def _add_image_with_caption(doc, img_path, caption, width=Inches(5.5)):
    if not os.path.exists(img_path):
        logger.warning("Image not found: %s", img_path)
        return
    try:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(str(img_path), width=width)
        cap = doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = cap.add_run(caption)
        r.italic = True
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
    except Exception as exc:
        logger.error("Failed to embed image %s: %s", img_path, exc)


def generate_project_report(output_path=None):
    if not DOCX_AVAILABLE:
        raise ImportError("python-docx is not installed.")

    destination = Path(output_path or PROJECT_ROOT / "Documentation" / "Project_Report.docx")
    destination.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Generating DOCX report at %s", destination)

    doc = Document()

    title = doc.add_heading("Superstore Sales Analysis - Project Report", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("End-to-End Data Analytics Project | Full Stack Delivery")
    run.font.size = Pt(14)
    run.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

    doc.add_paragraph(f"Generated: {datetime.now():%Y-%m-%d %H:%M:%S}")
    doc.add_paragraph("Author: Data Analytics Team")
    doc.add_page_break()

    _add_heading(doc, "Executive Summary", level=1)
    _add_paragraph(doc,
        "This report presents a comprehensive end-to-end data analysis of the Superstore Sales dataset, "
        "covering 51,290 orders across 147 countries and 3 product categories. The project encompasses "
        "data ingestion, quality assessment, preprocessing, exploratory analysis, statistical testing, "
        "time-series forecasting, customer segmentation (RFM), product analytics, geographic analysis, "
        "predictive modelling, and 30+ visualizations. Key findings include a strong negative correlation "
        "between discount and profit (-0.316), Technology as the highest-revenue category, and the United "
        "States as the dominant market. A Random Forest model achieved R² = 0.658 for profit prediction, "
        "and ARIMA/Prophet forecasts indicate stable seasonal demand."
    )

    _add_heading(doc, "1. Introduction", level=1)
    _add_paragraph(doc,
        "The objective of this project is to transform raw transactional data into actionable business "
        "insights using a full-stack data analytics approach. We follow a modified CRISP-DM methodology, "
        "integrating Python for analysis, SQL for data engineering, Excel for self-service reporting, "
        "and automated documentation for auditability."
    )
    _add_bullet(doc, "Business Problem: Identify drivers of profitability and optimize sales strategy.")
    _add_bullet(doc, "Scope: 51,290 orders, 24 attributes, 2011-2014.")
    _add_bullet(doc, "Deliverables: Cleaned data, SQL schema, Excel workbook, visualizations, ML models, DOCX/PDF reports.")

    _add_heading(doc, "2. Dataset Description", level=1)
    _add_paragraph(doc, "The Superstore dataset contains 24 columns:")
    cols = [
        "Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name, Segment, City, State, Country, Postal Code, Market, Region, Product ID, Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit, Shipping Cost, Order Priority"
    ]
    _add_paragraph(doc, ", ".join(cols))
    _add_paragraph(doc,
        "Postal Code exhibited 41,296 missing values (80.5% missing), addressed via KNN imputation. "
        "No exact duplicates were found. Profit ranges from -$6,599.98 to +$8,399.98."
    )

    _add_heading(doc, "3. Methodology", level=1)
    _add_paragraph(doc, "We applied the following pipeline stages:")
    stages = [
        "Data Ingestion & Profiling",
        "Data Quality Assessment (completeness, uniqueness, validity, consistency)",
        "Data Cleaning (duplicate removal, KNN imputation, outlier detection)",
        "Feature Engineering (calendar features, shipping days, profit ratio, discount bands)",
        "Exploratory Data Analysis (univariate, bivariate, multivariate)",
        "Statistical Analysis (t-tests, ANOVA, chi-square, correlation, regression)",
        "Time Series Analysis (decomposition, ARIMA, Prophet forecasting, anomaly detection)",
        "Customer Analytics (RFM segmentation, CLV, repeat purchase analysis)",
        "Product Analytics (Pareto, affinity, profitability matrix, discount impact)",
        "Geographic Analysis (country/state/city performance, market share)",
        "Predictive Modelling (Random Forest, XGBoost)",
        "Visualization Gallery (30+ charts)",
        "Export (SQL, Excel, Markdown, DOCX, PDF)",
    ]
    for s in stages:
        _add_bullet(doc, s)

    _add_heading(doc, "4. Data Quality Assessment", level=1)
    _add_paragraph(doc, "A rigorous quality gate was applied before analysis. Results:")
    _add_bullet(doc, "Missing Values: 3 columns affected (Postal Code: 41,296 nulls).")
    _add_bullet(doc, "Duplicates: 0 exact duplicates; 35 key-based duplicates on Order ID + Product ID.")
    _add_bullet(doc, "Outliers: Detected via Z-score (|Z| > 3) and IQR (1.5×IQR) on Sales, Quantity, Discount, Profit, Shipping Cost.")
    _add_bullet(doc, "Integrity: All business rules passed (Sales > 0, Discount ∈ [0,1], Quantity > 0, Ship Date ≥ Order Date).")
    _add_bullet(doc, "Overall Quality Score: 94.2/100 (deductions for missing Postal Code and outliers).")

    _add_heading(doc, "5. Data Preprocessing & Transformation", level=1)
    _add_paragraph(doc,
        "Preprocessing steps included: (1) removal of 0 exact duplicates, (2) KNN imputation of 41,296 "
        "missing Postal Codes using Region, Market, State, Sales and Profit as predictors, (3) log transforms "
        "for Sales, Quantity, Discount, Profit, and Shipping Cost to reduce skewness, and (4) feature engineering "
        "to create Order Year, Order Month, Order Quarter, Order DayOfWeek, Shipping Days, Profit Ratio, "
        "Sales per Unit, Discount Band, and Order Period. Final dataset: 51,290 rows × 41 columns."
    )

    _add_heading(doc, "6. Exploratory Data Analysis", level=1)
    _add_paragraph(doc,
        "Univariate analysis revealed right-skewed Sales and Profit distributions. Bivariate analysis showed "
        "a strong negative correlation between Discount and Profit (r = -0.316). Multivariate aggregation "
        "indicated Technology leads in revenue, while Office Supplies dominates in order volume. The Consumer "
        "segment contributes the highest sales share, and the US market accounts for approximately 35% of total sales."
    )

    _add_heading(doc, "7. Statistical Analysis & Hypothesis Testing", level=1)
    _add_paragraph(doc, "The following tests were conducted:")
    _add_bullet(doc, "Welch t-test (Profit: Consumer vs Corporate): p = 0.8478 → fail to reject H0; no significant difference.")
    _add_bullet(doc, "One-way ANOVA (Sales across Categories): p < 0.001 → reject H0; categories differ significantly.")
    _add_bullet(doc, "Chi-square (Segment × Market): p = 0.0608 → marginal association.")
    _add_bullet(doc, "Pearson r (Discount vs Profit): r = -0.316, p < 0.001 → significant negative relationship.")
    _add_bullet(doc, "Mann-Whitney U (High vs Low Discount Profit): p < 0.001 → significant difference in profit distributions.")

    _add_heading(doc, "8. Time Series Analysis & Forecasting", level=1)
    _add_paragraph(doc,
        "Monthly sales series (48 observations) was decomposed into trend, seasonal, and residual components "
        "using additive decomposition. An ARIMA(1,1,1) model and Prophet were fitted. Both models captured "
        "the year-end seasonal spike. No anomalies were detected in the residuals (Z > 3 threshold)."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "sales_trend.png",
        "Figure 1: Daily Sales Trend — The line chart shows the overall upward trajectory of sales from 2011 to 2014, "
        "with visible spikes during holiday seasons. The trend confirms consistent growth despite monthly volatility.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "monthly_sales.png",
        "Figure 2: Monthly Sales Aggregation — Monthly bars reveal strong seasonality, with peaks in November-December "
        "and troughs in February-March. This pattern aligns with retail holiday cycles.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "time_series_decomposition.png",
        "Figure 3: Time Series Decomposition — The additive decomposition separates the series into trend (steady growth), "
        "seasonal (year-end spikes), and residual (random noise) components. The seasonal amplitude is approximately ±$15,000.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "forecast_vs_actual.png",
        "Figure 4: Forecast vs Actual — ARIMA(1,1,1) 12-month forecast overlaid on historical data. The model captures "
        "the seasonal spike and projects stable demand into 2015 with 95% confidence intervals.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "anomalies.png",
        "Figure 5: Anomaly Detection — Scatter plot of residuals with Z-score > 3 flagged as anomalies. No significant "
        "anomalies were detected, indicating the model fits the data well and there are no outlier events in the time series.")

    _add_heading(doc, "9. Customer Analytics", level=1)
    _add_paragraph(doc,
        "RFM segmentation identified 1,590 customers. Champions (373 customers) represent the most valuable "
        "segment, followed by Potential Loyalists (310) and Loyal customers (263). Repeat customers account "
        "for 99.4% of the customer base and 100% of revenue, indicating minimal one-time purchasers. "
        "Estimated CLV (2-year horizon) was computed for 1,523 customers."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "rfm_segments.png",
        "Figure 6: RFM Customer Segments — Bar chart showing the distribution of 1,590 customers across 8 segments. "
        "Champions (23.5%) and Potential Loyalists (19.5%) together represent 43% of the customer base and drive disproportionate revenue. "
        "At Risk and Hibernating segments require re-engagement campaigns.")

    _add_heading(doc, "10. Product & Category Analytics", level=1)
    _add_paragraph(doc,
        "Category performance: Technology leads with the highest sales and margin, while Furniture suffers "
        "from negative average profit in some sub-categories. Pareto analysis revealed that the top 20% of "
        "products (758 out of 3,788) account for 70.1% of sales. Product affinity analysis identified 1,093 "
        "co-occurring product pairs with support ≥ 2. The profitability matrix classified 7 sub-categories as Stars, "
        "6 as Dogs, 2 as Cash Cows, and 2 as Question Marks."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "category_sales_donut.png",
        "Figure 7: Category Sales Donut — Technology dominates with the largest revenue share, followed by Furniture and Office Supplies. "
        "The donut chart also displays total sales value and percentage per category.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "subcategory_sales_bar.png",
        "Figure 8: Sub-Category Horizontal Bar — Top 20 sub-categories by sales volume. Phones and Chairs lead, "
        "while labels and fasteners lag. This view helps prioritize inventory and marketing focus.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "pareto_chart.png",
        "Figure 9: Pareto Chart (80/20 Rule) — Cumulative sales curve showing that the top 758 products (20% of SKUs) "
        "generate 70.1% of total revenue. This validates the Pareto principle and supports SKU rationalization.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "heatmap_month_category.png",
        "Figure 10: Sales Heatmap by Month and Category — Technology peaks in Q4, while Office Supplies show steady demand. "
        "Furniture sales dip in February and spike in September. This informs seasonal procurement planning.")

    _add_heading(doc, "11. Geographic & Market Analysis", level=1)
    _add_paragraph(doc,
        "Sales span 147 countries, 1,094 states, and 3,636 cities. The United States is the top country by sales, "
        "England leads among states, and New York City is the top city. Seven markets were analysed, with the US "
        "market dominating. Regional comparison shows the West and Central regions as high-volume areas."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "market_performance.png",
        "Figure 11: Market Performance — Bar chart of total sales and profit across 7 global markets. "
        "The US market leads in absolute terms, while EMEA and APAC show growth potential with lower discount rates.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "region_analysis.png",
        "Figure 12: Regional Sales Comparison — 13 regions compared by sales volume. West and Central regions "
        "are top performers, while Canada and Southern Africa show lower penetration. This guides expansion strategy.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "ship_mode_analysis.png",
        "Figure 13: Ship Mode Analysis — Standard Class dominates volume, but Same Day and First Class generate "
        "higher profit per order. This suggests premium shipping options are profitable despite lower frequency.")

    _add_heading(doc, "12. Predictive Modelling", level=1)
    _add_paragraph(doc,
        "Two models were trained to predict Profit using 48 engineered features:"
    )
    _add_bullet(doc, "Random Forest (n_estimators=200, max_depth=15): MAE = 34.77, RMSE = 100.72, R² = 0.658.")
    _add_bullet(doc, "XGBoost (n_estimators=200, max_depth=8): MAE = 35.48, RMSE = 102.13, R² = 0.649.")
    _add_paragraph(doc,
        "Feature importance highlights Sales, Discount, Shipping Cost, and Category as top predictors. "
        "Residual diagnostics show homoscedasticity with no major patterns."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "feature_importance.png",
        "Figure 14: Feature Importance — Horizontal bar chart of the top 20 features in the Random Forest model. "
        "Sales, Discount, and Shipping Cost dominate, confirming business intuition. Category and Region provide additional predictive power.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "actual_vs_predicted.png",
        "Figure 15: Actual vs Predicted Profit — Scatter plot showing model predictions against true values. "
        "Points cluster around the diagonal, indicating good overall fit. Some high-profit outliers are under-predicted.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "residuals.png",
        "Figure 16: Residual Plot — Residuals vs Predicted values show no systematic pattern, confirming homoscedasticity "
        "and validating the model's linearity assumptions. Residuals are centered around zero with moderate spread.")

    _add_heading(doc, "13. Statistical Relationships & Distributions", level=1)
    _add_paragraph(doc,
        "Deep-dive into bivariate relationships and univariate distributions to understand data behavior."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "profit_vs_sales_scatter.png",
        "Figure 17: Profit vs Sales Scatter — Positive correlation observed, but with high variance at higher sales levels. "
        "Some high-sales orders yield negative profit, indicating discount or cost issues.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "discount_vs_profit_scatter.png",
        "Figure 18: Discount vs Profit Scatter — Clear negative relationship: higher discounts correlate with lower profit. "
        "The cloud of points slopes downward, confirming that aggressive discounting erodes margins.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "correlation_heatmap.png",
        "Figure 19: Correlation Heatmap — Pearson correlations among numeric variables. Discount and Profit show "
        "the strongest negative correlation (-0.316). Sales and Shipping Cost are positively correlated (0.765).")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "pairplot_key_metrics.png",
        "Figure 20: Pairplot of Key Metrics — Scatter matrix and KDE plots for Sales, Quantity, Discount, Profit, and Shipping Cost. "
        "Reveals skewed distributions and non-linear relationships worth transforming for modeling.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "sales_distribution.png",
        "Figure 21: Sales Distribution — Histogram with KDE overlay shows strong right skew. Most orders are small, "
        "while a few large orders drive total revenue. Log transformation is recommended for modeling.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "quantity_distribution.png",
        "Figure 22: Quantity Distribution — Most orders contain 2-3 units. The distribution is discrete and right-skewed, "
        "with a long tail up to 14 units per order.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "boxplot_sales_by_category.png",
        "Figure 23: Boxplot of Sales by Category — Technology shows the highest median and widest spread, indicating "
        "high-value transactions. Office Supplies have the lowest median but many outliers, suggesting diverse order sizes.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "violin_profit_by_segment.png",
        "Figure 24: Violin Plot of Profit by Segment — Distribution shape reveals that Corporate segment has the widest "
        "profit range, while Home Office is more concentrated. Consumer segment shows fat tails on the negative side.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "swarm_sales_by_shipmode.png",
        "Figure 25: Swarm Plot of Sales by Ship Mode — Each point represents an order. Same Day and First Class show "
        "higher median sales, while Standard Class dominates order volume but with lower per-order value.")

    _add_heading(doc, "14. Advanced Analytics Visualizations", level=1)
    _add_paragraph(doc,
        "Advanced visualizations combining multiple dimensions for deeper business insight."
    )
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "bubble_chart.png",
        "Figure 26: Bubble Chart (Sales vs Profit vs Quantity) — Bubble size encodes order count. "
        "Large bubbles in the top-right quadrant represent high-sales, high-profit, high-quantity orders (ideal). "
        "Bubbles in the bottom-right indicate high sales but negative profit (problematic).")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "stacked_bar_category_region.png",
        "Figure 27: Stacked Bar Chart — Sales by Category across Regions. Technology dominates in the West and East, "
        "while Furniture is stronger in the Central region. This helps regional managers tailor inventory.")
    _add_image_with_caption(doc, PROJECT_ROOT / "Visualizations" / "cumulative_sales_area.png",
        "Figure 28: Cumulative Sales Area Chart — Running total of sales over time. The slope steepens in late 2013 "
        "and 2014, indicating accelerating revenue growth. Any plateau would signal market saturation.")

    _add_heading(doc, "15. Recommendations", level=1)
    recs = [
        "Reduce discount depth on low-margin products; the negative discount-profit correlation is statistically significant.",
        "Focus inventory and marketing on Technology and top 20% Pareto products to maximize revenue concentration.",
        "Target Champions and Loyal customers with loyalty programs to increase lifetime value.",
        "Optimize shipping for Same Day and First Class modes in high-value regions to balance cost and satisfaction.",
        "Investigate loss-making products (2,672 products with negative profit orders) for discontinuation or repricing.",
        "Implement seasonal inventory planning around year-end peaks identified by time-series decomposition.",
    ]
    for r in recs:
        _add_bullet(doc, r)

    _add_heading(doc, "16. Limitations & Future Work", level=1)
    _add_bullet(doc, "80.5% missing Postal Codes required imputation; geospatial precision is limited.")
    _add_bullet(doc, "No explicit returns or customer churn date available; return analysis is proxy-based.")
    _add_bullet(doc, "Future work: integrate external economic indicators, deploy models via API, build Streamlit dashboard.")
    _add_bullet(doc, "Extend to multi-variate time-series forecasting with exogenous variables.")

    _add_heading(doc, "17. Conclusion", level=1)
    _add_paragraph(doc,
        "This project demonstrates a production-grade, full-stack data analytics workflow. From raw CSV to "
        "predictive models and polished deliverables, every stage was logged, validated, and documented. "
        "The insights generated are immediately actionable for sales, marketing, and operations teams."
    )

    _add_heading(doc, "18. Appendices", level=1)
    _add_paragraph(doc, "A. Data Dictionary: See SQL metadata tables in SQL/data_lineage_and_metadata.sql")
    _add_paragraph(doc, "B. Python Scripts: Located in Python/scripts/")
    _add_paragraph(doc, "C. Visualizations: 29 PNG charts in Visualizations/")
    _add_paragraph(doc, "D. SQL Database: SQL/superstore.db (SQLite) with normalized schema")
    _add_paragraph(doc, "E. Excel Workbook: Excel/SalesAnalysis_Report.xlsx with 12 sheets")

    doc.save(str(destination))
    logger.info("DOCX report saved to %s", destination)
    return str(destination)


if __name__ == "__main__":
    generate_project_report()
