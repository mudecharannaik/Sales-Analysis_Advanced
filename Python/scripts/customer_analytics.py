"""Customer analytics: RFM segmentation, CLV estimation and repeat analysis.

This module provides a full customer-analytics suite built on the cleaned
Superstore frame. It computes Recency/Frequency/Monetary scores, assigns
segment labels, estimates historical CLV and ranks customers by value.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import get_logger

logger = get_logger(__name__)


def compute_rfm(
    df: pd.DataFrame,
    reference_date: pd.Timestamp | None = None,
) -> pd.DataFrame:
    """Compute Recency, Frequency and Monetary values per customer.

    Args:
        df: Cleaned DataFrame with Customer ID, Order Date, Sales.
        reference_date: Date against which recency is measured. Defaults to
            ``max(Order Date) + 1 day``.

    Returns:
        DataFrame indexed by Customer ID with columns ``Recency``,
        ``Frequency`` and ``Monetary``.
    """
    required = {"Customer ID", "Order Date", "Sales"}
    if not required.issubset(df.columns):
        raise KeyError(f"Missing required columns: {required - set(df.columns)}")

    if reference_date is None:
        reference_date = df["Order Date"].max() + pd.Timedelta(days=1)

    logger.info("Computing RFM with reference date %s", reference_date.date())

    rfm = (
        df.groupby("Customer ID")
        .agg(
            Recency=("Order Date", lambda s: (reference_date - s.max()).days),
            Frequency=("Order ID", "nunique"),
            Monetary=("Sales", "sum"),
        )
    )

    logger.info("RFM computed for %d customers", len(rfm))
    return rfm


def score_rfm(rfm: pd.DataFrame, n_bins: int = 5) -> pd.DataFrame:
    """Assign quintile scores (1-5) for each R/F/M dimension.

    For Recency a lower value is better, so scoring is reversed: the most
    recent customers receive a 5. Frequency and Monetary use the natural
    order (higher is better).

    Args:
        rfm: Output of :func:`compute_rfm`.
        n_bins: Number of quantile bins (default 5).

    Returns:
        Input frame augmented with ``R_Score``, ``F_Score``, ``M_Score`` and
        a combined ``RFM_Score`` string.
    """
    logger.info("Scoring RFM into %d quintiles", n_bins)
    out = rfm.copy()

    out["R_Score"] = pd.qcut(
        out["Recency"], q=n_bins, labels=list(range(n_bins, 0, -1))
    ).astype("Int64").fillna(1).astype(int)
    out["F_Score"] = pd.qcut(
        out["Frequency"].rank(method="first"), q=n_bins, labels=list(range(1, n_bins + 1))
    ).astype("Int64").fillna(1).astype(int)
    out["M_Score"] = pd.qcut(
        out["Monetary"].rank(method="first"), q=n_bins, labels=list(range(1, n_bins + 1))
    ).astype("Int64").fillna(1).astype(int)

    out["RFM_Score"] = (
        out["R_Score"].astype(str)
        + out["F_Score"].astype(str)
        + out["M_Score"].astype(str)
    )
    return out


def assign_segment_labels(rfm_scored: pd.DataFrame) -> pd.DataFrame:
    """Map RFM scores to human-readable segment labels.

    Rules (applied in priority order):
        * Champions: R >= 4 and F >= 4
        * Loyal: F >= 4
        * Potential Loyalist: R >= 3 and F in (2, 3)
        * Recent: R >= 4 and F <= 2
        * Promising: R in (2, 3) and F <= 2
        * At Risk: R <= 2 and F >= 3
        * Hibernating: R <= 2 and F <= 2 and M >= 3
        * Lost: R <= 2 and F <= 2 and M < 3

    Args:
        rfm_scored: Output of :func:`score_rfm`.

    Returns:
        Input frame with a ``Segment`` column appended.
    """
    logger.info("Assigning customer segment labels")

    def _label(row: pd.Series) -> str:
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r >= 4 and f >= 4:
            return "Champions"
        if f >= 4:
            return "Loyal"
        if r >= 3 and f in (2, 3):
            return "Potential Loyalist"
        if r >= 4 and f <= 2:
            return "Recent Customer"
        if r in (2, 3) and f <= 2:
            return "Promising"
        if r <= 2 and f >= 3:
            return "At Risk"
        if r <= 2 and f <= 2 and m >= 3:
            return "Hibernating"
        return "Lost"

    out = rfm_scored.copy()
    out["Segment"] = out.apply(_label, axis=1)
    counts = out["Segment"].value_counts().to_dict()
    logger.info("Segment distribution: %s", counts)
    return out


def estimate_clv(
    df: pd.DataFrame,
    avg_lifespan_years: float = 2.0,
) -> pd.DataFrame:
    """Estimate historical Customer Lifetime Value.

    Uses the simple formulation::

        CLV = avg monthly sales * 12 * avg_lifespan_years

    Args:
        df: Cleaned DataFrame with Customer ID, Order Date, Sales.
        avg_lifespan_years: Assumed average customer lifespan in years.

    Returns:
        DataFrame with Customer ID, ``Avg Monthly Sales``, ``Annual Sales``
        and ``Estimated_CLV``.
    """
    logger.info("Estimating CLV with assumed lifespan %.1f years", avg_lifespan_years)

    df = df.copy()
    df["Order Period"] = df["Order Date"].dt.to_period("M")

    monthly = (
        df.groupby(["Customer ID", "Order Period"])["Sales"]
        .sum()
        .reset_index()
    )

    avg_monthly = (
        monthly.groupby("Customer ID")["Sales"]
        .mean()
        .reset_index(name="Avg Monthly Sales")
    )

    avg_monthly["Annual Sales"] = avg_monthly["Avg Monthly Sales"] * 12
    avg_monthly["Estimated_CLV"] = avg_monthly["Annual Sales"] * avg_lifespan_years

    logger.info("CLV estimated for %d customers", len(avg_monthly))
    return avg_monthly


def repeat_customer_analysis(df: pd.DataFrame) -> dict:
    """Analyse repeat vs one-time customers.

    Args:
        df: Cleaned DataFrame with Customer ID and Order ID.

    Returns:
        Dictionary with counts, revenue share and a per-customer order summary.
    """
    logger.info("Running repeat customer analysis")
    order_counts = df.groupby("Customer ID")["Order ID"].nunique()

    repeat_mask = order_counts > 1
    n_repeat = int(repeat_mask.sum())
    n_one_time = int((~repeat_mask).sum())

    customer_orders = (
        order_counts.value_counts().sort_index().to_dict()
    )

    repeat_revenue = df.loc[
        df["Customer ID"].isin(order_counts[repeat_mask].index), "Sales"
    ].sum()
    total_revenue = df["Sales"].sum()
    repeat_share = round(100 * repeat_revenue / total_revenue, 2) if total_revenue else 0.0

    result = {
        "total_customers": int(len(order_counts)),
        "repeat_customers": n_repeat,
        "one_time_customers": n_one_time,
        "repeat_rate_pct": round(100 * n_repeat / len(order_counts), 2) if len(order_counts) else 0.0,
        "repeat_revenue_share_pct": repeat_share,
        "orders_per_customer_dist": customer_orders,
    }
    logger.info(
        "Repeat customers: %d / %d (%.1f%%) contributing %.1f%% of revenue",
        n_repeat,
        len(order_counts),
        result["repeat_rate_pct"],
        repeat_share,
    )
    return result


def top_customers(
    df: pd.DataFrame,
    by: str = "Sales",
    top_n: int = 20,
) -> pd.DataFrame:
    """Return the top-N customers ranked by a chosen metric.

    Args:
        df: Cleaned DataFrame.
        by: Column to rank on (``Sales`` or ``Profit``).
        top_n: Number of customers to return.

    Returns:
        DataFrame with Customer ID, Customer Name, total Sales, total Profit,
        Order Count and Avg Order Value.
    """
    if by not in {"Sales", "Profit"}:
        raise ValueError("by must be 'Sales' or 'Profit'")

    logger.info("Computing top %d customers by %s", top_n, by)

    agg: dict = {
        "Sales": "sum",
        "Profit": "sum",
        "Order ID": "nunique",
    }
    if "Customer Name" in df.columns:
        agg["Customer Name"] = "first"

    summary = df.groupby("Customer ID").agg(agg).reset_index()
    summary["Avg Order Value"] = np.where(
        summary["Order ID"] > 0, summary["Sales"] / summary["Order ID"], 0.0
    )
    summary = summary.sort_values(by, ascending=False).head(top_n).reset_index(drop=True)
    return summary


def customer_lifetime_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Build a per-customer lifetime summary table.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with first/last order dates, tenure days, total orders,
        total sales, total profit, avg discount and preferred segment.
    """
    logger.info("Building customer lifetime summary")

    agg: dict = {
        "Order Date": ["min", "max"],
        "Order ID": "nunique",
        "Sales": "sum",
        "Profit": "sum",
        "Discount": "mean",
    }
    if "Segment" in df.columns:
        agg["Segment"] = lambda s: s.mode().iloc[0] if not s.mode().empty else "Unknown"

    summary = df.groupby("Customer ID").agg(agg)
    summary.columns = [
        "First Order", "Last Order", "Total Orders",
        "Total Sales", "Total Profit", "Avg Discount", "Preferred Segment",
    ]
    summary = summary.reset_index()
    summary["Tenure Days"] = (summary["Last Order"] - summary["First Order"]).dt.days

    logger.info("Customer lifetime summary built for %d customers", len(summary))
    return summary


def run_customer_analytics(df: pd.DataFrame) -> dict:
    """Run the full customer analytics pipeline.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Dictionary with keys ``rfm``, ``clv``, ``repeat``, ``top_sales``,
        ``top_profit`` and ``lifetime_summary``.
    """
    logger.info("Starting full customer analytics pipeline")

    rfm = compute_rfm(df)
    rfm_scored = score_rfm(rfm)
    rfm_labeled = assign_segment_labels(rfm_scored)

    clv = estimate_clv(df)
    repeat = repeat_customer_analysis(df)
    top_sales = top_customers(df, by="Sales", top_n=20)
    top_profit = top_customers(df, by="Profit", top_n=20)
    lifetime = customer_lifetime_summary(df)

    logger.info("Customer analytics pipeline complete")
    return {
        "rfm": rfm_labeled,
        "clv": clv,
        "repeat": repeat,
        "top_sales": top_sales,
        "top_profit": top_profit,
        "lifetime_summary": lifetime,
    }
