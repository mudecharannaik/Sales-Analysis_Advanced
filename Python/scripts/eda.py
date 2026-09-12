"""Exploratory data analysis aggregation helpers.

These functions compute the summary tables used by the visualisation gallery
and EDA notebook. They are pure transformers that never mutate the input.
"""

from __future__ import annotations

import pandas as pd

from config import get_logger

logger = get_logger(__name__)


def sales_by_time(df: pd.DataFrame, freq: str = "M") -> pd.DataFrame:
    """Aggregate Sales/Profit/Quantity by a resampling frequency."""
    if "Order Date" not in df.columns:
        raise KeyError("Order Date column required")
    tmp = df.set_index("Order Date")
    agg = tmp.resample(freq).agg(
        {"Sales": "sum", "Profit": "sum", "Quantity": "sum", "Order ID": "nunique"}
    )
    agg = agg.rename(columns={"Order ID": "Orders"})
    logger.info("sales_by_time aggregated at frequency '%s'", freq)
    return agg.reset_index()


def sales_by_category(df: pd.DataFrame) -> pd.DataFrame:
    """Sales/Profit by Category sorted descending by Sales."""
    return (
        df.groupby("Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .sort_values("Sales", ascending=False)
        .reset_index()
    )


def sales_by_subcategory(df: pd.DataFrame, top: int = 20) -> pd.DataFrame:
    """Top-N sub-categories by Sales."""
    out = (
        df.groupby("Sub-Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .sort_values("Sales", ascending=False)
        .reset_index()
        .head(top)
    )
    return out


def segment_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Counts and sales share by customer Segment."""
    out = (
        df.groupby("Segment")
        .agg(Sales=("Sales", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
    )
    out["Sales Share %"] = (100 * out["Sales"] / out["Sales"].sum()).round(2)
    return out


def market_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Sales/Profit/Margin by Market."""
    out = (
        df.groupby("Market")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
    )
    out["Margin %"] = (100 * out["Profit"] / out["Sales"]).round(2)
    return out.sort_values("Sales", ascending=False).reset_index(drop=True)


def region_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Sales/Profit by Region."""
    out = (
        df.groupby("Region")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"), Orders=("Order ID", "nunique"))
        .reset_index()
    )
    return out


def ship_mode_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Sales/Profit by Ship Mode."""
    return (
        df.groupby("Ship Mode")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
        .sort_values("Sales", ascending=False)
    )


def numeric_summary(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Describe numeric columns with skew and kurtosis."""
    cols = columns or ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost"]
    cols = [c for c in cols if c in df.columns]
    desc = df[cols].describe().T
    desc["skew"] = df[cols].skew()
    desc["kurtosis"] = df[cols].kurtosis()
    return desc


def correlation_matrix(df: pd.DataFrame, columns: list[str] | None = None) -> pd.DataFrame:
    """Pearson correlation matrix for numeric columns."""
    cols = columns or ["Sales", "Quantity", "Discount", "Profit", "Shipping Cost"]
    cols = [c for c in cols if c in df.columns]
    return df[cols].corr()


def sales_by_month_category(df: pd.DataFrame) -> pd.DataFrame:
    """Pivot of Sales by Order Month and Category (for heatmaps)."""
    if "Order MonthName" not in df.columns:
        raise KeyError("Run engineer_features first (Order MonthName missing)")
    pivot = df.pivot_table(
        index="Order MonthName", columns="Category", values="Sales", aggfunc="sum"
    )
    order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    pivot = pivot.reindex([m for m in order if m in pivot.index])
    return pivot


def cumulative_sales(df: pd.DataFrame) -> pd.DataFrame:
    """Cumulative Sales over time (daily)."""
    tmp = df.set_index("Order Date").sort_index()
    cum = tmp["Sales"].cumsum().reset_index()
    cum.columns = ["Order Date", "Cumulative Sales"]
    return cum
