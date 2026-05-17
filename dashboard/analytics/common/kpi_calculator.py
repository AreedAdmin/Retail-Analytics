"""
KPI calculator - Compute all dashboard KPIs from normalized data.

This module calculates key performance indicators used across all dashboard modules.
"""

import pandas as pd
from typing import Dict, Any
from dashboard.analytics.common.kpi_definitions import KPIRegistry, KPIThresholds


def calculate_all_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all KPIs from the normalized dataset.
    
    Args:
        df: Normalized DataFrame with columns: sku_id, period, demand_units, price, feat_main_page, etc.
    
    Returns:
        Dict with all KPI values ready for display.
    """
    if df.empty:
        return _get_empty_kpis()
    
    # Basic metrics
    total_revenue = (df['demand_units'] * df['price']).sum()
    total_demand_units = df['demand_units'].sum()
    num_skus = df['sku_id'].nunique()
    num_periods = df['period'].nunique()
    avg_price = df['price'].mean()
    num_promotions = df['feat_main_page'].sum()
    
    return {
        # Overview KPIs (Module 1)
        KPIRegistry.TOTAL_REVENUE: round(total_revenue, 2),
        KPIRegistry.TOTAL_DEMAND_UNITS: int(total_demand_units),
        KPIRegistry.NUM_SKUS: int(num_skus),
        KPIRegistry.NUM_PERIODS: int(num_periods),
        KPIRegistry.AVG_PRICE: round(avg_price, 2),
        KPIRegistry.NUM_PROMOTIONS: int(num_promotions),
        
        # Additional stats for context
        'price_min': round(df['price'].min(), 2),
        'price_max': round(df['price'].max(), 2),
        'price_std': round(df['price'].std(), 2),
        'demand_min': int(df['demand_units'].min()),
        'demand_max': int(df['demand_units'].max()),
        'demand_mean': round(df['demand_units'].mean(), 2),
        'demand_std': round(df['demand_units'].std(), 2),
    }


def _get_empty_kpis() -> Dict[str, Any]:
    """Return empty KPI dict when data is unavailable."""
    return {
        KPIRegistry.TOTAL_REVENUE: 0,
        KPIRegistry.TOTAL_DEMAND_UNITS: 0,
        KPIRegistry.NUM_SKUS: 0,
        KPIRegistry.NUM_PERIODS: 0,
        KPIRegistry.AVG_PRICE: 0,
        KPIRegistry.NUM_PROMOTIONS: 0,
        'price_min': 0,
        'price_max': 0,
        'price_std': 0,
        'demand_min': 0,
        'demand_max': 0,
        'demand_mean': 0,
        'demand_std': 0,
    }


def get_sku_summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Get per-SKU summary statistics for Module 2 (Data Explorer).
    
    Args:
        df: Normalized DataFrame
    
    Returns:
        DataFrame with per-SKU stats
    """
    if df.empty:
        return pd.DataFrame()
    
    stats = df.groupby('sku_id').agg({
        'demand_units': ['count', 'mean', 'min', 'max', 'std'],
        'price': ['mean', 'min', 'max'],
        'feat_main_page': 'sum',  # count of promotions
    }).round(2)
    
    stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
    stats = stats.rename(columns={
        'demand_units_count': 'periods',
        'demand_units_mean': 'avg_demand',
        'demand_units_min': 'min_demand',
        'demand_units_max': 'max_demand',
        'demand_units_std': 'std_demand',
        'price_mean': 'avg_price',
        'price_min': 'min_price',
        'price_max': 'max_price',
        'feat_main_page_sum': 'num_promotions',
    })
    
    return stats.reset_index()


def format_kpi_for_display(value: Any, unit: str = "") -> str:
    """
    Format KPI value for display in UI.
    
    Args:
        value: KPI value
        unit: Unit to append (e.g., "$", "%", "units")
    
    Returns:
        Formatted string
    """
    if isinstance(value, float):
        formatted = f"{value:,.2f}"
    elif isinstance(value, int):
        formatted = f"{value:,}"
    else:
        formatted = str(value)
    
    return f"{formatted} {unit}".strip()
