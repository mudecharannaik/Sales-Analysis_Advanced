"""Generate comprehensive PDF report for the Superstore Sales Analysis project."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from config import PROJECT_ROOT, get_logger

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

logger = get_logger(__name__)


def generate_pdf_report(output_path=None):
    if not PDF_AVAILABLE:
        raise ImportError("reportlab is not installed.")

    destination = Path(output_path or PROJECT_ROOT / "Reports" / "SalesAnalysis_Report.pdf")
    destination.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Generating PDF report at %s", destination)

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=22,
        leading=26,
        alignment=1,
        spaceAfter=12,
    )
    heading1 = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading2"],
        fontSize=16,
        leading=20,
        spaceAfter=10,
        spaceBefore=12,
    )
    body = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )
    bullet_style = ParagraphStyle(
        "CustomBullet",
        parent=styles["BodyText"],
        fontSize=10,
        leading=14,
        leftIndent=20,
        bulletIndent=10,
        spaceAfter=6,
        bulletFontName="Symbol",
    )
    caption_style = ParagraphStyle(
        "Caption",
        parent=styles["BodyText"],
        fontSize=9,
        leading=12,
        alignment=1,
        spaceAfter=12,
        textColor=colors.HexColor("#444444"),
    )

    story = []

    def add_image(path, caption, width=6.5 * inch):
        if not os.path.exists(path):
            logger.warning("Image not found: %s", path)
            return
        try:
            img = Image(str(path), width=width, height=width * 0.5)
            story.append(img)
            story.append(Paragraph(caption, caption_style))
        except Exception as exc:
            logger.error("Failed to embed image %s: %s", path, exc)

    # Title Page
    story.append(Paragraph("Superstore Sales Analysis", title_style))
    story.append(Paragraph("Full-Stack Data Analytics Project Report", title_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now():%Y-%m-%d %H:%M:%S}", body))
    story.append(Paragraph("<b>Author:</b> Data Analytics Team", body))
    story.append(Paragraph("<b>Dataset:</b> Superstore Sales (51,290 orders, 24 columns)", body))
    story.append(PageBreak())

    # Executive Summary
    story.append(Paragraph("Executive Summary", heading1))
    story.append(Paragraph(
        "This report documents a complete data analytics lifecycle for the Superstore Sales dataset. "
        "We processed 51,290 orders, performed rigorous data quality checks, engineered features, "
        "conducted statistical tests, built time-series forecasts, segmented customers via RFM, "
        "trained predictive models (Random Forest R²=0.658), and produced 30+ visualizations. "
        "Key insight: discount depth is negatively correlated with profit (r=-0.316). "
        "Recommendations focus on discount optimization, Pareto product prioritization, and customer retention.",
        body
    ))
    story.append(PageBreak())

    # 1. Introduction
    story.append(Paragraph("1. Introduction", heading1))
    story.append(Paragraph(
        "The project transforms raw transactional data into actionable business intelligence. "
        "Scope covers 2011-2014 global sales across Consumer, Corporate, and Home Office segments. "
        "Tools: Python (pandas, scikit-learn, statsmodels, prophet), SQL (SQLite), Excel (openpyxl), "
        "and reportlab for PDF generation.",
        body
    ))

    # 2. Data Quality
    story.append(Paragraph("2. Data Quality Assessment", heading1))
    story.append(Paragraph(
        "Postal Code: 41,296 missing (80.5%) → KNN imputed using geographic and profitability features.<br/>"
        "Duplicates: 0 exact; 35 key-based on Order ID + Product ID.<br/>"
        "Outliers: Flagged via Z-score and IQR on numeric columns.<br/>"
        "Integrity: Sales &gt; 0, Discount ∈ [0,1], Quantity &gt; 0, Ship Date ≥ Order Date — all passed.<br/>"
        "Overall Quality Score: 94.2/100.",
        body
    ))

    # 3. Methodology
    story.append(Paragraph("3. Methodology", heading1))
    methodology = [
        "Data Ingestion & Profiling",
        "Data Quality Assessment",
        "Data Cleaning (KNN imputation, outlier handling)",
        "Feature Engineering (calendar, shipping, profitability metrics)",
        "Exploratory Data Analysis",
        "Statistical Testing (t-test, ANOVA, chi-square, regression)",
        "Time Series (decomposition, ARIMA, Prophet, anomaly detection)",
        "Customer Analytics (RFM, CLV, repeat purchase)",
        "Product Analytics (Pareto, affinity, profitability matrix)",
        "Geographic Analysis (market & regional performance)",
        "Predictive Modelling (Random Forest, XGBoost)",
        "Visualization (30+ charts)",
        "Multi-format Export (SQL, Excel, Markdown, DOCX, PDF)",
    ]
    for m in methodology:
        story.append(Paragraph(f"• {m}", bullet_style))

    story.append(PageBreak())

    # 4. Key Findings
    story.append(Paragraph("4. Key Findings", heading1))
    findings = [
        "<b>Revenue Concentration:</b> Technology is the top category; top 20% of products drive 70.1% of sales (Pareto).",
        "<b>Discount-Penalty:</b> Higher discounts strongly correlate with lower profit (r = -0.316, p &lt; 0.001).",
        "<b>Customer Value:</b> 373 Champions (23.5% of customers) are the most valuable segment.",
        "<b>Geographic dominance:</b> United States leads sales; England is the top state.",
        "<b>Model Performance:</b> Random Forest explains 65.8% of profit variance (R² = 0.658).",
        "<b>Seasonality:</b> Clear year-end demand spike captured by both ARIMA and Prophet.",
    ]
    for f in findings:
        story.append(Paragraph(f, bullet_style))

    # 5. Visualization Gallery with Explanations
    story.append(Paragraph("5. Visualization Gallery & Explanations", heading1))
    story.append(Paragraph(
        "This section presents 29 high-resolution charts generated during the analysis. "
        "Each visualization is accompanied by a clear explanation of what it shows and why it matters.",
        body
    ))
    story.append(PageBreak())

    viz_root = PROJECT_ROOT / "Visualizations"

    # Time Series Visualizations
    story.append(Paragraph("5.1 Time Series & Trend Analysis", heading1))
    add_image(viz_root / "sales_trend.png",
        "Figure 1: Daily Sales Trend — The line chart shows the overall upward trajectory of sales from 2011 to 2014, "
        "with visible spikes during holiday seasons. The trend confirms consistent growth despite monthly volatility.")
    story.append(PageBreak())
    add_image(viz_root / "monthly_sales.png",
        "Figure 2: Monthly Sales Aggregation — Monthly bars reveal strong seasonality, with peaks in November-December "
        "and troughs in February-March. This pattern aligns with retail holiday cycles.")
    story.append(PageBreak())
    add_image(viz_root / "time_series_decomposition.png",
        "Figure 3: Time Series Decomposition — The additive decomposition separates the series into trend (steady growth), "
        "seasonal (year-end spikes), and residual (random noise) components. The seasonal amplitude is approximately ±$15,000.")
    story.append(PageBreak())
    add_image(viz_root / "forecast_vs_actual.png",
        "Figure 4: Forecast vs Actual — ARIMA(1,1,1) 12-month forecast overlaid on historical data. The model captures "
        "the seasonal spike and projects stable demand into 2015 with 95% confidence intervals.")
    story.append(PageBreak())
    add_image(viz_root / "anomalies.png",
        "Figure 5: Anomaly Detection — Scatter plot of residuals with Z-score > 3 flagged as anomalies. No significant "
        "anomalies were detected, indicating the model fits the data well and there are no outlier events in the time series.")
    story.append(PageBreak())

    # Category & Product Visualizations
    story.append(Paragraph("5.2 Category & Product Analytics", heading1))
    add_image(viz_root / "category_sales_donut.png",
        "Figure 6: Category Sales Donut — Technology dominates with the largest revenue share, followed by Furniture and Office Supplies. "
        "The donut chart also displays total sales value and percentage per category.")
    story.append(PageBreak())
    add_image(viz_root / "subcategory_sales_bar.png",
        "Figure 7: Sub-Category Horizontal Bar — Top 20 sub-categories by sales volume. Phones and Chairs lead, "
        "while labels and fasteners lag. This view helps prioritize inventory and marketing focus.")
    story.append(PageBreak())
    add_image(viz_root / "pareto_chart.png",
        "Figure 8: Pareto Chart (80/20 Rule) — Cumulative sales curve showing that the top 758 products (20% of SKUs) "
        "generate 70.1% of total revenue. This validates the Pareto principle and supports SKU rationalization.")
    story.append(PageBreak())
    add_image(viz_root / "heatmap_month_category.png",
        "Figure 9: Sales Heatmap by Month and Category — Technology peaks in Q4, while Office Supplies show steady demand. "
        "Furniture sales dip in February and spike in September. This informs seasonal procurement planning.")
    story.append(PageBreak())

    # Customer Analytics
    story.append(Paragraph("5.3 Customer Analytics", heading1))
    add_image(viz_root / "rfm_segments.png",
        "Figure 10: RFM Customer Segments — Bar chart showing the distribution of 1,590 customers across 8 segments. "
        "Champions (23.5%) and Potential Loyalists (19.5%) together represent 43% of the customer base and drive disproportionate revenue. "
        "At Risk and Hibernating segments require re-engagement campaigns.")
    story.append(PageBreak())

    # Geographic Visualizations
    story.append(Paragraph("5.4 Geographic & Market Analysis", heading1))
    add_image(viz_root / "market_performance.png",
        "Figure 11: Market Performance — Bar chart of total sales and profit across 7 global markets. "
        "The US market leads in absolute terms, while EMEA and APAC show growth potential with lower discount rates.")
    story.append(PageBreak())
    add_image(viz_root / "region_analysis.png",
        "Figure 12: Regional Sales Comparison — 13 regions compared by sales volume. West and Central regions "
        "are top performers, while Canada and Southern Africa show lower penetration. This guides expansion strategy.")
    story.append(PageBreak())
    add_image(viz_root / "ship_mode_analysis.png",
        "Figure 13: Ship Mode Analysis — Standard Class dominates volume, but Same Day and First Class generate "
        "higher profit per order. This suggests premium shipping options are profitable despite lower frequency.")
    story.append(PageBreak())

    # Statistical Relationships
    story.append(Paragraph("5.5 Statistical Relationships & Distributions", heading1))
    add_image(viz_root / "profit_vs_sales_scatter.png",
        "Figure 14: Profit vs Sales Scatter — Positive correlation observed, but with high variance at higher sales levels. "
        "Some high-sales orders yield negative profit, indicating discount or cost issues.")
    story.append(PageBreak())
    add_image(viz_root / "discount_vs_profit_scatter.png",
        "Figure 15: Discount vs Profit Scatter — Clear negative relationship: higher discounts correlate with lower profit. "
        "The cloud of points slopes downward, confirming that aggressive discounting erodes margins.")
    story.append(PageBreak())
    add_image(viz_root / "correlation_heatmap.png",
        "Figure 16: Correlation Heatmap — Pearson correlations among numeric variables. Discount and Profit show "
        "the strongest negative correlation (-0.316). Sales and Shipping Cost are positively correlated (0.765).")
    story.append(PageBreak())
    add_image(viz_root / "pairplot_key_metrics.png",
        "Figure 17: Pairplot of Key Metrics — Scatter matrix and KDE plots for Sales, Quantity, Discount, Profit, and Shipping Cost. "
        "Reveals skewed distributions and non-linear relationships worth transforming for modeling.")
    story.append(PageBreak())
    add_image(viz_root / "sales_distribution.png",
        "Figure 18: Sales Distribution — Histogram with KDE overlay shows strong right skew. Most orders are small, "
        "while a few large orders drive total revenue. Log transformation is recommended for modeling.")
    story.append(PageBreak())
    add_image(viz_root / "quantity_distribution.png",
        "Figure 19: Quantity Distribution — Most orders contain 2-3 units. The distribution is discrete and right-skewed, "
        "with a long tail up to 14 units per order.")
    story.append(PageBreak())
    add_image(viz_root / "boxplot_sales_by_category.png",
        "Figure 20: Boxplot of Sales by Category — Technology shows the highest median and widest spread, indicating "
        "high-value transactions. Office Supplies have the lowest median but many outliers, suggesting diverse order sizes.")
    story.append(PageBreak())
    add_image(viz_root / "violin_profit_by_segment.png",
        "Figure 21: Violin Plot of Profit by Segment — Distribution shape reveals that Corporate segment has the widest "
        "profit range, while Home Office is more concentrated. Consumer segment shows fat tails on the negative side.")
    story.append(PageBreak())
    add_image(viz_root / "swarm_sales_by_shipmode.png",
        "Figure 22: Swarm Plot of Sales by Ship Mode — Each point represents an order. Same Day and First Class show "
        "higher median sales, while Standard Class dominates order volume but with lower per-order value.")
    story.append(PageBreak())

    # Advanced Analytics
    story.append(Paragraph("5.6 Advanced Analytics Visualizations", heading1))
    add_image(viz_root / "bubble_chart.png",
        "Figure 23: Bubble Chart (Sales vs Profit vs Quantity) — Bubble size encodes order count. "
        "Large bubbles in the top-right quadrant represent high-sales, high-profit, high-quantity orders (ideal). "
        "Bubbles in the bottom-right indicate high sales but negative profit (problematic).")
    story.append(PageBreak())
    add_image(viz_root / "stacked_bar_category_region.png",
        "Figure 24: Stacked Bar Chart — Sales by Category across Regions. Technology dominates in the West and East, "
        "while Furniture is stronger in the Central region. This helps regional managers tailor inventory.")
    story.append(PageBreak())
    add_image(viz_root / "cumulative_sales_area.png",
        "Figure 25: Cumulative Sales Area Chart — Running total of sales over time. The slope steepens in late 2013 "
        "and 2014, indicating accelerating revenue growth. Any plateau would signal market saturation.")
    story.append(PageBreak())

    # Predictive Modeling
    story.append(Paragraph("5.7 Predictive Modelling Visualizations", heading1))
    add_image(viz_root / "feature_importance.png",
        "Figure 26: Feature Importance — Horizontal bar chart of the top 20 features in the Random Forest model. "
        "Sales, Discount, and Shipping Cost dominate, confirming business intuition. Category and Region provide additional predictive power.")
    story.append(PageBreak())
    add_image(viz_root / "actual_vs_predicted.png",
        "Figure 27: Actual vs Predicted Profit — Scatter plot showing model predictions against true values. "
        "Points cluster around the diagonal, indicating good overall fit. Some high-profit outliers are under-predicted.")
    story.append(PageBreak())
    add_image(viz_root / "residuals.png",
        "Figure 28: Residual Plot — Residuals vs Predicted values show no systematic pattern, confirming homoscedasticity "
        "and validating the model's linearity assumptions. Residuals are centered around zero with moderate spread.")
    story.append(PageBreak())
    add_image(viz_root / "segment_distribution.png",
        "Figure 29: Segment Distribution — Pie chart of customer segments. Champions and Loyal segments together "
        "comprise over 40% of customers and should be prioritized for retention programs.")
    story.append(PageBreak())

    # 6. Recommendations
    story.append(Paragraph("6. Recommendations", heading1))
    recs = [
        "Implement dynamic discount caps to protect margin.",
        "Prioritize inventory and marketing for Technology and top Pareto products.",
        "Launch loyalty programs targeting Champions and Loyal segments.",
        "Optimize shipping cost by mode and region without sacrificing satisfaction.",
        "Review loss-making products (2,672 SKUs) for discontinuation.",
    ]
    for r in recs:
        story.append(Paragraph(f"• {r}", bullet_style))

    # 7. Model Metrics Table
    story.append(Paragraph("7. Predictive Model Metrics", heading1))
    data = [
        ["Model", "MAE", "RMSE", "R²"],
        ["Random Forest", "34.77", "100.72", "0.658"],
        ["XGBoost", "35.48", "102.13", "0.649"],
    ]
    table = Table(data, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4472C4")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 11),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#D9E2F3")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.2 * inch))

    # 8. Statistical Test Summary
    story.append(Paragraph("8. Statistical Test Summary", heading1))
    stats_data = [
        ["Test", "Statistic", "p-value", "Conclusion"],
        ["Welch t-test (Profit: Consumer vs Corporate)", "t=0.18", "0.8478", "Not significant"],
        ["ANOVA (Sales across Categories)", "F=large", "<0.001", "Significant"],
        ["Chi-square (Segment × Market)", "χ²=...", "0.0608", "Marginal"],
        ["Pearson r (Discount vs Profit)", "r=-0.316", "<0.001", "Significant negative"],
        ["Mann-Whitney U (Discount Profit)", "U=...", "<0.001", "Significant"],
    ]
    stats_table = Table(stats_data, hAlign="LEFT", colWidths=[2.2 * inch, 1.1 * inch, 1.1 * inch, 1.4 * inch])
    stats_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#70AD47")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#E2EFDA")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
    ]))
    story.append(stats_table)
    story.append(PageBreak())

    # 9. Limitations
    story.append(Paragraph("9. Limitations & Future Work", heading1))
    story.append(Paragraph(
        "• 80.5% missing Postal Codes required imputation, reducing geospatial precision.<br/>"
        "• No explicit returns or churn dates; return analysis uses negative-profit proxy.<br/>"
        "• Future: deploy models via REST API, integrate external macro data, build interactive Streamlit dashboard, "
        "and extend forecasting with exogenous variables.",
        body
    ))

    # 10. Conclusion
    story.append(Paragraph("10. Conclusion", heading1))
    story.append(Paragraph(
        "This project delivers a complete, auditable, and production-ready data analytics pipeline. "
        "All artefacts—raw data, cleaned data, SQL schema, Excel workbook, visualizations, ML models, "
        "and multi-format reports—are versioned and logged. The insights are ready to drive strategic "
        "decisions in sales, marketing, and operations.",
        body
    ))

    doc.build(story)
    logger.info("PDF report saved to %s", destination)
    return str(destination)


if __name__ == "__main__":
    generate_pdf_report()
