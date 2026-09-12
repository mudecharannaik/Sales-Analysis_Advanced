"""Main orchestrator for the Superstore Sales Analysis pipeline.

Runs the full pipeline from data loading through to report generation.
Designed to be executed from the project root directory.
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime

import pandas as pd

# Ensure the scripts directory is on sys.path when run as a script.
_SCRIPT_DIR = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
if _SCRIPT_DIR not in sys.path:
    sys.path.insert(0, _SCRIPT_DIR)

from config import get_logger  # noqa: E402

logger = get_logger("main")


def _run_step(step_name: str, fn, *args, **kwargs):
    """Execute a pipeline step with error handling.

    Args:
        step_name: Human-readable step name.
        fn: Callable to execute.
        *args: Positional arguments for fn.
        **kwargs: Keyword arguments for fn.

    Returns:
        Result of fn() or None on failure.
    """
    logger.info("=" * 60)
    logger.info("STEP: %s", step_name)
    logger.info("=" * 60)
    try:
        result = fn(*args, **kwargs)
        logger.info("COMPLETED: %s", step_name)
        return result
    except Exception as exc:  # noqa: BLE001
        logger.error("FAILED: %s - %s", step_name, exc)
        traceback.print_exc()
        return None


def main() -> dict:
    """Run the full analysis pipeline.

    Returns:
        Dictionary containing all pipeline outputs.
    """
    logger.info("Starting Superstore Sales Analysis Pipeline")
    logger.info("Timestamp: %s", datetime.now().isoformat())

    outputs: dict = {}

    # 1. Load data
    from data_loader import load_raw_data, save_clean_data
    raw_df = _run_step("Load Data", load_raw_data)
    if raw_df is None:
        logger.critical("Cannot proceed without data")
        return outputs

    # 2. Data quality
    from data_quality import generate_quality_summary
    quality_summary = _run_step("Data Quality Check", generate_quality_summary, raw_df)
    outputs["quality"] = quality_summary

    # 3. Preprocessing
    from preprocessing import clean_pipeline
    cleaned_df = _run_step("Cleaning & Preprocessing", clean_pipeline, raw_df)
    if cleaned_df is None:
        logger.critical("Cannot proceed without cleaned data")
        return outputs

    _run_step("Save Cleaned Data", save_clean_data, cleaned_df)

    # 4. EDA
    from eda import numeric_summary, correlation_matrix, sales_by_category
    eda_summary = _run_step("EDA Summary", numeric_summary, cleaned_df)
    correlation = _run_step("Correlation Matrix", correlation_matrix, cleaned_df)
    category_sales = _run_step("Category Sales", sales_by_category, cleaned_df)
    outputs["eda"] = {
        "numeric_summary": eda_summary,
        "correlation": correlation,
        "category_sales": category_sales,
    }

    # 5. Statistical analysis
    from statistical_analysis import run_full_battery
    stat_results = _run_step("Statistical Analysis", run_full_battery, cleaned_df)
    outputs["statistical"] = stat_results

    # 6. Time series analysis
    from time_series_analysis import run_time_series_pipeline
    ts_results = _run_step("Time Series Analysis", run_time_series_pipeline, cleaned_df)
    outputs["time_series"] = ts_results

    # 7. Customer analytics
    from customer_analytics import run_customer_analytics
    customer_results = _run_step("Customer Analytics", run_customer_analytics, cleaned_df)
    outputs["customer"] = customer_results

    # 8. Product analytics
    from product_analytics import run_product_analytics
    product_results = _run_step("Product Analytics", run_product_analytics, cleaned_df)
    outputs["product"] = product_results

    # 9. Geographic analysis
    from geographic_analysis import run_geographic_analysis
    geo_results = _run_step("Geographic Analysis", run_geographic_analysis, cleaned_df)
    outputs["geographic"] = geo_results

    # 10. Predictive modelling
    from predictive_modeling import run_predictive_modeling
    model_results = _run_step("Predictive Modelling", run_predictive_modeling, cleaned_df)
    outputs["predictive"] = model_results

    # 11. Visualizations
    from visualization import (
        plot_sales_trend,
        plot_monthly_sales,
        plot_profit_vs_sales_scatter,
        plot_category_sales_pie,
        plot_subcategory_horizontal_bar,
        plot_segment_distribution,
        plot_market_performance,
        plot_region_analysis,
        plot_ship_mode_analysis,
        plot_discount_vs_profit_scatter,
        plot_quantity_distribution,
        plot_sales_distribution,
        plot_boxplot_outliers_by_category,
        plot_correlation_heatmap,
        plot_pairplot_key_metrics,
        plot_rfm_segments,
        plot_pareto_chart,
        plot_bubble_chart,
        plot_stacked_bar_category_region,
        plot_heatmap_month_category,
        plot_violin_profit_by_segment,
        plot_swarm_sales_by_shipmode,
        plot_area_cumulative_sales,
        plot_feature_importance,
        plot_actual_vs_predicted,
        plot_residuals,
    )

    logger.info("=" * 60)
    logger.info("STEP: Visualizations")
    logger.info("=" * 60)

    _run_step("Sales Trend", plot_sales_trend, cleaned_df)
    _run_step("Monthly Sales", plot_monthly_sales, cleaned_df)
    _run_step("Profit vs Sales", plot_profit_vs_sales_scatter, cleaned_df)
    _run_step("Category Sales Pie", plot_category_sales_pie, cleaned_df)
    _run_step("Subcategory Bar", plot_subcategory_horizontal_bar, cleaned_df)
    _run_step("Segment Distribution", plot_segment_distribution, cleaned_df)
    _run_step("Market Performance", plot_market_performance, cleaned_df)
    _run_step("Region Analysis", plot_region_analysis, cleaned_df)
    _run_step("Ship Mode Analysis", plot_ship_mode_analysis, cleaned_df)
    _run_step("Discount vs Profit", plot_discount_vs_profit_scatter, cleaned_df)
    _run_step("Quantity Distribution", plot_quantity_distribution, cleaned_df)
    _run_step("Sales Distribution", plot_sales_distribution, cleaned_df)
    _run_step("Boxplot by Category", plot_boxplot_outliers_by_category, cleaned_df)
    _run_step("Correlation Heatmap", plot_correlation_heatmap, cleaned_df)
    _run_step("Pairplot", plot_pairplot_key_metrics, cleaned_df)
    _run_step("Cumulative Sales", plot_area_cumulative_sales, cleaned_df)
    _run_step("Bubble Chart", plot_bubble_chart, cleaned_df)
    _run_step("Stacked Bar", plot_stacked_bar_category_region, cleaned_df)
    _run_step("Heatmap Month-Category", plot_heatmap_month_category, cleaned_df)
    _run_step("Violin by Segment", plot_violin_profit_by_segment, cleaned_df)
    _run_step("Swarm by Ship Mode", plot_swarm_sales_by_shipmode, cleaned_df)

    # RFM segments chart
    if customer_results and "rfm" in customer_results:
        _run_step("RFM Segments", plot_rfm_segments, customer_results["rfm"])

    # Pareto chart - product sales distribution
    if "Product Name" in cleaned_df.columns:
        pareto_data = cleaned_df.groupby("Product Name")["Sales"].sum().sort_values(ascending=False)
        _run_step("Pareto Chart", plot_pareto_chart, pareto_data)

    # Time series decomposition chart
    if ts_results and "decomposition" in ts_results:
        _run_step("TS Decomposition", __import__("visualization", fromlist=["plot_time_series_decomposition"]).plot_time_series_decomposition, ts_results["decomposition"])

    # Forecast chart
    if ts_results and "arima_forecast" in ts_results and "series" in ts_results:
        _run_step("Forecast Chart", __import__("visualization", fromlist=["plot_forecast_vs_actual"]).plot_forecast_vs_actual, ts_results["series"], ts_results["arima_forecast"])

    # Anomaly chart
    if ts_results and "anomalies" in ts_results and "series" in ts_results:
        _run_step("Anomaly Chart", __import__("visualization", fromlist=["plot_anomalies"]).plot_anomalies, ts_results["series"], ts_results["anomalies"])

    # Feature importance chart
    if model_results and "rf_importance" in model_results:
        _run_step("Feature Importance", plot_feature_importance, model_results["rf_importance"])

    # Actual vs Predicted chart
    if model_results and "actual_vs_predicted" in model_results:
        avp = model_results["actual_vs_predicted"]
        _run_step("Actual vs Predicted", plot_actual_vs_predicted, avp["Actual"].values, avp["Predicted"].values)

    # Residuals chart
    if model_results and "residuals" in model_results:
        res = model_results["residuals"]
        _run_step("Residuals", plot_residuals, res["Actual"].values, res["Predicted"].values)

    logger.info("COMPLETED: Visualizations")

    # 12. SQL Export
    from sql_export import export_to_sql
    sql_counts = _run_step("SQL Export", export_to_sql, cleaned_df)
    outputs["sql_counts"] = sql_counts

    # 13. Excel Export
    from excel_export import create_excel_report
    excel_path = _run_step(
        "Excel Export",
        create_excel_report,
        quality_summary["profile"] if quality_summary else pd.DataFrame(),
        eda_summary if eda_summary is not None else pd.DataFrame(),
        stat_results if stat_results is not None else pd.DataFrame(),
        cleaned_df,
    )
    outputs["excel_path"] = excel_path

    # 14. Report Generation
    from report_generator import generate_report
    report_path = _run_step(
        "Report Generation",
        generate_report,
        cleaned_df,
        quality_summary,
        stat_results,
        customer_results,
        product_results,
        geo_results,
        model_results,
        ts_results,
    )
    outputs["report_path"] = report_path

    # 15. HTML Generation
    from html_report import generate_html
    html_paths = _run_step(
        "HTML Generation",
        generate_html,
        cleaned_df,
        quality_summary,
        stat_results,
        customer_results,
        product_results,
        geo_results,
        model_results,
        ts_results,
    )
    outputs["html_paths"] = html_paths

    # Final summary
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 60)
    logger.info("Records processed: %d", len(cleaned_df))
    logger.info("Output keys: %s", list(outputs.keys()))

    return outputs


if __name__ == "__main__":
    results = main()
    print("\n=== Pipeline Summary ===")
    for key, value in results.items():
        if isinstance(value, str):
            print(f"  {key}: {value}")
        elif isinstance(value, dict):
            print(f"  {key}: {list(value.keys())}")
        else:
            print(f"  {key}: {type(value).__name__}")
