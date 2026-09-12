"""Data cleaning, imputation, transformation and feature engineering.

This module turns the raw Superstore frame into a modelling-ready table:
 * removes duplicate rows,
 * imputes missing values (KNN for the heavily-missing ``Postal Code`` column),
 * engineers calendar, shipping and profitability features,
 * offers log transforms for skewed numeric columns.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder

from config import NUMERIC_COLUMNS, get_logger

logger = get_logger(__name__)


def drop_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Drop exact duplicate rows, logging how many were removed."""
    before = len(df)
    out = df.drop_duplicates().reset_index(drop=True)
    logger.info("Removed %d exact duplicate rows", before - len(out))
    return out


def knn_impute_missing(
    df: pd.DataFrame,
    target_cols: list[str],
    feature_cols: list[str],
    n_neighbors: int = 5,
) -> pd.DataFrame:
    """Impute ``target_cols`` using a KNN regressor over ``feature_cols``.

    Categorical ``feature_cols`` are label-encoded on the fly; the encoders are
    not persisted because imputation is applied in place to the provided frame.

    Args:
        df: Input DataFrame (mutated copy returned).
        target_cols: Columns with missing values to fill.
        feature_cols: Columns used as KNN predictors.
        n_neighbors: Number of neighbours.

    Returns:
        DataFrame with imputed values.
    """
    out = df.copy()
    encoders: dict[str, LabelEncoder] = {}
    work = pd.DataFrame(index=out.index)

    for col in feature_cols:
        if col not in out.columns:
            continue
        if out[col].dtype == object or str(out[col].dtype).startswith("string"):
            le = LabelEncoder()
            work[col] = le.fit_transform(out[col].astype(str).fillna("MISSING"))
            encoders[col] = le
        else:
            work[col] = pd.to_numeric(out[col], errors="coerce")

    imputer = KNNImputer(n_neighbors=n_neighbors)
    for col in target_cols:
        if col not in out.columns:
            continue
        if out[col].isna().sum() == 0:
            logger.info("No missing values in %s, skipping KNN", col)
            continue
        feature_matrix = work.copy()
        feature_matrix[col] = pd.to_numeric(out[col], errors="coerce")
        col_idx = list(feature_matrix.columns).index(col)
        filled = imputer.fit_transform(feature_matrix.values)
        imputed_count = int(out[col].isna().sum())
        out[col] = np.round(filled[:, col_idx], 0)
        logger.info("KNN-imputed %d missing values in %s", imputed_count, col)
    return out


def impute_postal_code(df: pd.DataFrame, n_neighbors: int = 5) -> pd.DataFrame:
    """Impute the heavily-missing ``Postal Code`` column via KNN.

    Postal Code is imputed from geographic context (Region/Market/State) and a
    profitability proxy so neighbours in the same area share codes.
    """
    if "Postal Code" not in df.columns:
        return df
    missing = int(df["Postal Code"].isna().sum())
    if missing == 0:
        logger.info("Postal Code has no missing values")
        return df
    logger.info("KNN-imputing %d missing Postal Code values", missing)

    geo_features = [c for c in ["Region", "Market", "State"] if c in df.columns]
    numeric_proxy = [c for c in ["Sales", "Profit"] if c in df.columns]
    out = knn_impute_missing(
        df,
        target_cols=["Postal Code"],
        feature_cols=geo_features + numeric_proxy,
        n_neighbors=n_neighbors,
    )
    return out


def log_transform(
    df: pd.DataFrame, columns: list[str], epsilon: float = 1.0
) -> pd.DataFrame:
    """Add ``log1p``-style columns for skewed numeric features.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to transform.
        epsilon: Constant added before the natural log to avoid log(0).

    Returns:
        DataFrame with new ``<col>_log`` columns appended.
    """
    out = df.copy()
    for col in columns:
        if col not in out.columns:
            continue
        vals = pd.to_numeric(out[col], errors="coerce").clip(lower=0)
        out[f"{col}_log"] = np.log(vals + epsilon)
    logger.info("Added log transforms for: %s", columns)
    return out


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create calendar, shipping and profitability features.

    Adds: Order Year/Month/Quarter/DayOfWeek, Ship Days, Profit Ratio,
    Discount Band, Sales per Unit, Is Weekend and a Period string.
    """
    out = df.copy()
    logger.info("Engineering features")

    date_col = "Order Date"
    if date_col in out.columns:
        out["Order Year"] = out[date_col].dt.year
        out["Order Month"] = out[date_col].dt.month
        out["Order Quarter"] = out[date_col].dt.quarter
        out["Order DayOfWeek"] = out[date_col].dt.dayofweek
        out["Order MonthName"] = out[date_col].dt.strftime("%b")
        out["Is Weekend"] = out["Order DayOfWeek"].isin([5, 6]).astype(int)
        out["Order Period"] = out[date_col].dt.to_period("M").astype(str)

    if {"Ship Date", "Order Date"}.issubset(out.columns):
        out["Shipping Days"] = (out["Ship Date"] - out["Order Date"]).dt.days

    if "Profit" in out.columns and "Sales" in out.columns:
        out["Profit Ratio"] = np.where(
            out["Sales"] != 0, out["Profit"] / out["Sales"], 0.0
        )

    if "Sales" in out.columns and "Quantity" in out.columns:
        out["Sales per Unit"] = np.where(
            out["Quantity"] != 0, out["Sales"] / out["Quantity"], 0.0
        )

    if "Discount" in out.columns:
        bins = [-0.001, 0.0, 0.2, 0.4, 0.6, 1.01]
        labels = ["None", "Low", "Medium", "High", "Very High"]
        out["Discount Band"] = pd.cut(
            out["Discount"], bins=bins, labels=labels, include_lowest=True
        ).astype("string")

    out["Order YearMonth"] = (
        out["Order Year"].astype(str) + "-"
        + out["Order Month"].astype(str).str.zfill(2)
    )
    logger.info("Feature engineering complete; new shape %d x %d", *out.shape)
    return out


def clean_pipeline(
    df: pd.DataFrame,
    impute_postal: bool = True,
    add_log: bool = True,
    log_columns: list[str] | None = None,
) -> pd.DataFrame:
    """Run the full cleaning + transformation pipeline.

    Args:
        df: Raw (already typed) DataFrame.
        impute_postal: Whether to KNN-impute Postal Code.
        add_log: Whether to append log transforms.
        log_columns: Subset of ``NUMERIC_COLUMNS`` to log-transform.

    Returns:
        A modelling-ready DataFrame.
    """
    out = drop_duplicates(df)
    if impute_postal:
        out = impute_postal_code(out)
    if add_log:
        cols = log_columns or [c for c in NUMERIC_COLUMNS if c in out.columns]
        out = log_transform(out, cols)
    out = engineer_features(out)
    return out
