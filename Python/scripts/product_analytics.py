"""Product analytics: category performance, Pareto analysis and discount impact.

This module analyses the product dimension of the Superstore dataset, from
high-level category KPIs down to product-level Pareto and co-occurrence
studies.
"""

from __future__ import annotations

import itertools

import numpy as np
import pandas as pd

from config import get_logger

logger = get_logger(__name__)


def category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Compute category-level KPIs.

    Args:
        df: Cleaned DataFrame with Category, Sales, Profit, Discount,
            Shipping Cost.

    Returns:
        DataFrame with Sales, Profit, Margin, Avg Discount, Avg Shipping
        Cost, Order Count and Product Count per category.
    """
    logger.info("Computing category performance")

    agg: dict = {
        "Sales": "sum",
        "Profit": "sum",
        "Discount": "mean",
        "Shipping Cost": "mean",
        "Order ID": "nunique",
        "Product ID": "nunique",
    }
    perf = df.groupby("Category").agg(agg).reset_index()
    perf = perf.rename(
        columns={"Order ID": "Orders", "Product ID": "Unique Products"}
    )
    perf["Margin %"] = (100 * perf["Profit"] / perf["Sales"]).round(2)
    perf["Avg Discount"] = (100 * perf["Discount"]).round(2)
    perf = perf.sort_values("Sales", ascending=False).reset_index(drop=True)

    logger.info("Category performance computed for %d categories", len(perf))
    return perf


def subcategory_deep_dive(df: pd.DataFrame) -> pd.DataFrame:
    """Detailed sub-category analysis.

    Args:
        df: Cleaned DataFrame with Sub-Category, Sales, Profit, Quantity,
            Discount.

    Returns:
        DataFrame of KPIs per sub-category.
    """
    logger.info("Computing sub-category deep dive")

    agg: dict = {
        "Sales": "sum",
        "Profit": "sum",
        "Quantity": "sum",
        "Discount": "mean",
        "Order ID": "nunique",
        "Product ID": "nunique",
    }
    sub = df.groupby("Sub-Category").agg(agg).reset_index()
    sub = sub.rename(columns={"Order ID": "Orders", "Product ID": "Products"})
    sub["Margin %"] = (100 * sub["Profit"] / sub["Sales"]).round(2)
    sub["Avg Order Value"] = (sub["Sales"] / sub["Orders"]).round(2)
    sub["Profit per Unit"] = np.where(
        sub["Quantity"] > 0, sub["Profit"] / sub["Quantity"], 0.0
    ).round(2)
    sub["Avg Discount %"] = (100 * sub["Discount"]).round(2)
    sub = sub.sort_values("Sales", ascending=False).reset_index(drop=True)

    logger.info("Sub-category analysis complete for %d sub-categories", len(sub))
    return sub


def pareto_analysis(
    df: pd.DataFrame,
    value_col: str = "Sales",
    group_col: str = "Product Name",
    top_pct: float = 0.2,
) -> dict:
    """Pareto (80/20) analysis on a product dimension.

    Args:
        df: Cleaned DataFrame.
        value_col: Numeric column to aggregate.
        group_col: Product-level column to group by.
        top_pct: Fraction defining "top" items (default 20%).

    Returns:
        Dictionary with ``pareto_table``, ``top_items`` (the top 20%),
        ``top_items_pct`` (share of total from those items) and ``n_total``.
    """
    logger.info("Running Pareto analysis on %s by %s", value_col, group_col)

    totals = (
        df.groupby(group_col)[value_col]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    totals["Cumulative"] = totals[value_col].cumsum()
    totals["Cumulative %"] = (100 * totals["Cumulative"] / totals[value_col].sum()).round(2)

    n_top = max(1, int(np.ceil(len(totals) * top_pct)))
    top = totals.head(n_top)
    top_share = round(100 * top[value_col].sum() / totals[value_col].sum(), 2)

    logger.info(
        "Top %d of %d %s (%.0f%%) account for %.1f%% of %s",
        n_top,
        len(totals),
        group_col,
        100 * top_pct,
        top_share,
        value_col,
    )

    return {
        "pareto_table": totals,
        "top_items": top,
        "top_items_pct": top_share,
        "n_total": len(totals),
    }


def product_affinity(
    df: pd.DataFrame,
    order_col: str = "Order ID",
    product_col: str = "Product Name",
    min_support: int = 2,
) -> pd.DataFrame:
    """Identify frequently co-purchased product pairs.

    Counts products appearing together within the same order and ranks pairs
    by co-occurrence frequency.

    Args:
        df: Cleaned DataFrame.
        order_col: Column identifying orders.
        product_col: Column identifying products.
        min_support: Minimum co-occurrence count to retain.

    Returns:
        DataFrame of product pairs and their co-occurrence counts, sorted
        descending.
    """
    logger.info("Computing product affinity (co-occurrence)")

    orders = df.groupby(order_col)[product_col].apply(lambda s: s.dropna().unique())

    pair_counts: dict[tuple, int] = {}
    for products in orders:
        if len(products) < 2:
            continue
        for a, b in itertools.combinations(sorted(products), 2):
            pair_counts[(a, b)] = pair_counts.get((a, b), 0) + 1

    if not pair_counts:
        logger.info("No co-purchased product pairs found")
        return pd.DataFrame(
            columns=["Product A", "Product B", "Co-occurrence"]
        )

    affinity = (
        pd.DataFrame(
            [
                {"Product A": a, "Product B": b, "Co-occurrence": c}
                for (a, b), c in pair_counts.items()
                if c >= min_support
            ]
        )
        .sort_values("Co-occurrence", ascending=False)
        .reset_index(drop=True)
    )

    logger.info(
        "Found %d product pairs with co-occurrence >= %d",
        len(affinity),
        min_support,
    )
    return affinity


def discount_impact(df: pd.DataFrame) -> pd.DataFrame:
    """Analyse discount impact by category and sub-category.

    Args:
        df: Cleaned DataFrame with Discount Band, Sales, Profit.

    Returns:
        DataFrame grouped by Discount Band with Sales, Profit, Margin and
        Order Count.
    """
    logger.info("Analysing discount impact")

    if "Discount Band" not in df.columns:
        logger.warning("Discount Band column missing; computing on the fly")
        df = df.copy()
        bins = [-0.001, 0.0, 0.2, 0.4, 0.6, 1.01]
        labels = ["None", "Low", "Medium", "High", "Very High"]
        df["Discount Band"] = pd.cut(
            df["Discount"], bins=bins, labels=labels, include_lowest=True
        ).astype(str)

    impact = (
        df.groupby("Discount Band")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            **{"Avg Discount": ("Discount", "mean")},
        )
        .reset_index()
    )
    impact["Margin %"] = (100 * impact["Profit"] / impact["Sales"]).round(2)
    impact["Avg Discount %"] = (100 * impact["Avg Discount"]).round(2)

    logger.info("Discount impact computed across %d bands", len(impact))
    return impact


def profitability_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Quadrant analysis of sub-categories by Sales and Profit.

    Splits sub-categories into four quadrants using the median Sales and
    Profit as thresholds:
        * Stars (high sales, high profit)
        * Cash Cows (low sales, high profit)
        * Question Marks (high sales, low profit)
        * Dogs (low sales, low profit)

    Args:
        df: Cleaned DataFrame with Sub-Category, Sales, Profit.

    Returns:
        DataFrame with Sales, Profit and Quadrant label per sub-category.
    """
    logger.info("Building profitability matrix")

    matrix = (
        df.groupby("Sub-Category")
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
        .reset_index()
    )

    sales_med = matrix["Sales"].median()
    profit_med = matrix["Profit"].median()

    def _quadrant(row: pd.Series) -> str:
        high_sales = row["Sales"] >= sales_med
        high_profit = row["Profit"] >= profit_med
        if high_sales and high_profit:
            return "Stars"
        if not high_sales and high_profit:
            return "Cash Cows"
        if high_sales and not high_profit:
            return "Question Marks"
        return "Dogs"

    matrix["Quadrant"] = matrix.apply(_quadrant, axis=1)
    logger.info("Profitability matrix quadrants: %s", matrix["Quadrant"].value_counts().to_dict())
    return matrix


