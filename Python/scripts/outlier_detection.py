"""Outlier detection helpers (Z-score and IQR methods)."""

from __future__ import annotations

import numpy as np
import pandas as pd

from config import IQR_MULTIPLIER, ZSCORE_THRESHOLD, get_logger

logger = get_logger(__name__)


def zscore_outliers(
    df: pd.DataFrame, columns: list[str], threshold: float = ZSCORE_THRESHOLD
) -> dict:
    """Flag outliers using the standard (Z) score per column.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to evaluate.
        threshold: Absolute Z-score above which a value is an outlier.

    Returns:
        Mapping of column -> boolean mask (True == outlier).
    """
    logger.info("Running Z-score outlier detection (threshold=%.1f)", threshold)
    masks: dict[str, pd.Series] = {}
    for col in columns:
        if col not in df.columns:
            continue
        values = df[col].astype(float)
        std = values.std(ddof=0)
        if std == 0 or pd.isna(std):
            masks[col] = pd.Series(False, index=df.index)
            continue
        z = (values - values.mean()).abs() / std
        masks[col] = z > threshold
    return masks


def iqr_outliers(
    df: pd.DataFrame, columns: list[str], multiplier: float = IQR_MULTIPLIER
) -> dict:
    """Flag outliers using the inter-quartile range (Tukey) rule.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to evaluate.
        multiplier: IQR fence multiplier (1.5 == standard fences).

    Returns:
        Mapping of column -> boolean mask (True == outlier).
    """
    logger.info("Running IQR outlier detection (multiplier=%.1f)", multiplier)
    masks: dict[str, pd.Series] = {}
    for col in columns:
        if col not in df.columns:
            continue
        values = df[col].astype(float)
        q1, q3 = values.quantile(0.25), values.quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - multiplier * iqr, q3 + multiplier * iqr
        masks[col] = (values < lower) | (values > upper)
    return masks


def combined_outlier_mask(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "either",
    z_threshold: float = ZSCORE_THRESHOLD,
    iqr_multiplier: float = IQR_MULTIPLIER,
) -> pd.Series:
    """Combine Z-score and IQR masks into a single row-level boolean mask.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to evaluate.
        method: ``"either"`` (union) or ``"both"`` (intersection).
        z_threshold: Z-score threshold.
        iqr_multiplier: IQR fence multiplier.

    Returns:
        Boolean Series (True == row flagged as outlier on any/required column).
    """
    z_masks = zscore_outliers(df, columns, z_threshold)
    iqr_masks = iqr_outliers(df, columns, iqr_multiplier)

    union = pd.Series(False, index=df.index)
    inter = pd.Series(True, index=df.index)
    for col in columns:
        if col not in z_masks:
            continue
        z = z_masks[col]
        i = iqr_masks[col]
        union = union | (z | i)
        inter = inter & (z & i)

    result = union if method == "either" else inter
    logger.info("Combined outliers (%s): %d rows flagged", method, int(result.sum()))
    return result


def winsorize_columns(
    df: pd.DataFrame, columns: list[str], limits: tuple[float, float] = (0.01, 0.01)
) -> pd.DataFrame:
    """Return a copy of ``df`` with specified columns winsorized.

    Args:
        df: Input DataFrame.
        columns: Numeric columns to winsorize.
        limits: (lower, upper) quantile clipping fractions.

    Returns:
        A new DataFrame with clipped values.
    """
    from scipy.stats import mstats

    out = df.copy()
    for col in columns:
        if col not in out.columns:
            continue
        out[col] = mstats.winsorize(out[col].astype(float), limits=limits)
    logger.info("Winsorized columns: %s", columns)
    return out
