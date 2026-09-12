"""SQL export utilities using SQLAlchemy.

Exports cleaned and derived data to a SQLite database with well-structured
tables for downstream querying.
"""

from __future__ import annotations

import os

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from config import PROJECT_ROOT, get_logger

logger = get_logger(__name__)

SQL_DIR = PROJECT_ROOT / "SQL"
SQL_DIR.mkdir(parents=True, exist_ok=True)


def get_engine(db_name: str = "superstore.db") -> Engine:
    """Create and return a SQLAlchemy engine pointing at the SQL directory.

    Args:
        db_name: Filename for the SQLite database.

    Returns:
        SQLAlchemy Engine instance.
    """
    db_path = SQL_DIR / db_name
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    logger.info("SQLAlchemy engine created at %s", db_path)
    return engine


def _to_sql(
    df: pd.DataFrame,
    table_name: str,
    engine: Engine,
    if_exists: str = "replace",
) -> int:
    """Write a DataFrame to a SQL table.

    Args:
        df: DataFrame to export.
        table_name: Target table name.
        engine: SQLAlchemy engine.
        if_exists: Behaviour when the table already exists.

    Returns:
        Number of rows written.
    """
    df.to_sql(table_name, engine, if_exists=if_exists, index=False)
    logger.info("Exported %d rows to table '%s'", len(df), table_name)
    return len(df)


def build_customers_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build a customers dimension table.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with unique customers and their attributes.
    """
    logger.info("Building customers table")
    agg: dict = {
        "Customer Name": "first",
        "Segment": "first",
        "Country": "first",
        "State": "first",
        "City": "first",
        "Region": "first",
        "Market": "first",
        "Order ID": "nunique",
        "Sales": "sum",
        "Profit": "sum",
    }
    if "Postal Code" in df.columns:
        agg["Postal Code"] = "first"

    customers = df.groupby("Customer ID").agg(agg).reset_index()
    customers = customers.rename(columns={"Order ID": "Order Count"})
    return customers


def build_products_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build a products dimension table.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with unique products and their attributes.
    """
    logger.info("Building products table")
    agg: dict = {
        "Product Name": "first",
        "Category": "first",
        "Sub-Category": "first",
        "Sales": "sum",
        "Profit": "sum",
        "Quantity": "sum",
        "Order ID": "nunique",
    }
    products = df.groupby("Product ID").agg(agg).reset_index()
    products = products.rename(columns={"Order ID": "Order Count"})
    return products


def build_orders_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build an orders dimension table.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with unique orders and their attributes.
    """
    logger.info("Building orders table")
    agg: dict = {
        "Order Date": "first",
        "Ship Date": "first",
        "Ship Mode": "first",
        "Customer ID": "first",
        "Segment": "first",
        "Country": "first",
        "State": "first",
        "City": "first",
        "Region": "first",
        "Market": "first",
        "Order Priority": "first",
        "Sales": "sum",
        "Profit": "sum",
        "Quantity": "sum",
        "Discount": "mean",
    }
    orders = df.groupby("Order ID").agg(agg).reset_index()
    return orders


def build_order_details_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build an order details (line items) table.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with line-item granularity.
    """
    logger.info("Building order details table")
    cols = [
        "Row ID", "Order ID", "Product ID", "Product Name",
        "Category", "Sub-Category", "Sales", "Quantity",
        "Discount", "Profit", "Shipping Cost",
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols].copy()


def build_geography_table(df: pd.DataFrame) -> pd.DataFrame:
    """Build a geography dimension table.

    Args:
        df: Cleaned DataFrame.

    Returns:
        DataFrame with geographic aggregations.
    """
    logger.info("Building geography table")
    agg: dict = {
        "Sales": "sum",
        "Profit": "sum",
        "Order ID": "nunique",
        "Customer ID": "nunique",
    }
    group_cols = [c for c in ["Country", "State", "City", "Region", "Market"] if c in df.columns]
    geo = df.groupby(group_cols).agg(agg).reset_index()
    geo = geo.rename(columns={"Order ID": "Orders", "Customer ID": "Customers"})
    return geo


def export_to_sql(
    df: pd.DataFrame,
    db_name: str = "superstore.db",
) -> dict:
    """Export the cleaned DataFrame and derived tables to SQLite.

    Creates the following tables:
        - cleaned_data: full cleaned dataset
        - customers: customer dimension
        - products: product dimension
        - orders: order dimension
        - order_details: line-item grain
        - geography: geographic aggregation

    Args:
        df: Cleaned DataFrame.
        db_name: SQLite database filename.

    Returns:
        Dictionary mapping table names to row counts.
    """
    logger.info("Starting SQL export to %s", db_name)

    engine = get_engine(db_name)

    tables = {
        "cleaned_data": df,
        "customers": build_customers_table(df),
        "products": build_products_table(df),
        "orders": build_orders_table(df),
        "order_details": build_order_details_table(df),
        "geography": build_geography_table(df),
    }

    counts = {}
    for name, frame in tables.items():
        counts[name] = _to_sql(frame, name, engine)

    logger.info("SQL export complete: %s", counts)
    engine.dispose()
    return counts
