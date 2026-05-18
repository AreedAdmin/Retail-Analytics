"""
Data access layer: Load and normalize raw dataset.

This module handles loading `data/data_raw.csv` and normalizing it
to match the integration contracts defined in schemas.py.

Key responsibilities:
- Load CSV with error handling
- Normalize column names to snake_case
- Cache processed data
- Provide SKU-level and period-level queries
"""

import os
import pandas as pd
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Central data access point for the dashboard.
    
    Loads raw CSV from `data/` and provides normalized data
    matching contract schemas (e.g., sku → sku_id, week → period).
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize data loader.
        
        Args:
            data_dir: Path to data directory. If None, uses PROJECT_ROOT/data/
        """
        if data_dir is None:
            # Infer path from this file's location
            # From: dashboard/analytics/common/data_loader.py
            # To: data/ (go up 3 levels)
            project_root = os.path.abspath(os.path.join(
                os.path.dirname(__file__), '../../..'
            ))
            data_dir = os.path.join(project_root, 'data')
        
        self.data_dir = data_dir
        self.raw_csv = os.path.join(data_dir, 'data_raw.csv')
        self._cache: Optional[pd.DataFrame] = None
    
    def load_raw_data(self, force_reload: bool = False) -> pd.DataFrame:
        """
        Load and cache the raw CSV data.
        
        Args:
            force_reload: If True, bypass cache and reload from disk.
        
        Returns:
            DataFrame with raw CSV data (unchanged column names).
        
        Raises:
            FileNotFoundError: If data_raw.csv not found.
        """
        if self._cache is not None and not force_reload:
            logger.debug("Returning cached raw data")
            return self._cache.copy()
        
        if not os.path.exists(self.raw_csv):
            raise FileNotFoundError(
                f"Raw data file not found: {self.raw_csv}\n"
                f"Expected location: {self.data_dir}/data_raw.csv"
            )
        
        try:
            df = pd.read_csv(self.raw_csv)
            logger.info(f"Loaded raw data: {df.shape[0]} rows, {df.shape[1]} columns")
            self._cache = df
            return df.copy()
        except Exception as e:
            logger.error(f"Error loading {self.raw_csv}: {e}")
            raise
    
    def get_normalized_data(self) -> pd.DataFrame:
        """
        Load and normalize data to contract schema.
        
        Normalization steps:
        - Rename 'sku' → 'sku_id' (for ForecastOutput, etc.)
        - Rename 'week' → 'period' (for ForecastOutput, etc.)
        - Ensure all columns follow snake_case
        - Validate data types
        
        Returns:
            Normalized DataFrame ready for analytics.
        """
        df = self.load_raw_data()
        
        # Column name mappings (raw CSV → normalized)
        rename_map = {
            'sku': 'sku_id',
            'week': 'period',
        }
        
        df_normalized = df.rename(columns=rename_map)

        # week/period column holds ISO dates — map to numeric period index
        if 'period' in df_normalized.columns:
            df_normalized['week_date'] = pd.to_datetime(df_normalized['period'])
            df_normalized = df_normalized.sort_values(['sku_id', 'week_date']).reset_index(drop=True)
            unique_weeks = df_normalized['week_date'].drop_duplicates().sort_values()
            week_to_period = {w: i + 1 for i, w in enumerate(unique_weeks)}
            df_normalized['period'] = df_normalized['week_date'].map(week_to_period).astype(int)

        # Validate expected columns exist
        expected_cols = {
            'period', 'sku_id', 'weekly_sales', 'feat_main_page',
            'color', 'price', 'vendor', 'functionality'
        }
        missing = expected_cols - set(df_normalized.columns)
        if missing:
            raise ValueError(
                f"Missing expected columns: {missing}\n"
                f"Available columns: {set(df_normalized.columns)}"
            )

        if 'weekly_sales' in df_normalized.columns:
            df_normalized = df_normalized.rename(columns={'weekly_sales': 'demand_units'})
        
        logger.info(f"Normalized data: {df_normalized.shape}")
        return df_normalized
    
    def get_sku_list(self) -> List[str]:
        """Get unique SKU IDs."""
        df = self.get_normalized_data()
        return sorted(df['sku_id'].unique().tolist())
    
    def get_period_range(self) -> Dict[str, Any]:
        """Get period information (min, max, count)."""
        df = self.get_normalized_data()
        return {
            'min_period': df['period'].min(),
            'max_period': df['period'].max(),
            'num_periods': df['period'].nunique(),
            'periods': sorted(df['period'].unique().tolist()),
        }
    
    def get_sku_data(self, sku_id: str) -> pd.DataFrame:
        """Get all data for a specific SKU."""
        df = self.get_normalized_data()
        sku_df = df[df['sku_id'] == sku_id].sort_values('period')
        return sku_df
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """
        Get summary statistics for the entire dataset.
        
        Used by Module 1 (Overview) and Module 2 (Data Explorer).
        
        Returns:
            Dict with summary metrics.
        """
        df = self.get_normalized_data()
        
        return {
            'num_skus': df['sku_id'].nunique(),
            'num_periods': df['period'].nunique(),
            'num_records': len(df),
            'total_demand_units': df['demand_units'].sum(),
            'total_revenue': (df['demand_units'] * df['price']).sum(),
            'avg_price': df['price'].mean(),
            'num_promotions': df['feat_main_page'].sum(),
            'price_range': {
                'min': df['price'].min(),
                'max': df['price'].max(),
                'mean': df['price'].mean(),
                'std': df['price'].std(),
            },
            'demand_range': {
                'min': df['demand_units'].min(),
                'max': df['demand_units'].max(),
                'mean': df['demand_units'].mean(),
                'std': df['demand_units'].std(),
            },
        }
    
    def get_sku_stats(self, sku_id: str = None) -> pd.DataFrame:
        """
        Get per-SKU summary statistics.
        
        Used by Module 2 (Data Explorer).
        
        Args:
            sku_id: If provided, return stats for single SKU. If None, return all.
        
        Returns:
            DataFrame with per-SKU statistics.
        """
        df = self.get_normalized_data()
        
        if sku_id is not None:
            df = df[df['sku_id'] == sku_id]
        
        stats = df.groupby('sku_id').agg({
            'demand_units': ['mean', 'std', 'min', 'max'],
            'price': ['mean', 'std', 'min', 'max'],
            'feat_main_page': 'sum',  # count of promotions
        }).round(2)
        
        stats.columns = ['_'.join(col).strip() for col in stats.columns.values]
        return stats


# Singleton instance for dashboard
_data_loader: Optional[DataLoader] = None


def get_data_loader() -> DataLoader:
    """Get or create the singleton DataLoader instance."""
    global _data_loader
    if _data_loader is None:
        _data_loader = DataLoader()
    return _data_loader
