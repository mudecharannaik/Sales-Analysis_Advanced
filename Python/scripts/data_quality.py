"""Data quality assessment utilities.

Produces a comprehensive profile of the dataset (schema, missingness, duplicate
checks, cardinality, numeric summary and basic sanity rules). These functions
are pure analysis helpers and do not mutate the input frame.
"""

from __future__ import annotations

import pandas as pd

from config import get_logger

logger = get_logger(__name__)


def profile_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Build a tabular profile of every column.

    Args:
        df: DataFrame to profile.

    Returns:
        A DataFrame indexed by column name with dtype, non-null counts,
        missing counts/percentages, cardinality and (for numerics) min/max.
    """
    logger.info("Profiling dataframe with %d rows and %d columns", *df.shape)
    rows = []
    for col in df.columns:
        series = df[col]
        n_missing = int(series.isna().sum())
        record = {
            "column": col,
            "dtype": str(series.dtype),
            "non_null": int(series.notna().sum()),
            "missing": n_missing,
            "missing_pct": round(100 * n_missing / len(series), 2),
            "nunique": int(series.nunique(dropna=True)),
        }
        if pd.api.types.is_numeric_dtype(series):
            record["min"] = series.min()
            record["max"] = series.max()
            record["mean"] = round(float(series.mean()), 4)
        else:
            record["min"] = pd.NA
            record["max"] = pd.NA
            record["mean"] = pd.NA
        rows.append(record)

    profile = pd.DataFrame(rows).set_index("column")
    logger.info("Profiling complete")
    return profile


def missing_value_report(df: pd.DataFrame) -> pd.DataFrame:
    """Return columns with missing values sorted by severity."""
    miss = df.isna().sum()
    miss = miss[miss > 0].sort_values(ascending=False)
    report = pd.DataFrame(
        {
            "missing": miss.values,
            "missing_pct": (100 * miss.values / len(df)).round(2),
        },
        index=miss.index,
    )
    logger.info("Found %d columns with missing values", len(report))
    return report


def duplicate_report(df: pd.DataFrame, subset: list[str] | None = None) -> dict:
    """Summarise exact and key-based duplicate rows.

    Args:
        df: DataFrame to inspect.
        subset: Optional column subset used to define a "logical" duplicate
            (defaults to the order/customer/product identifiers).

    Returns:
        A dictionary with ``exact_duplicates`` and ``key_duplicates`` counts.
    """
    exact = int(df.duplicated().sum())
    if subset is None:
        subset = [c for c in ["Order ID", "Product ID", "Customer ID"] if c in df.columns]
    key_dups = int(df.duplicated(subset=subset).sum()) if subset else 0
    logger.info("Exact duplicates: %d | Key duplicates: %d", exact, key_dups)
    return {"exact_duplicates": exact, "key_duplicates": key_dups}


def integrity_checks(df: pd.DataFrame) -> pd.DataFrame:
    """Run a battery of rule-based integrity checks.

    Returns:
        A DataFrame of ``(check, result, detail)`` rows describing each test
        and whether it passed.
    """
    checks: list[dict] = []

    def add(check: str, passed: bool, detail: str) -> None:
        checks.append({"check": check, "passed": passed, "detail": detail})

    # Negative or zero sales?
    if "Sales" in df.columns:
        bad_sales = int((df["Sales"] <= 0).sum())
        add("Sales > 0", bad_sales == 0, f"{bad_sales} rows with Sales <= 0")

    # Profit can be negative by design; only flag nulls.
    if "Profit" in df.columns:
        null_profit = int(df["Profit"].isna().sum())
        add("Profit not null", null_profit == 0, f"{null_profit} null Profit values")

    # Discount bounds.
    if "Discount" in df.columns:
        bad_disc = int(((df["Discount"] < 0) | (df["Discount"] > 1)).sum())
        add("Discount in [0,1]", bad_disc == 0, f"{bad_disc} out-of-range discounts")

    # Ship date after order date.
    if {"Order Date", "Ship Date"}.issubset(df.columns):
        invalid = int((df["Ship Date"] < df["Order Date"]).sum())
        add("Ship Date >= Order Date", invalid == 0, f"{invalid} invalid date pairs")

    # Quantity positive.
    if "Quantity" in df.columns:
        bad_qty = int((df["Quantity"] <= 0).sum())
        add("Quantity > 0", bad_qty == 0, f"{bad_qty} rows with Quantity <= 0")

    report = pd.DataFrame(checks)
    logger.info("Integrity checks complete: %d evaluated", len(report))
    return report


def generate_quality_summary(
    df: pd.DataFrame, subset: list[str] | None = None
) -> dict:
    """Convenience wrapper returning every quality artefact at once."""
    return {
        "profile": profile_dataframe(df),
        "missing": missing_value_report(df),
        "duplicates": duplicate_report(df, subset),
        "integrity": integrity_checks(df),
    }
