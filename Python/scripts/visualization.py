"""Visualization gallery for the Superstore Sales Analysis project.

Each function creates a chart and saves it as a PNG to the Visualizations/
directory. All functions close the figure after saving to free memory.
"""

from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from config import PROJECT_ROOT, get_logger

logger = get_logger(__name__)

VIS_DIR = PROJECT_ROOT / "Visualizations"
VIS_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", palette="muted")


def _save_fig(fig: plt.Figure, filename: str) -> str:
    """Save the figure to the Visualizations directory.

    Args:
        fig: Matplotlib figure to save.
        filename: Output filename (without directory).

    Returns:
        Absolute path of the saved file.
    """
    path = VIS_DIR / filename
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    logger.info("Saved chart: %s", path)
    return str(path)


def plot_sales_trend(df: pd.DataFrame) -> str:
    """Plot daily sales trend as a line chart.

    Args:
        df: DataFrame with Order Date and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating sales trend chart")
    daily = df.set_index("Order Date")["Sales"].resample("D").sum().fillna(0)
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(daily.index, daily.values, linewidth=0.8, alpha=0.8)
    ax.set_title("Daily Sales Trend")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales")
    fig.tight_layout()
    return _save_fig(fig, "sales_trend.png")


def plot_monthly_sales(df: pd.DataFrame) -> str:
    """Plot monthly total sales as a bar chart.

    Args:
        df: DataFrame with Order Date and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating monthly sales chart")
    monthly = df.set_index("Order Date")["Sales"].resample("ME").sum()
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.bar(monthly.index.astype(str), monthly.values, width=20)
    ax.set_title("Monthly Sales")
    ax.set_xlabel("Month")
    ax.set_ylabel("Sales")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "monthly_sales.png")


def plot_quarterly_sales(df: pd.DataFrame) -> str:
    """Plot quarterly total sales as a bar chart.

    Args:
        df: DataFrame with Order Date and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating quarterly sales chart")
    quarterly = df.set_index("Order Date")["Sales"].resample("QE").sum()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(quarterly.index.astype(str), quarterly.values, width=40)
    ax.set_title("Quarterly Sales")
    ax.set_xlabel("Quarter")
    ax.set_ylabel("Sales")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "quarterly_sales.png")


def plot_profit_vs_sales_scatter(df: pd.DataFrame) -> str:
    """Plot profit vs sales scatter chart.

    Args:
        df: DataFrame with Sales and Profit columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating profit vs sales scatter")
    sample = df.sample(min(len(df), 5000), random_state=42) if len(df) > 5000 else df
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(sample["Sales"], sample["Profit"], alpha=0.4, s=10)
    ax.set_title("Profit vs Sales")
    ax.set_xlabel("Sales")
    ax.set_ylabel("Profit")
    ax.axhline(0, color="red", linewidth=0.5, linestyle="--")
    fig.tight_layout()
    return _save_fig(fig, "profit_vs_sales_scatter.png")


def plot_category_sales_pie(df: pd.DataFrame) -> str:
    """Plot a donut chart of sales by category.

    Args:
        df: DataFrame with Category and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating category sales pie")
    cat = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        cat.values, labels=cat.index, autopct="%1.1f%%", startangle=90,
        wedgeprops=dict(width=0.4),
    )
    ax.set_title("Sales by Category")
    fig.tight_layout()
    return _save_fig(fig, "category_sales_donut.png")


def plot_subcategory_horizontal_bar(df: pd.DataFrame) -> str:
    """Plot horizontal bar chart of sales by sub-category.

    Args:
        df: DataFrame with Sub-Category and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating subcategory horizontal bar")
    sub = (
        df.groupby("Sub-Category")["Sales"]
        .sum()
        .sort_values(ascending=True)
    )
    fig, ax = plt.subplots(figsize=(10, 8))
    sub.plot.barh(ax=ax)
    ax.set_title("Sales by Sub-Category")
    ax.set_xlabel("Sales")
    fig.tight_layout()
    return _save_fig(fig, "subcategory_sales_bar.png")


