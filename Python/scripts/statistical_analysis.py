"""Statistical analysis and hypothesis testing.

Wraps SciPy/Statsmodels routines to answer business questions: do segments
differ in profit, do categories differ in sales, is discount associated with
lower profit, and so on. Each function returns a structured result dict with
the statistic, p-value and a plain-language conclusion.
"""

from __future__ import annotations

import pandas as pd
from scipy import stats

from config import get_logger

logger = get_logger(__name__)


def _conclusion(p: float, alpha: float = 0.05) -> str:
    return "reject H0 (significant)" if p < alpha else "fail to reject H0 (not significant)"


def ttest_profit_by_segment(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Welch t-test comparing Profit between Consumer and Corporate segments."""
    if not {"Segment", "Profit"}.issubset(df.columns):
        raise KeyError("Segment and Profit required")
    groups = df[df["Segment"].isin(["Consumer", "Corporate"])]
    a = groups.loc[groups["Segment"] == "Consumer", "Profit"]
    b = groups.loc[groups["Segment"] == "Corporate", "Profit"]
    t, p = stats.ttest_ind(a, b, equal_var=False)
    res = {"test": "Welch t-test (Profit: Consumer vs Corporate)", "statistic": t, "p_value": p, "conclusion": _conclusion(p, alpha)}
    logger.info("t-test profit by segment: p=%.4g", p)
    return res


def anova_sales_by_category(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """One-way ANOVA of Sales across Categories."""
    if not {"Category", "Sales"}.issubset(df.columns):
        raise KeyError("Category and Sales required")
    samples = [g["Sales"].values for _, g in df.groupby("Category")]
    f, p = stats.f_oneway(*samples)
    res = {"test": "One-way ANOVA (Sales across Category)", "statistic": f, "p_value": p, "conclusion": _conclusion(p, alpha)}
    logger.info("ANOVA sales by category: p=%.4g", p)
    return res


def chi_square_segment_market(df: pd.DataFrame, alpha: float = 0.05) -> dict:
    """Chi-square test of independence between Segment and Market."""
    if not {"Segment", "Market"}.issubset(df.columns):
        raise KeyError("Segment and Market required")
    ct = pd.crosstab(df["Segment"], df["Market"])
    chi2, p, dof, _ = stats.chi2_contingency(ct)
    res = {"test": "Chi-square (Segment x Market)", "statistic": chi2, "p_value": p, "dof": dof, "conclusion": _conclusion(p, alpha)}
    logger.info("Chi-square segment x market: p=%.4g", p)
    return res


def correlation_significance(df: pd.DataFrame, col_a: str, col_b: str, alpha: float = 0.05) -> dict:
    """Pearson correlation test between two numeric columns."""
    if col_a not in df.columns or col_b not in df.columns:
        raise KeyError(f"{col_a} and {col_b} required")
    r, p = stats.pearsonr(df[col_a].dropna(), df[col_b].dropna())
    res = {"test": f"Pearson r ({col_a} vs {col_b})", "statistic": r, "p_value": p, "conclusion": _conclusion(p, alpha)}
    logger.info("Correlation %s~%s: r=%.3f p=%.4g", col_a, col_b, r, p)
    return res


def mannwhitney_discount_profit(df: pd.DataFrame, threshold: float = 0.2, alpha: float = 0.05) -> dict:
    """Non-parametric test of Profit distribution for high vs low discount."""
    if not {"Discount", "Profit"}.issubset(df.columns):
        raise KeyError("Discount and Profit required")
    low = df.loc[df["Discount"] <= threshold, "Profit"]
    high = df.loc[df["Discount"] > threshold, "Profit"]
    u, p = stats.mannwhitneyu(low, high, alternative="two-sided")
    res = {"test": f"Mann-Whitney U (Profit: Discount<={threshold} vs >)", "statistic": u, "p_value": p, "conclusion": _conclusion(p, alpha)}
    logger.info("Mann-Whitney discount vs profit: p=%.4g", p)
    return res


def regression_profit_on_discount(df: pd.DataFrame):
    """OLS regression of Profit on Discount (with Sales control)."""
    from statsmodels.formula.api import ols

    if not {"Profit", "Discount", "Sales"}.issubset(df.columns):
        raise KeyError("Profit, Discount, Sales required")
    sub = df[["Profit", "Discount", "Sales"]].dropna()
    model = ols("Profit ~ Discount + Sales", data=sub).fit()
    logger.info("OLS R2=%.3f", model.rsquared)
    return model


def run_full_battery(df: pd.DataFrame) -> pd.DataFrame:
    """Run every available test and return a summary table."""
    results: list[dict] = []
    for fn in (
        ttest_profit_by_segment,
        anova_sales_by_category,
        chi_square_segment_market,
        correlation_significance,
        mannwhitney_discount_profit,
    ):
        try:
            if fn is correlation_significance:
                results.append(fn(df, "Discount", "Profit"))
            else:
                results.append(fn(df))
        except Exception as exc:  # noqa: BLE001 - keep pipeline robust
            logger.warning("Test %s skipped: %s", getattr(fn, "__name__", fn), exc)
    return pd.DataFrame(results)
