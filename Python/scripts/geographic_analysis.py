"""Geographic analysis: sales and profit by location dimensions.

Analyses the Superstore data across Country, State, City, Market, Region and
Postal Code dimensions.
"""

from __future__ import annotations

import pandas as pd

from config import get_logger

logger = get_logger(__name__)


def sales_by_country(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Aggregate sales and profit by country.

    Args:
        df: Cleaned DataFrame with Country, Sales, Profit, Order ID.
        top_n: Number of top countries to return.

    Returns:
        DataFrame with Sales, Profit, Margin, Orders per country.
    """
    logger.info("Computing sales by country")

    country = (
        df.groupby("Country")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    country["Margin %"] = (100 * country["Profit"] / country["Sales"]).round(2)
    country["Avg Order Value"] = (country["Sales"] / country["Orders"]).round(2)
    country = country.sort_values("Sales", ascending=False).head(top_n).reset_index(drop=True)

    logger.info("Sales by country computed for top %d countries", len(country))
    return country


def sales_by_state(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Aggregate sales and profit by state.

    Args:
        df: Cleaned DataFrame with State, Sales, Profit, Order ID.
        top_n: Number of top states to return.

    Returns:
        DataFrame with Sales, Profit, Margin, Orders per state.
    """
    logger.info("Computing sales by state")

    state = (
        df.groupby("State")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    state["Margin %"] = (100 * state["Profit"] / state["Sales"]).round(2)
    state = state.sort_values("Sales", ascending=False).head(top_n).reset_index(drop=True)

    logger.info("Sales by state computed for top %d states", len(state))
    return state


def sales_by_city(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Aggregate sales and profit by city.

    Args:
        df: Cleaned DataFrame with City, Sales, Profit, Order ID.
        top_n: Number of top cities to return.

    Returns:
        DataFrame with Sales, Profit, Margin, Orders per city.
    """
    logger.info("Computing sales by city")

    city = (
        df.groupby("City")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    city["Margin %"] = (100 * city["Profit"] / city["Sales"]).round(2)
    city = city.sort_values("Sales", ascending=False).head(top_n).reset_index(drop=True)

    logger.info("Sales by city computed for top %d cities", len(city))
    return city


def market_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales and profit by market.

    Args:
        df: Cleaned DataFrame with Market, Sales, Profit, Order ID.

    Returns:
        DataFrame with Sales, Profit, Margin, Orders per market.
    """
    logger.info("Computing market performance")

    market = (
        df.groupby("Market")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    market["Margin %"] = (100 * market["Profit"] / market["Sales"]).round(2)
    market["Avg Order Value"] = (market["Sales"] / market["Orders"]).round(2)
    market = market.sort_values("Sales", ascending=False).reset_index(drop=True)

    logger.info("Market performance computed for %d markets", len(market))
    return market


def regional_comparison(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales and profit by region.

    Args:
        df: Cleaned DataFrame with Region, Sales, Profit, Order ID.

    Returns:
        DataFrame with Sales, Profit, Margin, Orders per region.
    """
    logger.info("Computing regional comparison")

    region = (
        df.groupby("Region")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
            Customers=("Customer ID", "nunique"),
        )
        .reset_index()
    )
    region["Margin %"] = (100 * region["Profit"] / region["Sales"]).round(2)
    region["Sales Share %"] = (100 * region["Sales"] / region["Sales"].sum()).round(2)
    region = region.sort_values("Sales", ascending=False).reset_index(drop=True)

    logger.info("Regional comparison computed for %d regions", len(region))
    return region


def postal_code_analysis(df: pd.DataFrame, top_n: int = 20) -> pd.DataFrame:
    """Aggregate sales and profit by postal code (after imputation).

    Args:
        df: Cleaned DataFrame with Postal Code, Sales, Profit, Order ID.
        top_n: Number of top postal codes to return.

    Returns:
        DataFrame with Sales, Profit, Orders per postal code.
    """
    logger.info("Computing postal code analysis")

    if "Postal Code" not in df.columns:
        logger.warning("Postal Code column not found; returning empty frame")
        return pd.DataFrame(columns=["Postal Code", "Sales", "Profit", "Orders"])

    postal = (
        df.groupby("Postal Code")
        .agg(
            Sales=("Sales", "sum"),
            Profit=("Profit", "sum"),
            Orders=("Order ID", "nunique"),
        )
        .reset_index()
    )
    postal["Margin %"] = (100 * postal["Profit"] / postal["Sales"]).round(2)
    postal = postal.sort_values("Sales", ascending=False).head(top_n).reset_index(drop=True)

    logger.info("Postal code analysis computed for top %d codes", len(postal))
    return postal


def geographic_distribution_summary(df: pd.DataFrame) -> dict:
    """Produce a high-level geographic distribution summary.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Dictionary with counts of unique locations and top performers.
    """
    logger.info("Building geographic distribution summary")

    summary = {
        "total_countries": int(df["Country"].nunique()) if "Country" in df.columns else 0,
        "total_states": int(df["State"].nunique()) if "State" in df.columns else 0,
        "total_cities": int(df["City"].nunique()) if "City" in df.columns else 0,
        "total_postal_codes": int(df["Postal Code"].nunique()) if "Postal Code" in df.columns else 0,
        "total_regions": int(df["Region"].nunique()) if "Region" in df.columns else 0,
        "total_markets": int(df["Market"].nunique()) if "Market" in df.columns else 0,
    }

    if "Country" in df.columns:
        top_country = (
            df.groupby("Country")["Sales"].sum().idxmax()
        )
        summary["top_country_by_sales"] = str(top_country)

    if "State" in df.columns:
        top_state = df.groupby("State")["Sales"].sum().idxmax()
        summary["top_state_by_sales"] = str(top_state)

    if "City" in df.columns:
        top_city = df.groupby("City")["Sales"].sum().idxmax()
        summary["top_city_by_sales"] = str(top_city)

    logger.info("Geographic distribution summary: %s", summary)
    return summary


def run_geographic_analysis(df: pd.DataFrame) -> dict:
    """Run the full geographic analysis pipeline.

    Args:
        df: Cleaned DataFrame.

    Returns:
        Dictionary with keys ``country``, ``state``, ``city``, ``market``,
        ``region``, ``postal_code`` and ``distribution_summary``.
    """
    logger.info("Starting full geographic analysis pipeline")

    result = {
        "country": sales_by_country(df),
        "state": sales_by_state(df),
        "city": sales_by_city(df),
        "market": market_performance(df),
        "region": regional_comparison(df),
        "postal_code": postal_code_analysis(df),
        "distribution_summary": geographic_distribution_summary(df),
    }

    logger.info("Geographic analysis pipeline complete")
    return result