def plot_segment_distribution(df: pd.DataFrame) -> str:
    """Plot pie chart of sales by segment.

    Args:
        df: DataFrame with Segment and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating segment distribution")
    seg = df.groupby("Segment")["Sales"].sum()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(seg.values, labels=seg.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Sales by Segment")
    fig.tight_layout()
    return _save_fig(fig, "segment_distribution.png")


def plot_market_performance(df: pd.DataFrame) -> str:
    """Plot bar chart of sales by market.

    Args:
        df: DataFrame with Market and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating market performance chart")
    market = df.groupby("Market")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=market.index, y=market.values, ax=ax)
    ax.set_title("Sales by Market")
    ax.set_xlabel("Market")
    ax.set_ylabel("Sales")
    fig.tight_layout()
    return _save_fig(fig, "market_performance.png")


def plot_region_analysis(df: pd.DataFrame) -> str:
    """Plot bar chart of sales by region.

    Args:
        df: DataFrame with Region and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating region analysis chart")
    region = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.barplot(x=region.index, y=region.values, ax=ax)
    ax.set_title("Sales by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "region_analysis.png")


def plot_ship_mode_analysis(df: pd.DataFrame) -> str:
    """Plot bar chart of sales by ship mode.

    Args:
        df: DataFrame with Ship Mode and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating ship mode analysis chart")
    ship = df.groupby("Ship Mode")["Sales"].sum().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=ship.index, y=ship.values, ax=ax)
    ax.set_title("Sales by Ship Mode")
    ax.set_xlabel("Ship Mode")
    ax.set_ylabel("Sales")
    fig.tight_layout()
    return _save_fig(fig, "ship_mode_analysis.png")


def plot_discount_vs_profit_scatter(df: pd.DataFrame) -> str:
    """Plot scatter chart of discount vs profit.

    Args:
        df: DataFrame with Discount and Profit columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating discount vs profit scatter")
    sample = df.sample(min(len(df), 5000), random_state=42) if len(df) > 5000 else df
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(sample["Discount"], sample["Profit"], alpha=0.4, s=10)
    ax.set_title("Discount vs Profit")
    ax.set_xlabel("Discount")
    ax.set_ylabel("Profit")
    ax.axhline(0, color="red", linewidth=0.5, linestyle="--")
    fig.tight_layout()
    return _save_fig(fig, "discount_vs_profit_scatter.png")


def plot_quantity_distribution(df: pd.DataFrame) -> str:
    """Plot histogram of quantity distribution.

    Args:
        df: DataFrame with Quantity column.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating quantity distribution")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.histplot(df["Quantity"], bins=range(1, int(df["Quantity"].max()) + 2), ax=ax)
    ax.set_title("Quantity Distribution")
    ax.set_xlabel("Quantity")
    fig.tight_layout()
    return _save_fig(fig, "quantity_distribution.png")


def plot_sales_distribution(df: pd.DataFrame) -> str:
    """Plot histogram/KDE of sales distribution.

    Args:
        df: DataFrame with Sales column.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating sales distribution")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(df["Sales"], kde=True, ax=ax, bins=100)
    ax.set_title("Sales Distribution")
    ax.set_xlabel("Sales")
    fig.tight_layout()
    return _save_fig(fig, "sales_distribution.png")


def plot_boxplot_outliers_by_category(df: pd.DataFrame) -> str:
    """Plot boxplot of sales by category to show outliers.

    Args:
        df: DataFrame with Category and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating boxplot outliers by category")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.boxplot(data=df, x="Category", y="Sales", ax=ax)
    ax.set_title("Sales Distribution by Category")
    fig.tight_layout()
    return _save_fig(fig, "boxplot_sales_by_category.png")


