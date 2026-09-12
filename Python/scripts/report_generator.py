"""Report generator.

Produces a comprehensive markdown report summarising every stage of the
analysis pipeline.
"""

from __future__ import annotations

import os
from datetime import datetime

import pandas as pd

from config import OUTPUT_DIR, get_logger

logger = get_logger(__name__)


def _fmt_number(value, decimals: int = 2) -> str:
    """Format a number with thousands separators and given decimals."""
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def generate_report(
    df: pd.DataFrame,
    quality_summary: dict | None = None,
    stat_results: pd.DataFrame | None = None,
    customer_results: dict | None = None,
    product_results: dict | None = None,
    geo_results: dict | None = None,
    model_results: dict | None = None,
    ts_results: dict | None = None,
    output_name: str = "final_report.md",
) -> str:
    """Generate a comprehensive markdown report.

    Args:
        df: Cleaned DataFrame.
        quality_summary: Data quality summary dictionary.
        stat_results: Statistical test results DataFrame.
        customer_results: Customer analytics results dictionary.
        product_results: Product analytics results dictionary.
        geo_results: Geographic analysis results dictionary.
        model_results: Predictive modelling results dictionary.
        ts_results: Time series results dictionary.
        output_name: Output filename.

    Returns:
        Absolute path of the saved report.
    """
    logger.info("Generating final report")

    lines: list[str] = []
    lines.append("# Superstore Sales Analysis - Final Report")
    lines.append(f"\n*Generated: {datetime.now():%Y-%m-%d %H:%M:%S}*\n")

    # Executive Summary
    lines.append("## Executive Summary\n")
    lines.append(f"- **Total Records:** {_fmt_number(len(df), 0)}")
    lines.append(f"- **Date Range:** {df['Order Date'].min():%Y-%m-%d} to {df['Order Date'].max():%Y-%m-%d}")
    lines.append(f"- **Total Sales:** ${_fmt_number(df['Sales'].sum())}")
    lines.append(f"- **Total Profit:** ${_fmt_number(df['Profit'].sum())}")
    lines.append(f"- **Overall Margin:** {_fmt_number(100 * df['Profit'].sum() / df['Sales'].sum())}%")
    lines.append(f"- **Unique Customers:** {_fmt_number(df['Customer ID'].nunique(), 0)}")
    lines.append(f"- **Unique Products:** {_fmt_number(df['Product ID'].nunique(), 0)}")
    lines.append(f"- **Unique Orders:** {_fmt_number(df['Order ID'].nunique(), 0)}")
    lines.append("")

    # Data Quality
    if quality_summary:
        lines.append("## Data Quality\n")
        if "duplicates" in quality_summary:
            dups = quality_summary["duplicates"]
            lines.append(f"- **Exact Duplicates:** {_fmt_number(dups.get('exact_duplicates', 0), 0)}")
            lines.append(f"- **Key Duplicates:** {_fmt_number(dups.get('key_duplicates', 0), 0)}")
        if "integrity" in quality_summary:
            lines.append("\n### Integrity Checks\n")
            lines.append("| Check | Passed | Detail |")
            lines.append("|-------|--------|--------|")
            for _, row in quality_summary["integrity"].iterrows():
                lines.append(f"| {row['check']} | {row['passed']} | {row['detail']} |")
        lines.append("")

    # Statistical Analysis
    if stat_results is not None and not stat_results.empty:
        lines.append("## Statistical Analysis\n")
        lines.append("| Test | Statistic | P-Value | Conclusion |")
        lines.append("|------|-----------|---------|------------|")
        for _, row in stat_results.iterrows():
            lines.append(
                f"| {row.get('test', '')} | {_fmt_number(row.get('statistic', 0))} "
                f"| {_fmt_number(row.get('p_value', 0))} | {row.get('conclusion', '')} |"
            )
        lines.append("")

    # Customer Analytics
    if customer_results:
        lines.append("## Customer Analytics\n")
        if "repeat" in customer_results:
            rep = customer_results["repeat"]
            lines.append("### Repeat Customer Analysis\n")
            lines.append(f"- **Total Customers:** {_fmt_number(rep.get('total_customers', 0), 0)}")
            lines.append(f"- **Repeat Customers:** {_fmt_number(rep.get('repeat_customers', 0), 0)}")
            lines.append(f"- **One-Time Customers:** {_fmt_number(rep.get('one_time_customers', 0), 0)}")
            lines.append(f"- **Repeat Rate:** {_fmt_number(rep.get('repeat_rate_pct', 0))}%")
            lines.append(f"- **Repeat Revenue Share:** {_fmt_number(rep.get('repeat_revenue_share_pct', 0))}%")
            lines.append("")

        if "rfm" in customer_results:
            rfm = customer_results["rfm"]
            lines.append("### RFM Segmentation\n")
            if "Segment" in rfm.columns:
                seg_counts = rfm["Segment"].value_counts()
                lines.append("| Segment | Count |")
                lines.append("|---------|-------|")
                for seg, cnt in seg_counts.items():
                    lines.append(f"| {seg} | {_fmt_number(cnt, 0)} |")
            lines.append("")

        if "top_sales" in customer_results:
            lines.append("### Top 10 Customers by Sales\n")
            lines.append(customer_results["top_sales"].head(10).to_markdown(index=False))
            lines.append("")

    # Product Analytics
    if product_results:
        lines.append("## Product Analytics\n")
        if "category" in product_results:
            lines.append("### Category Performance\n")
            lines.append(product_results["category"].to_markdown(index=False))
            lines.append("")

        if "subcategory" in product_results:
            lines.append("### Sub-Category Deep Dive\n")
            lines.append(product_results["subcategory"].to_markdown(index=False))
            lines.append("")

        if "pareto" in product_results:
            pareto = product_results["pareto"]
            lines.append("### Pareto Analysis\n")
            lines.append(
                f"- Top 20% of products account for **{_fmt_number(pareto.get('top_items_pct', 0))}%** of total sales."
            )
            lines.append("")

        if "profitability_matrix" in product_results:
            lines.append("### Profitability Matrix\n")
            lines.append(product_results["profitability_matrix"].to_markdown(index=False))
            lines.append("")

    # Geographic Analysis
    if geo_results:
        lines.append("## Geographic Analysis\n")
        if "distribution_summary" in geo_results:
            dist = geo_results["distribution_summary"]
            lines.append("### Distribution Summary\n")
            for key, value in dist.items():
                lines.append(f"- **{key}:** {value}")
            lines.append("")

        if "market" in geo_results:
            lines.append("### Market Performance\n")
            lines.append(geo_results["market"].to_markdown(index=False))
            lines.append("")

        if "region" in geo_results:
            lines.append("### Regional Comparison\n")
            lines.append(geo_results["region"].to_markdown(index=False))
            lines.append("")

    # Time Series
    if ts_results:
        lines.append("## Time Series Analysis\n")
        if "anomalies" in ts_results:
            n_anomalies = int(ts_results["anomalies"].sum()) if hasattr(ts_results["anomalies"], "sum") else 0
            lines.append(f"- **Anomalies Detected:** {_fmt_number(n_anomalies, 0)}")
        if "arima_forecast" in ts_results:
            fc = ts_results["arima_forecast"]
            lines.append(f"- **ARIMA Forecast Steps:** {_fmt_number(len(fc), 0)}")
        lines.append("")

    # Predictive Modelling
    if model_results:
        lines.append("## Predictive Modelling\n")
        if "rf_metrics" in model_results:
            lines.append("### Random Forest Performance\n")
            for metric, value in model_results["rf_metrics"].items():
                lines.append(f"- **{metric}:** {_fmt_number(value)}")
            lines.append("")

        if "xgb_metrics" in model_results:
            lines.append("### XGBoost Performance\n")
            for metric, value in model_results["xgb_metrics"].items():
                lines.append(f"- **{metric}:** {_fmt_number(value)}")
            lines.append("")

        if "rf_importance" in model_results:
            lines.append("### Top 10 Feature Importances\n")
            lines.append(model_results["rf_importance"].head(10).to_markdown(index=False))
            lines.append("")

    # Conclusion
    lines.append("## Conclusion\n")
    lines.append("This report summarises the complete analysis of the Superstore dataset. "
                 "All outputs (charts, SQL database, Excel workbook) are available in "
                 "the project output directories.\n")

    report_text = "\n".join(lines)
    output_path = OUTPUT_DIR / output_name
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    logger.info("Report saved to %s", output_path)
    return str(output_path)