def return_analysis_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """Proxy for product returns using negative-profit orders.

    In the absence of an explicit returns flag, we treat any row with
    negative profit as a potential return / loss-making transaction.

    Args:
        df: Cleaned DataFrame with Product Name, Sales, Profit, Order ID.

    Returns:
        DataFrame with loss counts and loss rates per product.
    """
    logger.info("Running return analysis proxy (negative profit orders)")

    loss = (
        df.groupby("Product Name")
        .agg(
            Total_Orders=("Order ID", "nunique"),
            Loss_Orders=("Profit", lambda s: int((s < 0).sum())),
            Total_Sales=("Sales", "sum"),
            Total_Profit=("Profit", "sum"),
        )
        .reset_index()
    )
    loss["Loss Rate %"] = (
        100 * loss["Loss_Orders"] / loss["Total_Orders"].replace(0, np.nan)
    ).round(2)
    loss = loss.sort_values("Loss_Orders", ascending=False).reset_index(drop=True)

    logger.info(
        "Products with loss-making orders: %d / %d",
        int((loss["Loss_Orders"] > 0).sum()),
        len(loss),
    )
    return loss


def run_product_analytics(df: pd.DataFrame) -> dict:
    """Run the full product analytics pipeline.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Dictionary with keys ``category``, ``subcategory``, ``pareto``,
        ``affinity``, ``discount_impact``, ``profitability_matrix`` and
        ``return_proxy``.
    """
    logger.info("Starting full product analytics pipeline")

    result = {
        "category": category_performance(df),
        "subcategory": subcategory_deep_dive(df),
        "pareto": pareto_analysis(df),
        "affinity": product_affinity(df),
        "discount_impact": discount_impact(df),
        "profitability_matrix": profitability_matrix(df),
        "return_proxy": return_analysis_proxy(df),
    }

    logger.info("Product analytics pipeline complete")
    return result