def plot_correlation_heatmap(df: pd.DataFrame) -> str:
    """Plot correlation heatmap of numeric columns.

    Args:
        df: DataFrame with numeric columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating correlation heatmap")
    numeric_cols = ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost"]
    numeric_cols = [c for c in numeric_cols if c in df.columns]
    corr = df[numeric_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm", center=0, ax=ax)
    ax.set_title("Correlation Heatmap")
    fig.tight_layout()
    return _save_fig(fig, "correlation_heatmap.png")


def plot_pairplot_key_metrics(df: pd.DataFrame) -> str:
    """Plot pairplot of key metrics.

    Args:
        df: DataFrame with Sales, Profit, Quantity, Discount columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating pairplot")
    cols = ["Sales", "Profit", "Quantity", "Discount"]
    cols = [c for c in cols if c in df.columns]
    sample = df[cols].sample(min(len(df), 2000), random_state=42) if len(df) > 2000 else df[cols]

    g = sns.pairplot(sample, diag_kind="kde", plot_kws={"alpha": 0.4, "s": 10})
    g.fig.suptitle("Pairplot of Key Metrics", y=1.02)
    path = VIS_DIR / "pairplot_key_metrics.png"
    g.savefig(path, dpi=150, bbox_inches="tight")
    plt.close("all")
    logger.info("Saved chart: %s", path)
    return str(path)


def plot_time_series_decomposition(decomp_result) -> str:
    """Plot the 4-panel seasonal decomposition chart.

    Args:
        decomp_result: Result from statsmodels seasonal_decompose.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating time series decomposition chart")
    fig, axes = plt.subplots(4, 1, figsize=(14, 10), sharex=True)
    decomp_result.observed.plot(ax=axes[0], title="Observed")
    decomp_result.trend.plot(ax=axes[1], title="Trend")
    decomp_result.seasonal.plot(ax=axes[2], title="Seasonal")
    decomp_result.resid.plot(ax=axes[3], title="Residual")
    fig.suptitle("Time Series Decomposition", y=1.02)
    fig.tight_layout()
    return _save_fig(fig, "time_series_decomposition.png")


def plot_forecast_vs_actual(series: pd.Series, forecast_df: pd.DataFrame) -> str:
    """Plot forecast vs actual values.

    Args:
        series: Historical time series.
        forecast_df: DataFrame with forecast, lower, upper columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating forecast vs actual chart")
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(series.index, series.values, label="Actual", linewidth=1.5)
    if "forecast" in forecast_df.columns:
        fc_index = forecast_df.index if isinstance(forecast_df.index, pd.DatetimeIndex) else pd.RangeIndex(len(forecast_df))
        ax.plot(fc_index, forecast_df["forecast"].values, label="Forecast", linewidth=1.5)
        if "lower" in forecast_df.columns and "upper" in forecast_df.columns:
            ax.fill_between(
                fc_index,
                forecast_df["lower"].values,
                forecast_df["upper"].values,
                alpha=0.2,
                label="Confidence Interval",
            )
    ax.set_title("Forecast vs Actual")
    ax.set_xlabel("Date")
    ax.set_ylabel("Sales")
    ax.legend()
    fig.tight_layout()
    return _save_fig(fig, "forecast_vs_actual.png")


def plot_rfm_segments(rfm_df: pd.DataFrame) -> str:
    """Plot RFM segment distribution.

    Args:
        rfm_df: DataFrame with Segment column.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating RFM segments chart")
    if "Segment" not in rfm_df.columns:
        logger.warning("Segment column not found; skipping")
        return ""

    seg_counts = rfm_df["Segment"].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=seg_counts.index, y=seg_counts.values, ax=ax)
    ax.set_title("Customer Segment Distribution")
    ax.set_xlabel("Segment")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "rfm_segments.png")


def plot_pareto_chart(df: pd.DataFrame) -> str:
    """Plot Pareto (80/20) chart.

    Args:
        df: DataFrame with Sales column.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating Pareto chart")
    totals = df.sort_values(ascending=False).values
    cumulative_pct = 100 * totals.cumsum() / totals.sum()

    fig, ax1 = plt.subplots(figsize=(14, 6))
    ax1.bar(range(len(totals)), totals, color="steelblue")
    ax1.set_xlabel("Products (ranked)")
    ax1.set_ylabel("Sales")

    ax2 = ax1.twinx()
    ax2.plot(range(len(totals)), cumulative_pct, color="red", linewidth=1.5)
    ax2.axhline(80, color="gray", linestyle="--", linewidth=0.8)
    ax2.set_ylabel("Cumulative %")

    ax1.set_title("Pareto Chart (80/20 Rule)")
    fig.tight_layout()
    return _save_fig(fig, "pareto_chart.png")


def plot_bubble_chart(df: pd.DataFrame) -> str:
    """Plot bubble chart of Sales, Profit and Quantity.

    Args:
        df: DataFrame with Category, Sales, Profit, Quantity columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating bubble chart")
    agg = (
        df.groupby("Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Quantity=("Quantity", "sum"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(10, 7))
    scatter = ax.scatter(
        agg["Sales"], agg["Profit"],
        s=agg["Quantity"] * 2, alpha=0.6, c=range(len(agg)), cmap="viridis",
    )
    for _, row in agg.iterrows():
        ax.annotate(row["Category"], (row["Sales"], row["Profit"]), fontsize=9)
    ax.set_title("Bubble Chart: Sales vs Profit (size=Quantity)")
    ax.set_xlabel("Sales")
    ax.set_ylabel("Profit")
    fig.tight_layout()
    return _save_fig(fig, "bubble_chart.png")


def plot_stacked_bar_category_region(df: pd.DataFrame) -> str:
    """Plot stacked bar chart of category sales by region.

    Args:
        df: DataFrame with Category, Region, Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating stacked bar chart")
    pivot = df.pivot_table(index="Region", columns="Category", values="Sales", aggfunc="sum")
    fig, ax = plt.subplots(figsize=(12, 7))
    pivot.plot.bar(stacked=True, ax=ax)
    ax.set_title("Sales by Region and Category")
    ax.set_xlabel("Region")
    ax.set_ylabel("Sales")
    ax.legend(title="Category")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "stacked_bar_category_region.png")


def plot_heatmap_month_category(df: pd.DataFrame) -> str:
    """Plot heatmap of sales by month and category.

    Args:
        df: DataFrame with Order MonthName, Category, Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating month-category heatmap")
    if "Order MonthName" not in df.columns:
        logger.warning("Order MonthName missing; skipping")
        return ""

    pivot = df.pivot_table(
        index="Order MonthName", columns="Category", values="Sales", aggfunc="sum"
    )
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot = pivot.reindex([m for m in order if m in pivot.index])

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
    ax.set_title("Sales Heatmap: Month vs Category")
    fig.tight_layout()
    return _save_fig(fig, "heatmap_month_category.png")


def plot_violin_profit_by_segment(df: pd.DataFrame) -> str:
    """Plot violin chart of profit distribution by segment.

    Args:
        df: DataFrame with Segment and Profit columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating violin plot")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.violinplot(data=df, x="Segment", y="Profit", ax=ax, cut=0)
    ax.set_title("Profit Distribution by Segment")
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    return _save_fig(fig, "violin_profit_by_segment.png")


def plot_swarm_sales_by_shipmode(df: pd.DataFrame) -> str:
    """Plot swarm chart of sales by ship mode.

    Args:
        df: DataFrame with Ship Mode and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating swarm plot")
    sample = df.sample(min(len(df), 1000), random_state=42) if len(df) > 1000 else df
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.stripplot(data=sample, x="Ship Mode", y="Sales", ax=ax, alpha=0.5, jitter=True)
    ax.set_title("Sales by Ship Mode (sample)")
    fig.tight_layout()
    return _save_fig(fig, "swarm_sales_by_shipmode.png")


def plot_area_cumulative_sales(df: pd.DataFrame) -> str:
    """Plot area chart of cumulative sales over time.

    Args:
        df: DataFrame with Order Date and Sales columns.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating cumulative sales area chart")
    daily = df.set_index("Order Date")["Sales"].resample("D").sum().fillna(0).cumsum()
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.fill_between(daily.index, daily.values, alpha=0.5)
    ax.plot(daily.index, daily.values, linewidth=1)
    ax.set_title("Cumulative Sales Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative Sales")
    fig.tight_layout()
    return _save_fig(fig, "cumulative_sales_area.png")


def plot_anomalies(series: pd.Series, anomalies: pd.Series) -> str:
    """Plot anomaly detection results.

    Args:
        series: Full time series.
        anomalies: Boolean series indicating anomaly positions.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating anomaly scatter chart")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(series.index, series.values, linewidth=1, label="Series")
    if anomalies.any():
        ax.scatter(series.index[anomalies], series.values[anomalies], color="red", s=40, zorder=5, label="Anomaly")
    ax.set_title("Anomaly Detection")
    ax.set_xlabel("Date")
    ax.set_ylabel("Value")
    ax.legend()
    fig.tight_layout()
    return _save_fig(fig, "anomalies.png")


def plot_feature_importance(importances: pd.DataFrame, feature_names: list[str] | None = None) -> str:
    """Plot feature importance bar chart.

    Args:
        importances: DataFrame with Feature and Importance columns (or array-like).
        feature_names: Optional list of feature names if importances is array-like.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating feature importance chart")
    if isinstance(importances, pd.DataFrame):
        data = importances.head(20)
    else:
        data = pd.DataFrame({"Feature": feature_names, "Importance": importances}).head(20)

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.barplot(data=data, x="Importance", y="Feature", ax=ax)
    ax.set_title("Feature Importance (Top 20)")
    fig.tight_layout()
    return _save_fig(fig, "feature_importance.png")


def plot_actual_vs_predicted(actual: np.ndarray, predicted: np.ndarray) -> str:
    """Plot actual vs predicted scatter chart.

    Args:
        actual: True target values.
        predicted: Predicted values.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating actual vs predicted chart")
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(actual, predicted, alpha=0.4, s=10)
    lo, hi = min(actual.min(), predicted.min()), max(actual.max(), predicted.max())
    ax.plot([lo, hi], [lo, hi], "r--", linewidth=1, label="Perfect fit")
    ax.set_title("Actual vs Predicted")
    ax.set_xlabel("Actual")
    ax.set_ylabel("Predicted")
    ax.legend()
    fig.tight_layout()
    return _save_fig(fig, "actual_vs_predicted.png")


def plot_residuals(actual: np.ndarray, predicted: np.ndarray) -> str:
    """Plot residual analysis chart.

    Args:
        actual: True target values.
        predicted: Predicted values.

    Returns:
        Path to saved PNG.
    """
    logger.info("Creating residuals chart")
    residuals = actual - predicted
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].scatter(predicted, residuals, alpha=0.4, s=10)
    axes[0].axhline(0, color="red", linewidth=0.8, linestyle="--")
    axes[0].set_title("Residuals vs Predicted")
    axes[0].set_xlabel("Predicted")
    axes[0].set_ylabel("Residual")

    sns.histplot(residuals, kde=True, ax=axes[1])
    axes[1].set_title("Residual Distribution")
    axes[1].set_xlabel("Residual")
    fig.tight_layout()
    return _save_fig(fig, "residuals.png")


def plot_roc_auc(y_true: np.ndarray | None = None, y_proba: np.ndarray | None = None) -> str | None:
    """Plot ROC curve for binary classification.

    This function is a no-op for the regression pipeline; it returns None
    unless both arguments are provided.

    Args:
        y_true: True binary labels.
        y_proba: Predicted probabilities.

    Returns:
        Path to saved PNG, or None if not applicable.
    """
    if y_true is None or y_proba is None:
        logger.info("ROC/AUC skipped (regression pipeline, no binary labels)")
        return None

    from sklearn.metrics import roc_auc_score, roc_curve

    logger.info("Creating ROC/AUC chart")
    fpr, tpr, _ = roc_curve(y_true, y_proba)
    auc = roc_auc_score(y_true, y_proba)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.plot(fpr, tpr, label=f"AUC = {auc:.3f}")
    ax.plot([0, 1], [0, 1], "k--", linewidth=0.8)
    ax.set_title("ROC Curve")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend()
    fig.tight_layout()
    return _save_fig(fig, "roc_auc.png")


def plot_confusion_matrix(y_true: np.ndarray | None = None, y_pred: np.ndarray | None = None) -> str | None:
    """Plot confusion matrix for classification.

    This function is a no-op for the regression pipeline; it returns None
    unless both arguments are provided.

    Args:
        y_true: True labels.
        y_pred: Predicted labels.

    Returns:
        Path to saved PNG, or None if not applicable.
    """
    if y_true is None or y_pred is None:
        logger.info("Confusion matrix skipped (regression pipeline)")
        return None

    from sklearn.metrics import confusion_matrix as sk_confusion_matrix

    logger.info("Creating confusion matrix")
    cm = sk_confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 7))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title("Confusion Matrix")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    fig.tight_layout()
    return _save_fig(fig, "confusion_matrix.png")
